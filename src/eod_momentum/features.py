from __future__ import annotations

import numpy as np
import polars as pl

from .calendar import sessions
from .common import stamp


def available(row):
    receipt = row['first_available_at_utc'] or row['assumed_available_at_utc']
    revision = row.get('revision_available_at_utc')
    # Finalized revised prices cannot be treated as the original published value.
    return max(receipt, revision) if revision else receipt


def features_asof(bars, prev_close, day, cutoff='15:30', decision='15:31'):
    cut, dec = stamp(day, cutoff), stamp(day, decision)
    if dec < cut or prev_close <= 0:
        raise ValueError('Invalid cutoff/decision or previous close')
    # Restrict economic interval first; never use a fully formed 15:30 minute.
    eligible = bars.filter(pl.col('bar_end_utc') <= cut)
    rows = eligible.to_dicts()
    if not rows or rows[-1]['bar_end_utc'] != cut:
        raise ValueError('MISSING_CUTOFF_MARK')
    if any(available(r) > dec for r in rows):
        raise ValueError('FUTURE_INFORMATION_POISON: bar unavailable by decision')
    prices = np.array([r['close'] for r in rows])
    high, low = max(r['high'] for r in rows), min(r['low'] for r in rows)
    lookup = {r['bar_start_et'].strftime('%H:%M'): r for r in rows}
    p = prices[-1]
    noon = lookup['11:59']['close']
    return {'symbol': rows[-1]['symbol'], 'date': day, 'r_pre': float(p / prev_close - 1),
            'cutoff_price': p, 'mark_at': rows[-1]['bar_end_utc'],
            'feature_available_at': max(available(r) for r in rows), 'decision_at': dec,
            'r_morning': noon / rows[0]['open'] - 1, 'r_afternoon': p / noon - 1,
            'r_1430_1530': p / lookup['14:30']['open'] - 1,
            'rv_lookback': float(np.std(np.diff(np.log(prices)), ddof=1)),
            'range_location': (p - low) / (high - low) if high > low else None,
            'dollar_volume_pre': sum(r['close'] * r['volume'] for r in rows),
            'prev_close_source': 'PREVIOUS_RTH_15:59_CLOSE_PROXY',
            'availability_basis': 'ASSUMED' if any(r['availability_basis'].startswith('ASSUMED')
                                                  for r in rows) else 'OBSERVED'}


def build_features(valid, start, end, cfg, actions=None):
    out, exclusions = [], []
    dates = [s['date'] for s in sessions(start, end)]
    actions = actions or set()
    for symbol in cfg['symbols']:
        closing_dv = []
        for i, day in enumerate(dates):
            bars = valid.get((symbol, day))
            prev = valid.get((symbol, dates[i - 1])) if i else None
            if bars is None:
                continue
            if prev is None or (symbol, day) in actions or (i and (symbol, dates[i - 1]) in actions):
                exclusions.append({'symbol': symbol, 'date': day,
                                   'reason': 'MISSING_PRIOR_SESSION_OR_CORPORATE_ACTION'})
            else:
                try:
                    if available(prev.to_dicts()[-1]) > stamp(day, cfg['decision']):
                        raise ValueError('PRIOR_CLOSE_NOT_AVAILABLE')
                    f = features_asof(bars, prev['close'][-1], day, cfg['cutoff'], cfg['decision'])
                    history = closing_dv[-20:]
                    f['closing_volume_reference'] = float(np.mean([v for v, _ in history])) if (
                        len(history) >= 20 and all(a <= f['decision_at'] for _, a in history)) else None
                    out.append(f)
                except ValueError as exc:
                    exclusions.append({'symbol': symbol, 'date': day, 'reason': str(exc)})
            late = bars.filter(pl.col('bar_start_et').dt.strftime('%H:%M') >= '15:30')
            closing_dv.append((float((late['close'] * late['volume']).sum()),
                               max(available(r) for r in late.to_dicts())))
    return sorted(out, key=lambda f: (f['date'], f['symbol'])), exclusions


def signal(feature, model, theta=0.0):
    allowed = {'symbol', 'date', 'r_pre', 'cutoff_price', 'mark_at', 'feature_available_at',
               'decision_at', 'r_morning', 'r_afternoon', 'r_1430_1530', 'rv_lookback',
               'range_location', 'dollar_volume_pre', 'prev_close_source', 'availability_basis',
               'closing_volume_reference'}
    if set(feature) - allowed:
        raise ValueError('Unsupported feature: arbitrary future-price columns are forbidden')
    if model == 'flat':
        return 0
    if model == 'long':
        return 1
    if model == 'short':
        return -1
    if model not in ['momentum', 'reversal']:
        raise ValueError('Unknown model')
    r = feature['r_pre']
    q = int(r > theta) - int(r < -theta)
    return q if model == 'momentum' else -q
