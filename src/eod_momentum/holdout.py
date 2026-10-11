"""A one-use holdout seal: freeze before evaluation; failures consume the attempt."""
import json
from pathlib import Path

import numpy as np
import polars as pl

from .calendar import latest_completed, sessions
from .common import ROOT, code_hashes, digest, dump, external_hashes, sha, utcnow
from .data import audit
from .engine import simulate
from .features import build_features, signal
from .research import write_csv, write_table
from .statistics import block_bootstrap, metrics


def freeze(cfg, run_dir, seal=None):
    run_dir = Path(run_dir)
    m = json.loads((run_dir / 'run_manifest.json').read_text())
    if m['data_status'] != 'REAL_IMPORTED' or m['config_hash'] != digest(cfg):
        raise ValueError('Cannot freeze from synthetic/absent/mismatched research')
    if m['code_hashes'] != code_hashes() or m['protocol_status'] != 'PRE_REGISTERED':
        raise ValueError('Code or preregistered protocol changed')
    if m['data_sha256'] != sha(ROOT / 'data/processed/underlying.parquet') or (
            m.get('external_hashes') != external_hashes(cfg)):
        raise ValueError('Source data or external dependencies changed since research run')
    stats = json.loads((run_dir / 'metrics.json').read_text())
    eligible = [r for r in stats if r['symbol'] == 'SPY' and r['cost_bps_side'] == 3 and
                r['strategy'].startswith(('momentum_', 'reversal_')) and r['trades'] >= 100 and
                r['sessions'] >= 200]
    if not eligible:
        raise ValueError('Insufficient development evidence for final selection')
    best = max(eligible, key=lambda r: (r['mean_net_session'], r['strategy']))
    model, value = best['strategy'].split('_')
    if value == 'selected':
        ledger = pl.read_csv(run_dir / 'model_ledger.csv').filter(
            (pl.col('model') == model) & (pl.col('symbol') == 'SPY'))
        last = ledger.filter(pl.col('fold') == ledger['fold'].max()).sort(
            ['mean_validation_net', 'theta'], descending=[True, False])
        theta = last['theta'][0]
    else:
        theta = float(value)
    seal = Path(seal or ROOT / 'experiments/holdout_seal.json')
    record = {'frozen_at': utcnow().isoformat(), 'model': model, 'theta': theta,
              'selected_strategy': best['strategy'], 'code_hashes': code_hashes(),
              'config_hash': digest(cfg), 'external_hashes': external_hashes(cfg), 'data_hash': sha(ROOT / 'data/processed/underlying.parquet'),
              'protocol_hash': sha(ROOT / 'experiments/RESEARCH_PROTOCOL.md'),
              'source_run': str(run_dir), 'source_metrics_hash': sha(run_dir / 'metrics.json'),
              'holdout_start': cfg['holdout_start'], 'end_inclusive': latest_completed()}
    with seal.open('x') as fh:
        json.dump(record, fh, indent=2)
    return seal


def evaluate(cfg, seal=None):
    seal = Path(seal or ROOT / 'experiments/holdout_seal.json')
    locked = json.loads(seal.read_text())
    data_path = ROOT / 'data/processed/underlying.parquet'
    if (locked['code_hashes'] != code_hashes() or locked['config_hash'] != digest(cfg) or
            locked.get('external_hashes') != external_hashes(cfg) or
            locked['data_hash'] != sha(data_path) or
            locked['protocol_hash'] != sha(ROOT / 'experiments/RESEARCH_PROTOCOL.md')):
        raise ValueError('Frozen code/config/data/protocol mismatch; holdout evaluation forbidden')
    # Exclusive marker before any computation. Failure cannot be retried as an untouched holdout.
    marker = seal.with_suffix('.consumed.json')
    with marker.open('x') as fh:
        json.dump({'consumed_at': utcnow().isoformat(), 'status': 'EVALUATION_STARTED'}, fh)
    frame = pl.read_parquet(data_path)
    if frame['synthetic'].any():
        raise ValueError('Synthetic holdout forbidden')
    start = locked['holdout_start']
    previous = [s['date'] for s in sessions(str(np.datetime64(start) - np.timedelta64(14, 'D')), start)
                if s['date'] < start][-1]
    quality, valid = audit(frame, previous, locked['end_inclusive'], cfg['symbols'])
    actions = set()
    if cfg.get('corporate_actions_path'):
        actions = {(r['symbol'], r['date']) for r in pl.read_csv(cfg['corporate_actions_path']).to_dicts()}
    features, exclusions = build_features(valid, previous, locked['end_inclusive'], cfg, actions)
    rows = []
    for f in features:
        if f['date'] < start:
            continue
        for cost in cfg['slippage_bps_side']:
            r = simulate(f, valid[(f['symbol'], f['date'])], signal(f, locked['model'], locked['theta']),
                         entry=cfg['entry'], exit=cfg['exit'], slippage=cost,
                         commission=cfg['commission_bps_side'])
            r.pop('events')
            rows.append({**r, 'cost_bps_side': cost})
    out = ROOT / 'results' / ('holdout_' + utcnow().strftime('%Y%m%dT%H%M%S%fZ'))
    out.mkdir()
    write_table(out / 'trades.parquet', rows)
    write_csv(out / 'daily_pnl.csv', rows)
    summary = []
    for symbol in cfg['symbols']:
        for cost in cfg['slippage_bps_side']:
            sub = [r for r in rows if r['symbol'] == symbol and r['cost_bps_side'] == cost]
            summary.append({'symbol': symbol, 'cost_bps_side': cost, **metrics(sub),
                            'bootstrap': block_bootstrap([r['net'] for r in sub])})
    dump(out / 'metrics.json', summary)
    dump(out / 'quality.json', {'sessions': quality, 'exclusions': exclusions})
    dump(out / 'frozen_rule.json', locked)
    dump(marker, {'consumed_at': utcnow(), 'status': 'CONSUMED', 'output': str(out)})
    (out / 'RESEARCH_REPORT.md').write_text(
        '# One-time final holdout\n\nINCONCLUSIVE_RESEARCH_ONLY: quote/availability and '
        'official close validation remain unresolved. No retuning on this holdout.\n')
    return out
