"""Synthetic integrity tests only. No market observations or alpha claims."""
import json
from datetime import timedelta

import polars as pl
import pytest

from conftest import synthetic
from eod_momentum.calendar import sessions
from eod_momentum.common import stamp
from eod_momentum.data import audit, normalize
from eod_momentum.ibs_pipeline import asof_check, run, simulate_symbol


def controlled():
    data = synthetic('2024-02-01', '2024-03-12')
    raw = data.select('symbol', 'timestamp_utc', 'open', 'high', 'low', 'close', 'volume')
    raw = raw.with_columns(pl.lit(100.).alias('open'), pl.lit(101.).alias('high'),
                           pl.lit(99.).alias('low'), pl.lit(100.).alias('close'))
    dates = [s['date'] for s in sessions('2024-02-01', '2024-03-12')]
    entry, later = dates[21:23]
    raw = raw.filter(pl.col('timestamp_utc') < stamp(later, '16:00'))
    raw = raw.with_columns(pl.when(pl.col('timestamp_utc').is_in([stamp(entry, '15:53'), stamp(entry, '15:54')]))
                           .then(99.1).otherwise(pl.col('close')).alias('close'))
    # Later low-range day retains the position; close recovers from 80 to 90,
    # still a terminal unrealized loss against entry 100.
    raw = raw.with_columns([
        pl.when(pl.col('timestamp_utc') >= stamp(later, '09:30')).then(v)
        .otherwise(pl.col(c)).alias(c) for c, v in [('open', 80.), ('high', 81.), ('low', 79.), ('close', 79.1)]])
    raw = raw.with_columns(pl.when(pl.col('timestamp_utc') == stamp(later, '15:59'))
                           .then(90.).otherwise(pl.col('close')).alias('close'),
                           pl.when(pl.col('timestamp_utc') == stamp(later, '15:59'))
                           .then(90.).otherwise(pl.col('high')).alias('high'))
    bars = normalize(raw, source='SYNTHETIC_TEST_ONLY', feed='TEST', synthetic=True)
    _, valid = audit(bars, dates[0], later, ['SPY'])
    return bars, valid, dates[0], entry, later


def test_asof_uses_1553_and_future_range_cannot_poison():
    bars, valid, _, entry, _ = controlled()
    day = valid[('SPY', entry)]
    f = asof_check(day, entry)
    assert f['last_bar_start'] == stamp(entry, '15:53')
    assert f['ibs'] == pytest.approx(.05)
    changed = day.with_columns(pl.when(pl.col('timestamp_utc') >= stamp(entry, '15:54'))
                              .then(999999.).otherwise(pl.col('high')).alias('high'))
    assert asof_check(changed, entry) == f
    late = day.with_columns(pl.when(pl.col('timestamp_utc') == stamp(entry, '15:53'))
                           .then(stamp(entry, '15:56')).otherwise(pl.col('revision_available_at_utc'))
                           .alias('revision_available_at_utc'))
    with pytest.raises(ValueError, match='STALE_PREFIX'):
        asof_check(late, entry)
    assert asof_check(late, entry, max_mark_age_seconds=120)['last_bar_start'] == stamp(entry, '15:52')


def test_prior_atr_timing_terminal_loss_and_calendar_financing():
    _, valid, start, entry, later = controlled()
    r = simulate_symbol(valid, 'SPY', start, later, bps_side=0, annual_financing=.10)
    assert len(r['trades']) == 1
    t = r['trades'][0]
    assert t['date'] == entry and t['prior_atr'] == pytest.approx(2)
    assert t['quantity'] == 500
    assert t['feature_available_at'] <= t['decision_at'] < t['submitted_at'] < t['arrival_at'] < t['filled_at']
    last = r['daily'][-1]
    assert last['unrealized_pnl'] == pytest.approx(-5000)
    assert last['overnight_gap_pnl'] == pytest.approx(-10000)
    assert last['financing'] == pytest.approx(500 * 100 * .10 * last['elapsed_calendar_days'] / 365)
    assert r['summary']['terminal_open_shares'] == 500
    assert last['equity'] == pytest.approx(100000 - 5000 - last['financing'])
    assert all(d['shares'] == 0 for d in r['daily'][:21])


def test_costs_and_lag_scenarios_keep_independent_books():
    _, valid, start, _, end = controlled()
    zero = simulate_symbol(valid, 'SPY', start, end, bps_side=0)
    friction = simulate_symbol(valid, 'SPY', start, end, bps_side=5, commission_bps_side=1, lag_minutes=2)
    assert friction['summary']['net_pnl'] < zero['summary']['net_pnl']
    assert friction['trades'][0]['filled_at'] == stamp(friction['trades'][0]['date'], '15:58')
    assert friction['trades'][0]['decision_at'] == stamp(friction['trades'][0]['date'], '15:57')
    assert friction['trades'][0]['adverse_fill_price'] == pytest.approx(100.05)
    assert friction['trades'][0]['commission'] > 0


def test_missing_held_session_and_known_action_fail_loudly():
    _, valid, start, _, later = controlled()
    missing = {k: v for k, v in valid.items() if k != ('SPY', later)}
    with pytest.raises(ValueError, match='MISSING_HELD_SESSION'):
        simulate_symbol(missing, 'SPY', start, later)
    with pytest.raises(ValueError, match='HELD_CORPORATE_ACTION'):
        simulate_symbol(valid, 'SPY', start, later, actions={('SPY', later)})


def test_late_prior_history_blocks_atr_entry():
    _, valid, start, entry, later = controlled()
    first = valid[('SPY', start)].with_columns(pl.when(pl.col('timestamp_utc') == stamp(start, '15:59'))
                                            .then(stamp(later, '16:00')).otherwise(pl.col('revision_available_at_utc'))
                                            .alias('revision_available_at_utc'))
    valid[('SPY', start)] = first
    result = simulate_symbol(valid, 'SPY', start, entry)
    assert not result['trades']
    assert result['traces'][-1]['reason'] == 'ATR_WARMUP_OR_UNAVAILABLE'


def test_no_data_and_synthetic_guard(cfg, tmp_path):
    p = run(cfg, out=tmp_path / 'empty')
    assert json.loads((p / 'metrics.json').read_text())['performance'] is None
    assert not list(p.rglob('*.png'))
    bars, _, _, _, _ = controlled()
    with pytest.raises(ValueError, match='Synthetic'):
        run(cfg, frame=bars, out=tmp_path / 'refused')


def test_holdout_excluded_and_replay_deterministic(cfg, tmp_path):
    bars, _, start, entry, later = controlled()
    cfg = {**cfg, 'symbols': ['SPY'], 'start': start, 'holdout_start': later,
           'slippage_bps_side': [0], 'ibs_annual_financing': .10}
    first = run(cfg, frame=bars, fixture=True, out=tmp_path / 'first')
    poisoned = bars.with_columns(pl.when(pl.col('timestamp_utc') >= stamp(later, '09:30'))
                                .then(900.).otherwise(pl.col('close')).alias('close'))
    second = run(cfg, frame=poisoned, fixture=True, out=tmp_path / 'second')
    for name in ['metrics.json', 'daily_equity.csv', 'trade_log.csv', 'order_traces.json']:
        assert (first / name).read_bytes() == (second / name).read_bytes()
    daily = pl.read_csv(first / 'daily_equity.csv')
    assert daily['date'].max() == entry
    assert json.loads((first / 'metrics.json').read_text())[0]['terminal_open_shares'] == 500


def test_exit_on_later_check_realized_and_unrealized_reconcile():
    _, valid, start, entry, later = controlled()
    # A later check in the upper range exits; its final close is an accounting
    # mark only and must not alter the execution price or exit decision.
    day = valid[('SPY', later)].with_columns(pl.lit(101.).alias('open'), pl.lit(102.).alias('high'),
                                            pl.lit(100.).alias('low'), pl.lit(101.8).alias('close'))
    valid[('SPY', later)] = day
    result = simulate_symbol(valid, 'SPY', start, later, bps_side=0, annual_financing=.1)
    assert [r['reason'] for r in result['trades']] == ['IBS_ENTRY', 'IBS_EXIT']
    assert result['trades'][1]['date'] > entry
    assert result['summary']['terminal_open_shares'] == 0
    assert result['summary']['terminal_unrealized_pnl'] == 0
    assert result['summary']['realized_trade_pnl'] == pytest.approx(500)
    assert result['summary']['net_pnl'] == pytest.approx(
        result['summary']['realized_trade_pnl'] - result['summary']['financing_paid'])


def test_fold_labels_do_not_reset_or_refit_positions():
    _, valid, start, entry, later = controlled()
    windows = [{'fold': 0, 'test_start': later, 'test_end': '2024-04-01'}]
    result = simulate_symbol(valid, 'SPY', start, later, bps_side=0, fold_windows=windows)
    assert result['daily'][-2]['date'] == entry
    assert result['daily'][-2]['fold_attribution'] is None
    assert result['daily'][-1]['fold_attribution'] == 0
    assert result['daily'][-1]['shares'] == result['daily'][-2]['shares'] == 500


def test_delayed_decision_receipts_keep_original_economic_cutoff():
    _, valid, _, entry, _ = controlled()
    day = valid[('SPY', entry)]
    delayed = asof_check(day, entry, decision_lag_minutes=1, max_mark_age_seconds=120)
    assert delayed['decision_at'] == stamp(entry, '15:56')
    assert delayed['economic_cutoff'] == stamp(entry, '15:55')
    assert delayed['last_bar_start'] == stamp(entry, '15:54')
    assert delayed['feature_available_at'] == stamp(entry, '15:55') + timedelta(seconds=30)
    poisoned = day.with_columns(pl.when(pl.col('timestamp_utc') >= stamp(entry, '15:55'))
                               .then(9999.).otherwise(pl.col('high')).alias('high'))
    assert asof_check(poisoned, entry, decision_lag_minutes=1, max_mark_age_seconds=120) == delayed
