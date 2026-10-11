from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import polars as pl

from .calendar import latest_completed, sessions
from .common import ROOT, code_hashes, digest, dump, environment, external_hashes, sha, stamp, utcnow
from .data import audit
from .engine import screening_reference, simulate
from .features import build_features, signal
from .ledger import append
from .statistics import block_bootstrap, hac_regression, metrics, multiplicity
from .walk_forward import folds, in_interval

TRADE_SCHEMA = {'symbol': pl.String, 'date': pl.String, 'strategy': pl.String, 'fold': pl.Int64,
                'q': pl.Int64, 'gross': pl.Float64, 'net': pl.Float64, 'cost_bps_side': pl.Float64}


def candidates(cfg):
    out = [{'strategy': m, 'model': m, 'theta': 0.0} for m in ['flat', 'long', 'short']]
    for model in ['momentum', 'reversal']:
        out += [{'strategy': f'{model}_{t:g}', 'model': model, 'theta': t} for t in cfg['thresholds']]
        out.append({'strategy': f'{model}_selected', 'model': model, 'theta': None})
    return out


def write_csv(path, rows, fields=None):
    fields = fields or list(rows[0]) if rows else fields or ['status']
    with Path(path).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def write_table(path, rows, schema=None):
    f = pl.DataFrame(rows, infer_schema_length=None) if rows else pl.DataFrame(schema=schema or TRADE_SCHEMA)
    f.write_parquet(path)
    return f


def drop_best_trades(rows, count):
    """Remove executed trades, retaining calendar dates as flat observations.

    Stable input order resolves equal-return ties. This diagnostic does not alter
    the base strategy book. See experiments/ERRATUM_001_DROP_BEST_TRADES.md.
    """
    if count < 0:
        raise ValueError('Trade removal count must be nonnegative')
    active = (i for i, row in enumerate(rows) if row['q'])
    removed = set(sorted(active, key=lambda i: rows[i]['net'], reverse=True)[:count])
    return [{**row, 'net': 0, 'gross': 0, 'q': 0, 'fees': 0,
             'slippage': 0, 'exposure_minutes': 0} if i in removed else dict(row)
            for i, row in enumerate(rows)]


def preregister(cfg):
    path = ROOT / 'experiments/registry.csv'
    rows = candidates(cfg)
    for i, r in enumerate(rows, 1):
        r.update(trial_id=i, registration='PRE_REGISTERED', phase='A', status='AWAITING_DATA')
    if path.exists():
        return
    write_csv(path, rows)
    dump(ROOT / 'experiments/protocol_lock.json', {
        'registered_at': utcnow(), 'protocol_sha256': sha(ROOT / 'experiments/RESEARCH_PROTOCOL.md'),
        'registry_sha256': sha(path), 'config_hash': digest(cfg), 'model_count': len(rows),
        'holdout_start': cfg['holdout_start']})


def protocol_status(cfg):
    lock = json.loads((ROOT / 'experiments/protocol_lock.json').read_text())
    valid = (lock['protocol_sha256'] == sha(ROOT / 'experiments/RESEARCH_PROTOCOL.md') and
             lock['registry_sha256'] == sha(ROOT / 'experiments/registry.csv') and
             lock['config_hash'] == digest(cfg))
    return 'PRE_REGISTERED' if valid else 'EXPLORATORY_PROTOCOL_CHANGED'


def manifest(cfg, frame=None, fixture=False):
    path = ROOT / 'data/processed/underlying.parquet'
    prov = ROOT / 'data/manifests/underlying.json'
    return {'started_at_utc': utcnow(), 'config': cfg, 'config_hash': digest(cfg),
            'code_hashes': code_hashes(), 'external_hashes': external_hashes(cfg), 'protocol_status': protocol_status(cfg),
            'protocol_hash': sha(ROOT / 'experiments/RESEARCH_PROTOCOL.md'),
            'data_sha256': sha(path) if path.exists() and not fixture else None,
            'data_provenance': json.loads(prov.read_text()) if prov.exists() and not fixture else None,
            'data_rows': frame.height if frame is not None else 0,
            'data_status': 'SYNTHETIC_TEST_ONLY' if fixture else 'REAL_IMPORTED' if frame is not None
            else 'NO_REAL_HISTORICAL_BACKTEST', 'latest_completed': latest_completed(),
            'holdout_start': cfg['holdout_start'], 'holdout_status': 'SEALED_NOT_ANALYZED',
            'environment': environment(), 'random_seed': cfg['bootstrap_seed']}


def scorecard(out, has_data, *, results=None, fixture=False, protocol='PRE_REGISTERED'):
    gates = [
        ('G1', 'INCONCLUSIVE', 'data_quality.json',
         'NO_REAL_HISTORICAL_BACKTEST' if not has_data else
         'FILL_PROXY_ONLY; official close/action history/representative NBBO validation required'),
        ('G2', 'INCONCLUSIVE', 'reconciliation_report.json',
         'Tests establish fixture behavior; genuine WFA and frozen final holdout still required'),
        ('G3', 'INCONCLUSIVE', 'metrics.json', 'No validated conservative OOS/holdout edge'),
        ('G4', 'INCONCLUSIVE', 'stress_tests.csv', 'Genuine fold, latency and event stability unresolved'),
        ('G5', 'INCONCLUSIVE', 'DATA_ACCESS_BLOCKERS.md', 'Live input/timing/Pine feasibility unverified')]
    if results and not fixture:
        core = [r for r in results if r.get('cost_bps_side') == 3 and
                r['strategy'] in ['momentum_0', 'reversal_0'] and r['symbol'] == 'SPY']
        if core and all(r['mean_net_session'] <= 0 for r in core):
            gates[2] = ('G3', 'FAIL', 'metrics.json', 'Both zero-tuning families nonpositive at 3 bps/side')
    write_csv(out / 'robustness_scorecard.csv', [dict(zip(['gate', 'status', 'evidence', 'limitation'], g))
                                               for g in gates])


def empty_outputs(out, cfg, m, reason):
    dump(out / 'run_manifest.json', m)
    dump(out / 'environment_manifest.json', m['environment'])
    dump(out / 'data_quality.json', {'status': reason, 'real_sessions': 0, 'excluded_sessions': None})
    dump(out / 'data_provenance.json', m.get('data_provenance') or {'status': 'NO_DATA_ACQUIRED'})
    dump(out / 'metrics.json', {'status': reason, 'performance': None})
    dump(out / 'multiplicity.json', multiplicity(0, len(candidates(cfg))))
    dump(out / 'reconciliation_report.json', {'status': 'SEE_TEST_REPORT', 'real_data_parity': 'NOT_RUN'})
    write_csv(out / 'walk_forward_folds.csv', folds(cfg['start'], cfg['holdout_start']))
    for name in ['daily_pnl', 'baseline_comparisons', 'model_ledger', 'execution_cost_frontier',
                 'stress_tests', 'null_controls', 'calibration', 'holdout_status']:
        write_csv(out / f'{name}.csv', [{'status': reason}])
    write_table(out / 'trades.parquet', [])
    write_table(out / 'signals.parquet', [], {'symbol': pl.String, 'date': pl.String, 'r_pre': pl.Float64})
    scorecard(out, False)
    text = f'''# Research report

**NO_REAL_HISTORICAL_BACKTEST**

{reason}. No empirical profitability, trade logs, confidence intervals, or performance charts exist.
Empty tables are schema artifacts, not simulated zero-return results.

Target SPY/QQQ: {cfg['start']}–{m['latest_completed']}. Real coverage: **none**.
Holdout: [{cfg['holdout_start']}, after latest completed session), sealed; never evaluated.
15 registered baseline/selection rules; 100 seeded null controls are diagnostic only.
Train/validation/test: 12/3/3 calendar months; see proposed folds CSV. No folds executed on real data.
Costs: 0/1/3/5 bps per side plus commission. No empirical cost frontier available.

Infrastructure: raw-price/UTC schemas, XNYS calendar, as-of features, event-driven fills,
Parquet/Polars/DuckDB storage, chronological WFA, date-block bootstrap, cost/latency tests,
append-only trials, separate research vs execution endpoints, sealed holdout commands.
IBS ETF bookkeeping, GEX sign/unit and option-NBBO utilities are tested only; later phases need data.
No calibrated probability model; DSR/PBO NOT_ESTIMABLE; no indicator or live-trading code.
All G1–G5 remain INCONCLUSIVE; no candidate can graduate. Unit fixtures are not evidence of alpha.

Next evidence: authorized 1-minute raw SPY/QQQ history, corporate actions, official closes,
and representative historical NBBO with timestamp/size information. See DATA_ACCESS_BLOCKERS.md.
'''
    (out / 'RESEARCH_REPORT.md').write_text(text)
    (out / 'charts').mkdir(exist_ok=True)
    (out / 'charts/NOT_GENERATED.md').write_text('No market data: performance charts would fabricate evidence.\n')
    dump(out / 'artifact_hashes.json', {str(p.relative_to(out)): sha(p) for p in out.rglob('*') if p.is_file()})


def run(cfg, *, frame=None, out=None, fixture=False):
    preregister(cfg)
    if out is None:
        out = ROOT / 'results' / (utcnow().strftime('%Y%m%dT%H%M%S%fZ'))
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    if frame is not None and 'synthetic' in frame.columns and frame['synthetic'].any() and not fixture:
        raise ValueError('Synthetic data forbidden in real research run')
    m = manifest(cfg, frame, fixture)
    dump(out / 'run_manifest.json', m)  # pre-outcome provenance
    for candidate in candidates(cfg):
        append(out / 'trials.jsonl', {'run': out.name, 'phase': 'A', **candidate,
                                    'status': 'REGISTERED_BEFORE_ANALYSIS', 'fixture': fixture})
    if frame is None:
        for candidate in candidates(cfg):
            append(out / 'trials.jsonl', {**candidate, 'status': 'BLOCKED_NO_DATA'})
        empty_outputs(out, cfg, m, 'Missing credentials and licensed minute-bar files')
        return out
    end = latest_completed()
    # Sealed holdout rows are never fed to feature computation or outcome analysis.
    frame = frame.filter((pl.col('bar_start_et').dt.date().cast(pl.String) >= cfg['start']) &
                         (pl.col('bar_start_et').dt.date().cast(pl.String) < cfg['holdout_start']) &
                         (pl.col('bar_start_et').dt.date().cast(pl.String) <= end))
    dev_end = min(end, str((np.datetime64(cfg['holdout_start']) - np.timedelta64(1, 'D'))))
    quality, valid = audit(frame, cfg['start'], dev_end, cfg['symbols'])
    actions = set()
    if cfg.get('corporate_actions_path'):
        actions = {(r['symbol'], r['date']) for r in pl.read_csv(cfg['corporate_actions_path']).to_dicts()}
    features, excluded = build_features(valid, cfg['start'], dev_end, cfg, actions)
    dump(out / 'data_quality.json', {'sessions': quality, 'feature_exclusions': excluded,
                                    'actions_status': 'SUPPLIED' if cfg.get('corporate_actions_path') else 'UNAVAILABLE_G1_BLOCKED',
                                    'holdout': 'NOT_AUDITED_FOR_OUTCOMES'})
    write_table(out / 'signals.parquet', features,
                {'symbol': pl.String, 'date': pl.String, 'r_pre': pl.Float64})
    all_folds = folds(cfg['start'], cfg['holdout_start'], train_months=cfg['train_months'],
                      validation_months=cfg['validation_months'], test_months=cfg['test_months'])
    cache = {}

    def trade(f, model, theta, cost, entry=None, exit=None):
        q = signal(f, model, theta)
        en, ex = entry or cfg['entry'], exit or cfg['exit']
        key = (f['symbol'], f['date'], q, en, ex)
        if key not in cache:
            decision_feature = {**f, 'decision_at': stamp(f['date'], '15:35')} if en in ['15:36', '15:37'] else f
            cache[key] = simulate(decision_feature, valid[(f['symbol'], f['date'])], q, entry=en, exit=ex,
                                  slippage=0, commission=0)
        result = dict(cache[key])
        result.pop('events')
        result['slippage'] = abs(result['q']) * 2 * cost / 10000
        result['fees'] = abs(result['q']) * 2 * cfg['commission_bps_side'] / 10000
        result['net'] = result['gross'] - result['slippage'] - result['fees']
        result['cost_bps_side'] = cost
        result['theta'] = theta
        return result

    daily, fold_ledger, selection_rows, stress_rows = [], [], [], []
    for fold in all_folds:
        for symbol in cfg['symbols']:
            sub = [f for f in features if f['symbol'] == symbol]
            segments = {name: [f for f in sub if in_interval(f['date'], fold[f'{name}_start'], fold[f'{name}_end'])]
                        for name in ['train', 'validation', 'test']}
            coverage = {}
            for name in segments:
                expected = len([s for s in sessions(fold[f'{name}_start'],
                                                   str((np.datetime64(fold[f'{name}_end']) -
                                                        np.timedelta64(1, 'D')))) if not s['early']])
                coverage[name] = len(segments[name]) / max(1, expected)
            if min(coverage.values()) < cfg.get('min_session_coverage', 0.95):
                fold_ledger.append({**fold, 'symbol': symbol, 'status': 'SKIPPED_INSUFFICIENT_COVERAGE',
                                    'coverage': json.dumps(coverage)})
                continue
            fold_ledger.append({**fold, 'symbol': symbol, 'status': 'EXECUTED',
                                'coverage': json.dumps(coverage)})
            selected = {}
            for model in ['momentum', 'reversal']:
                choices = []
                for theta in cfg['thresholds']:
                    val = [trade(f, model, theta, cfg['selection_cost_bps_side'])
                           for f in segments['validation']]
                    score = float(np.mean([t['net'] for t in val]))
                    choices.append((score, -theta, theta))
                    row = {'fold': fold['fold'], 'symbol': symbol, 'model': model, 'theta': theta,
                           'mean_validation_net': score, 'validation_dates': len(val)}
                    selection_rows.append(row)
                    append(out / 'trials.jsonl', {**row, 'status': 'VALIDATION_EVALUATED'})
                selected[model] = max(choices)[2]
            for candidate in candidates(cfg):
                theta = candidate['theta'] if candidate['theta'] is not None else selected[candidate['model']]
                for cost in cfg['slippage_bps_side']:
                    for f in segments['test']:
                        daily.append({**trade(f, candidate['model'], theta, cost),
                                      'strategy': candidate['strategy'], 'fold': fold['fold']})
                scenarios = [(en, cfg['exit'], 3, 'entry_' + en) for en in cfg['stress_entry_times']]
                scenarios += [(cfg['entry'], ex, 3, 'exit_' + ex) for ex in cfg['stress_exit_times']]
                scenarios += [(cfg['entry'], cfg['exit'], c, f'friction_{c}') for c in [6, 9]]
                for en, ex, cost, scenario in scenarios:
                    # Delayed signals retain original cutoff; later decision is a latency stress only.
                    records = [trade(f, candidate['model'], theta, cost, en, ex) for f in segments['test']]
                    stress = {**metrics(records), 'fold': fold['fold'], 'symbol': symbol,
                              'strategy': candidate['strategy'], 'scenario': scenario,
                              'entry': en, 'exit': ex, 'cost_bps_side': cost}
                    stress_rows.append(stress)
                    append(out / 'trials.jsonl', {'status': 'STRESS_EVALUATED', **stress})
    write_csv(out / 'walk_forward_folds.csv', fold_ledger or all_folds)
    write_csv(out / 'model_ledger.csv', selection_rows)
    write_csv(out / 'daily_pnl.csv', daily)
    write_table(out / 'trades.parquet', [r for r in daily if r['q']], TRADE_SCHEMA)
    groups = defaultdict(list)
    for row in daily:
        groups[(row['symbol'], row['strategy'], row['cost_bps_side'])].append(row)
    summary, frontier, comparisons, stratified, nulls = [], [], [], [], []
    for (symbol, strategy, cost), rows in groups.items():
        rows.sort(key=lambda r: r['date'])
        dates = [r['date'] for r in rows]
        if len(dates) != len(set(dates)):
            raise ValueError('Overlapping OOS tests')
        stat = metrics(rows)
        if cost == 3:
            stat['bootstrap'] = block_bootstrap([r['net'] for r in rows], samples=cfg['bootstrap_samples'],
                                               seed=cfg['bootstrap_seed'], block=cfg['bootstrap_block_days'])
        summary.append({'symbol': symbol, 'strategy': strategy, 'cost_bps_side': cost, **stat})
        if cost == 0:
            frontier.append({'symbol': symbol, 'strategy': strategy,
                             'break_even_round_trip_bps': stat['break_even_round_trip_bps_per_trade']})
        if cost != 3:
            continue
        for bench in ['long', 'short', 'flat', 'momentum_0', 'reversal_0']:
            base = {r['date']: r for r in groups[(symbol, bench, cost)]}
            diff = [r['net'] - base[r['date']]['net'] for r in rows]
            comparisons.append({'symbol': symbol, 'strategy': strategy, 'benchmark': bench,
                                'lift_mean_net': float(np.mean(diff)),
                                'ci': json.dumps(block_bootstrap(diff, samples=cfg['bootstrap_samples'],
                                                                seed=cfg['bootstrap_seed']))})
        for k in [1, 5]:
            kept = drop_best_trades(rows, k)
            stress_rows.append({'symbol': symbol, 'strategy': strategy, 'scenario': f'drop_best_{k}',
                                **metrics(kept)})
        for grouping in ['year', 'month', 'quarter', 'fold', 'direction', 'weekday']:
            buckets = defaultdict(list)
            for r in rows:
                feat = next(f for f in features if f['symbol'] == symbol and f['date'] == r['date'])
                key = {'year': r['date'][:4], 'month': r['date'][:7],
                       'quarter': r['date'][:4] + 'Q' + str((int(r['date'][5:7]) - 1) // 3 + 1),
                       'fold': str(r['fold']), 'direction': 'positive' if feat['r_pre'] > 0 else 'negative',
                       'weekday': str(stamp(r['date'], '15:30').weekday())}[grouping]
                buckets[key].append(r)
            stratified += [{'symbol': symbol, 'strategy': strategy, 'grouping': grouping, 'bucket': k,
                            **metrics(v)} for k, v in buckets.items()]
    # All fixed seeds retained; no best-seed selection. Same date random sign shared across assets.
    core = [r for r in daily if r['strategy'] == 'long' and r['cost_bps_side'] == 3]
    null_dates = sorted({r['date'] for r in core})
    for seed in range(cfg['null_seeds']):
        rng = np.random.default_rng(cfg['bootstrap_seed'] + seed)
        q = dict(zip(null_dates, rng.choice([-1, 1], len(null_dates))))
        for symbol in cfg['symbols']:
            x = [q[r['date']] * r['gross'] - r['slippage'] - r['fees'] for r in core if r['symbol'] == symbol]
            if x:
                nulls.append({'seed': seed, 'symbol': symbol, 'mean_net': float(np.mean(x))})
    predictive = []
    oos_dates = {(r['symbol'], r['date']) for r in core}
    for symbol in cfg['symbols']:
        fs = [f for f in features if f['symbol'] == symbol and (symbol, f['date']) in oos_dates]
        x = [f['r_pre'] for f in fs]
        y = [valid[(symbol, f['date'])]['close'][-1] / f['cutoff_price'] - 1 for f in fs]
        predictive.append({'symbol': symbol, 'endpoint': '15:29_CLOSE_TO_15:59_CLOSE_PROXY',
                           'official_auction_close': False, **hac_regression(x, y)})
    joint = []
    for strategy in [c['strategy'] for c in candidates(cfg)]:
        by_symbol = {s: {r['date']: r['net'] for r in groups.get((s, strategy, 3), [])} for s in cfg['symbols']}
        common = sorted(set.intersection(*(set(v) for v in by_symbol.values())))
        matrix = [[by_symbol[s][d] for s in cfg['symbols']] for d in common]
        joint.append({'strategy': strategy, 'common_dates': len(common),
                      'capital_policy': '50/50 unlevered; no cross-asset independent-row resampling',
                      'bootstrap': block_bootstrap(matrix, samples=cfg['bootstrap_samples'],
                                                   seed=cfg['bootstrap_seed']) if common else
                      {'status': 'NOT_ESTIMABLE'}})
    write_csv(out / 'baseline_comparisons.csv', comparisons)
    write_csv(out / 'execution_cost_frontier.csv', frontier)
    write_csv(out / 'stress_tests.csv', stress_rows)
    write_csv(out / 'stratified.csv', stratified)
    write_csv(out / 'null_controls.csv', nulls)
    write_csv(out / 'calibration.csv', [{'status': 'NOT_APPLICABLE', 'reason': 'No probabilities estimated'}])
    dump(out / 'predictive.json', predictive)
    dump(out / 'joint_date_bootstrap.json', joint)
    dump(out / 'metrics.json', summary)
    dump(out / 'multiplicity.json', multiplicity(len(null_dates), len(candidates(cfg))))
    dump(out / 'environment_manifest.json', m['environment'])
    dump(out / 'data_provenance.json', m.get('data_provenance') or {'status': 'TEST_ONLY' if fixture else 'UNKNOWN'})
    parity = []
    for f in features[:10]:
        bars = valid[(f['symbol'], f['date'])]
        for q in [-1, 0, 1]:
            event = simulate(f, bars, q, slippage=3)
            ref = screening_reference(f, bars, q, slippage=3)
            parity.append(abs(event['net'] - ref) < 1e-12)
    dump(out / 'reconciliation_report.json', {'status': 'PASS' if parity and all(parity) else 'NOT_RUN_OR_FAIL',
                                             'cases': len(parity), 'tolerance': 1e-12,
                                             'final_data_realism': 'FILL_PROXY_ONLY'})
    if features:
        trace = simulate(features[0], valid[(features[0]['symbol'], features[0]['date'])], 1, trace=True)
        dump(out / 'one_session_trace.json', trace)
    scorecard(out, True, results=summary, fixture=fixture)
    status = 'SYNTHETIC_TEST_ONLY' if fixture else 'INCONCLUSIVE_RESEARCH_ONLY'
    m.update(status=status, development_features=len(features), independent_oos_dates=len(null_dates),
             coverage_start=min((f['date'] for f in features), default=None),
             coverage_end=max((f['date'] for f in features), default=None),
             completed_at_utc=utcnow())
    dump(out / 'run_manifest.json', m)
    report = f'''# Research report

**{status}**

Primary SPY; QQQ secondary. {len(features)} eligible development features; {len(null_dates)} distinct
OOS dates. All 15 rules retained, including no-trade/negative variants. Costs 0/1/3/5 bps per side;
6/9 bps and timing/outlier stresses are diagnostic. Performance is stored in metrics.json and
all OOS daily records in daily_pnl.csv; selection evidence in model_ledger.csv.

Holdout [{cfg['holdout_start']}, after {end}) remains sealed. No final winner claim.
Fold boundaries, coverage and skipped folds are in walk_forward_folds.csv. Eligibility exclusions
are in data_quality.json. 95% circular 5-date block bootstrap intervals include flat days; jointly
trading assets are aligned by calendar date. Sharpe uses 252 session annualization. Costs are
additive return-bps, not exact adverse-price arithmetic. Shorting assumes no borrow/locate fees.

Fills: ASSUMED minute-open proxies, FILL_PROXY_ONLY. Historical bar revisions can arrive late.
Economic endpoint uses 15:29/15:59 close proxies, not official auction values; no claim of paper
replication. Raw prices and unknown action history block G1 unless an action file is supplied.
No genuine NBBO subset, live timing proof, calibrated probabilities or deployability evidence.
Bootstrap intervals are exploratory and unadjusted for selection. DSR/PBO NOT_ESTIMABLE.
No interest/cash yield or capital-constrained claims are made. ETF returns are not options returns.

All gates are unresolved or failed: no Pine exports, trade alerts or live orders. Event-calendar,
feed and macro-event ablations requiring unavailable sources remain untested. IBS is independent;
bookkeeping/ATR/gap/financing utilities have fixture tests only. Option/GEX utilities have no
historical empirical validation. Missing inputs are listed in DATA_ACCESS_BLOCKERS.md.
'''
    (out / 'RESEARCH_REPORT.md').write_text(report)
    from .reporting import charts
    charts(out, daily, summary, stress_rows, features, valid, fixture=fixture)
    append(out / 'trials.jsonl', {'status': 'RUN_COMPLETED', 'strategy_count': len(candidates(cfg)),
                                 'independent_oos_dates': len(null_dates), 'fixture': fixture})
    dump(out / 'artifact_hashes.json', {str(p.relative_to(out)): sha(p) for p in out.rglob('*') if p.is_file()})
    return out
