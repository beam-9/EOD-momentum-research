"""Fixed-rule, independent ETF IBS research. No CFD or live execution claims."""
from __future__ import annotations

import json

from datetime import date, timedelta
from hashlib import sha256
from pathlib import Path

import numpy as np
import polars as pl

from .calendar import expected_minutes, latest_completed, sessions
from .common import ROOT, code_hashes, digest, dump, environment, external_hashes, sha, stamp, utcnow
from .data import audit
from .features import available
from .ibs import atr_size, ibs, prior_atr
from .statistics import block_bootstrap
from .walk_forward import folds, in_interval

THRESHOLDS = {'SPY': 0.20, 'QQQ': 0.10}


def asof_check(bars, day, *, decision_lag_minutes=0, max_mark_age_seconds=60):
    """Return only observations actually available by the fixed daily check."""
    cutoff = stamp(day, '15:55')
    decision = cutoff + timedelta(minutes=decision_lag_minutes)
    rows = [r for r in bars.to_dicts() if r['bar_end_utc'] <= cutoff and available(r) <= decision]
    if not rows:
        raise ValueError('IBS_NO_AVAILABLE_PREFIX')
    rows.sort(key=lambda r: r['timestamp_utc'])
    age = (decision - rows[-1]['bar_end_utc']).total_seconds()
    if age > max_mark_age_seconds:
        raise ValueError('IBS_STALE_PREFIX')
    # Missing late receipts are excluded from BOTH last price and prefix range.
    high, low = max(r['high'] for r in rows), min(r['low'] for r in rows)
    return {'decision_at': decision, 'economic_cutoff': cutoff, 'mark_age_seconds': age,
            'max_mark_age_seconds': max_mark_age_seconds, 'feature_available_at': max(available(r) for r in rows),
            'last_bar_start': rows[-1]['timestamp_utc'], 'ibs': ibs(rows[-1]['close'], high, low),
            'high_so_far': high, 'low_so_far': low, 'last_eligible_price': rows[-1]['close']}


def simulate_symbol(valid, symbol, start, end, *, lag_minutes=0, bps_side=3,
                    commission_bps_side=0, annual_financing=0, capital=100000,
                    risk_currency=1000, actions=None, fold_windows=None, max_mark_age_seconds=60):
    """Independent book over canonical complete sessions, including half-day marks.

    Missing held-session marks raise rather than omit overnight risk. No model fit
    or fold reset occurs; fold is accounting attribution of daily changes only.
    """
    if symbol not in THRESHOLDS or lag_minutes not in [0, 1, 2]:
        raise ValueError('Unsupported fixed IBS proxy/scenario')
    if min(bps_side, commission_bps_side, annual_financing) < 0 or min(capital, risk_currency) <= 0:
        raise ValueError('Invalid IBS costs/capital')
    cash, shares, basis, last_close, last_day = float(capital), 0, 0., None, None
    realized = fees_total = financing_total = 0.
    history, daily, trades, traces, exclusions = [], [], [], [], []
    actions = actions or set()
    prior_equity = float(capital)
    for session in sessions(start, end):
        day = session['date']
        bars = valid.get((symbol, day))
        if bars is None:
            if shares:
                raise ValueError(f'IBS_MISSING_HELD_SESSION:{symbol}:{day}')
            history = []
            exclusions.append({'symbol': symbol, 'date': day, 'reason': 'MISSING_COMPLETE_SESSION'})
            continue
        rows = bars.sort('timestamp_utc').to_dicts()
        close, op = rows[-1]['close'], rows[0]['open']
        old_shares = shares
        gap = old_shares * (op - last_close) if last_close is not None else 0.
        elapsed = (date.fromisoformat(day) - date.fromisoformat(last_day)).days if last_day else 0
        financing = old_shares * (last_close or 0) * annual_financing * elapsed / 365
        cash -= financing
        financing_total += financing
        action = (symbol, day) in actions
        if action and shares:
            raise ValueError(f'IBS_HELD_CORPORATE_ACTION_REQUIRES_ACCOUNTING:{symbol}:{day}')
        if action:
            history = []
        check = None
        atr = None
        if not session['early'] and not action:
            check = asof_check(bars, day, decision_lag_minutes=lag_minutes,
                               max_mark_age_seconds=max_mark_age_seconds + 60 * lag_minutes)
            eligible_history = history[-21:]
            if len(eligible_history) == 21 and all(d['available_at'] <= check['decision_at'] for d in eligible_history):
                atr = prior_atr(eligible_history)
            quantity = 0
            reason = 'HOLD_OR_NO_SIGNAL'
            if shares and check['ibs'] is not None and check['ibs'] > .5:
                quantity, reason = -shares, 'IBS_EXIT'
            elif not shares and check['ibs'] is not None and check['ibs'] < THRESHOLDS[symbol]:
                if atr is not None and atr > 0:
                    # Quantity is decided from available last price; cash is rechecked at fill.
                    quantity = int(min(atr_size(atr, risk_currency),
                                       max(0, np.floor(cash / (check['last_eligible_price'] *
                                                             (1 + (bps_side + commission_bps_side) / 10000))))))
                    reason = 'IBS_ENTRY'
                else:
                    reason = 'ATR_WARMUP_OR_UNAVAILABLE'
            submit = check['decision_at'] + timedelta(microseconds=1)
            fill_at = stamp(day, f'15:{56 + lag_minutes:02d}')
            arrival = submit + timedelta(seconds=1)
            trace = {'symbol': symbol, 'date': day, **check, 'prior_atr': atr,
                     'submitted_at': submit if quantity else None, 'arrival_at': arrival if quantity else None,
                     'scheduled_fill_at': fill_at, 'requested_quantity': quantity, 'reason': reason}
            if quantity:
                if not check['feature_available_at'] <= check['decision_at'] < submit < arrival < fill_at:
                    raise ValueError('IBS_ORDER_CHRONOLOGY')
                marks = [r for r in rows if r['timestamp_utc'] == fill_at]
                if len(marks) != 1:
                    raise ValueError('IBS_MISSING_FILL_EVENT')
                raw_price = marks[0]['open']
                price = raw_price * (1 + np.sign(quantity) * bps_side / 10000)
                if quantity > 0:
                    quantity = min(quantity, int(max(0, np.floor(cash / (price * (1 + commission_bps_side / 10000))))))
                fee = abs(quantity) * price * commission_bps_side / 10000
                if quantity:
                    if quantity > 0:
                        basis = quantity * price + fee
                    else:
                        realized += -quantity * price - fee - basis
                        basis = 0.
                    cash -= quantity * price + fee
                    shares += quantity
                    fees_total += fee
                    trades.append({'symbol': symbol, 'date': day, 'quantity': quantity, 'reason': reason,
                                   'decision_at': check['decision_at'], 'feature_available_at': check['feature_available_at'],
                                   'submitted_at': submit, 'arrival_at': arrival, 'filled_at': fill_at,
                                   'raw_fill_price': raw_price, 'adverse_fill_price': price, 'commission': fee,
                                   'slippage_currency': abs(quantity) * abs(price - raw_price),
                                   'prior_atr': atr, 'ibs': check['ibs'], 'fill_model': 'FILL_PROXY_ONLY'})
                trace['executed_quantity'] = quantity
            traces.append(trace)
        elif action:
            exclusions.append({'symbol': symbol, 'date': day, 'reason': 'CORPORATE_ACTION_RESET_WARMUP'})
        equity = cash + shares * close
        if equity <= 0:
            raise ValueError('IBS_EQUITY_EXHAUSTED')
        fold = next((f['fold'] for f in (fold_windows or []) if in_interval(day, f['test_start'], f['test_end'])), None)
        daily.append({'symbol': symbol, 'date': day, 'cash': cash, 'shares': shares,
                      'close_mark': close, 'equity': equity, 'daily_return': equity / prior_equity - 1,
                      'daily_pnl': equity - prior_equity, 'overnight_gap_pnl': gap,
                      'financing': financing, 'elapsed_calendar_days': elapsed,
                      'realized_trade_pnl_cumulative': realized, 'unrealized_pnl': shares * close - basis,
                      'commission_cumulative': fees_total, 'financing_cumulative': financing_total,
                      'held_overnight_shares': old_shares, 'fold_attribution': fold,
                      'early_close_no_check': session['early']})
        prior_equity, last_close, last_day = equity, close, day
        if not action:
            history.append({'high': max(r['high'] for r in rows), 'low': min(r['low'] for r in rows),
                            'close': close, 'available_at': max(available(r) for r in rows)})
    x = np.array([r['daily_return'] for r in daily])
    wealth = np.r_[capital, [r['equity'] for r in daily]]
    dd = wealth / np.maximum.accumulate(wealth) - 1
    summary = {'symbol': symbol, 'lag_minutes': lag_minutes, 'bps_side': bps_side,
               'status': 'COMPUTED' if daily else 'NO_OBSERVATIONS', 'sessions': len(daily),
               'entry_orders': sum(r['quantity'] > 0 for r in trades), 'exit_orders': sum(r['quantity'] < 0 for r in trades),
               'terminal_open_shares': shares, 'terminal_equity': prior_equity,
               'terminal_unrealized_pnl': daily[-1]['unrealized_pnl'] if daily else None,
               'net_pnl': prior_equity - capital if daily else None,
               'realized_trade_pnl': realized, 'financing_paid': financing_total,
               'commission_paid': fees_total, 'max_drawdown': float(dd.min()) if daily else None,
               'worst_gap_pnl': min((r['overnight_gap_pnl'] for r in daily), default=None),
               'overnight_exposure_sessions': sum(bool(r['held_overnight_shares']) for r in daily),
               'mean_daily_return': float(x.mean()) if len(x) else None,
               'bootstrap': block_bootstrap(x), 'classification': 'ETF_PROXY_ONLY;FILL_PROXY_ONLY;NO_INTRADAY_MARGIN_MODEL'}
    return {'daily': daily, 'trades': trades, 'traces': traces, 'exclusions': exclusions, 'summary': summary}


def run(cfg, *, frame=None, out=None, fixture=False):
    """CLI integration: run(cfg, frame=canonical_frame_or_None) -> output Path."""
    from .research import write_csv, write_table
    from .ledger import append
    out = Path(out or ROOT / 'results' / ('ibs_' + utcnow().strftime('%Y%m%dT%H%M%S%fZ')))
    out.mkdir(parents=True, exist_ok=False)
    protocol = ROOT / 'experiments/IBS_PROTOCOL.md'
    manifest = {'phase': 'D', 'config': cfg, 'config_hash': digest(cfg), 'protocol_sha256': sha(protocol),
                'code_hashes': code_hashes(), 'external_hashes': external_hashes(cfg),
                'started_at_utc': utcnow(), 'environment': environment(),
                'input_data_sha256': sha256(frame.serialize()).hexdigest() if frame is not None else None,
                'data_provenance': json.loads((ROOT / 'data/manifests/underlying.json').read_text())
                if (ROOT / 'data/manifests/underlying.json').exists() and not fixture else None,
                'holdout_status': 'EXCLUDED_NOT_ANALYZED', 'classification': 'ETF_PROXY_ONLY',
                'status': 'SYNTHETIC_TEST_ONLY' if fixture else 'INCONCLUSIVE_RESEARCH_ONLY' if frame is not None else 'NO_REAL_HISTORICAL_BACKTEST'}
    dump(out / 'run_manifest.json', manifest)
    if frame is None:
        dump(out / 'metrics.json', {'status': 'NO_REAL_HISTORICAL_BACKTEST', 'performance': None})
        (out / 'RESEARCH_REPORT.md').write_text('# Independent IBS ETF proxy\n\nNO_REAL_HISTORICAL_BACKTEST. No empirical performance. Fixed protocol implemented; minute bars and action history required.\n')
        return out
    if frame['synthetic'].any() and not fixture:
        raise ValueError('Synthetic data forbidden in real IBS research')
    end = min(latest_completed(), str(np.datetime64(cfg['holdout_start']) - np.timedelta64(1, 'D')))
    frame = frame.filter((pl.col('bar_start_et').dt.date().cast(pl.String) >= cfg['start']) &
                         (pl.col('bar_start_et').dt.date().cast(pl.String) <= end))
    quality, valid = audit(frame, cfg['start'], end, cfg['symbols'])
    # Complete half-days are accounting sessions even though Phase A has no 15:30 signal.
    for s in sessions(cfg['start'], end):
        if s['early']:
            for symbol in cfg['symbols']:
                g = frame.filter((pl.col('symbol') == symbol) & (pl.col('timestamp_utc') >= s['open']) &
                                 (pl.col('timestamp_utc') < s['close']))
                if set(g['timestamp_utc']) == set(expected_minutes(s)) and (g['volume'] > 0).all():
                    valid[(symbol, s['date'])] = g
                    for q in quality:
                        if q['symbol'] == symbol and q['date'] == s['date']:
                            q.update(status='ACCOUNTING_ONLY', reasons=['EARLY_CLOSE_NO_1555_CHECK'])
    actions = set()
    if cfg.get('corporate_actions_path'):
        actions = {(r['symbol'], r['date']) for r in pl.read_csv(cfg['corporate_actions_path']).to_dicts()}
    summaries, daily, trades, traces, exclusions = [], [], [], [], []
    windows = folds(cfg['start'], cfg['holdout_start'], train_months=cfg['train_months'],
                    validation_months=cfg['validation_months'], test_months=cfg['test_months'])
    for symbol in cfg['symbols']:
        if symbol not in THRESHOLDS:
            raise ValueError('IBS only supports independently labeled SPY/QQQ proxies')
        for lag in [0, 1, 2]:
            for cost in cfg['slippage_bps_side']:
                append(out / 'trials.jsonl', {'phase': 'D', 'symbol': symbol, 'lag_minutes': lag,
                                              'bps_side': cost, 'threshold': THRESHOLDS[symbol],
                                              'status': 'REGISTERED_BEFORE_SCENARIO', 'fixture': fixture})
                result = simulate_symbol(valid, symbol, cfg['start'], end, lag_minutes=lag, bps_side=cost,
                                         commission_bps_side=cfg['commission_bps_side'], actions=actions,
                                         annual_financing=cfg.get('ibs_annual_financing', 0),
                                         capital=cfg.get('ibs_capital', 100000), risk_currency=cfg.get('ibs_risk_currency', 1000),
                                         fold_windows=windows,
                                         max_mark_age_seconds=cfg.get('ibs_max_mark_age_seconds', 60))
                append(out / 'trials.jsonl', {'phase': 'D', 'status': 'SCENARIO_COMPLETED',
                                              'fixture': fixture, **result['summary']})
                summaries.append(result['summary'])
                for key, target in [('daily', daily), ('trades', trades), ('traces', traces), ('exclusions', exclusions)]:
                    target.extend({**r, 'lag_minutes': lag, 'bps_side': cost} for r in result[key])
    write_csv(out / 'daily_equity.csv', daily)
    write_csv(out / 'trade_log.csv', trades)
    write_table(out / 'trades.parquet', trades)
    dump(out / 'order_traces.json', traces)
    dump(out / 'data_quality.json', {'sessions': quality, 'exclusions': exclusions})
    dump(out / 'metrics.json', summaries)
    dump(out / 'walk_forward_attribution.json', {'interpretation': 'Calendar MTM attribution only; fixed rules, continuous positions, no fitting', 'windows': windows})
    (out / 'RESEARCH_REPORT.md').write_text(f'''# Independent IBS ETF proxy

{manifest['status']}. SPY <0.20; QQQ <0.10; exit >0.50 at later checks. No threshold search.
15:55 economic cutoff/decision; 15:56 fills. Separate +1/+2 minute decision AND fill delays.
Latest mark age is limited to 60 seconds plus the expressly simulated decision delay.
ATR uses prior completed sessions only. Cash-limited, long-only, no leverage, no stops.
Continuous daily close valuation retains terminal open positions and unrealized P&L.
Separate ETF books and scenarios; no pooled sample inference. Fold labels attribute daily
MTM only and never reset positions or represent independently validated trade samples.
Costs use adverse minute-open proxies plus commission; financing ACT/365 on prior-close
notional at configured rate (default zero assumption). No actual NBBO/spread, CFD swaps,
corporate-action entitlements, official auction closes, intraday margin calls or live timing
validated. Missing held-session data fails loudly. Unknown action history blocks validation.
This is distinct from Phase A and not a ten-year CFD replication. No deployment eligibility.
''')
    if daily:
        import os
        os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.mpl-cache'))
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        folder = out / 'charts'
        folder.mkdir()
        for symbol in cfg['symbols']:
            base = [r for r in daily if r['symbol'] == symbol and r['lag_minutes'] == 0 and r['bps_side'] == 3]
            if not base:
                continue
            equity = np.array([r['equity'] for r in base])
            initial = cfg.get('ibs_capital', 100000)
            fig, axes = plt.subplots(2, 1, figsize=(10, 6))
            axes[0].plot([r['date'] for r in base], equity)
            axes[1].plot([r['date'] for r in base], equity / np.maximum.accumulate(np.r_[initial, equity])[1:] - 1)
            axes[0].set_ylabel('Account equity')
            axes[1].set_ylabel('Drawdown')
            for ax in axes:
                ax.set_xticks(ax.get_xticks()[::max(1, len(base) // 6)])
            fig.suptitle('SYNTHETIC TEST ONLY' if fixture else f'{symbol} IBS ETF proxy; historical bar fills')
            fig.tight_layout()
            fig.savefig(folder / f'{symbol}_equity_underwater.png')
            plt.close(fig)
    return out
