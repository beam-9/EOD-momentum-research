import os
from collections import defaultdict

import numpy as np

from .common import ROOT

os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.mpl-cache'))


def charts(out, daily, summary, stresses, features, valid, *, fixture=False):
    if not daily:
        (out / 'charts').mkdir(exist_ok=True)
        (out / 'charts/NOT_GENERATED.md').write_text('Insufficient OOS coverage; no performance chart.\n')
        return
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    folder = out / 'charts'
    folder.mkdir(exist_ok=True)
    label = 'SYNTHETIC TEST ONLY — NOT RESEARCH' if fixture else 'Historical bar fill proxy; holdout sealed'

    def save(name):
        plt.title(label)
        plt.tight_layout()
        plt.savefig(folder / (name + '.png'), dpi=130)
        plt.close()

    core = [r for r in daily if r['symbol'] == 'SPY' and r['cost_bps_side'] == 3]
    groups = defaultdict(list)
    for r in core:
        groups[r['strategy']].append(r)
    plt.figure(figsize=(10, 5))
    for name, rows in groups.items():
        if name in ['long', 'short', 'flat', 'momentum_0', 'reversal_0']:
            plt.plot(np.cumprod(1 + np.array([r['net'] for r in rows])), label=name)
    plt.ylabel('Unlevered net wealth / initial wealth')
    plt.xlabel('OOS session index')
    plt.legend()
    save('net_equity')
    plt.figure(figsize=(10, 5))
    for name in ['long', 'momentum_0', 'reversal_0']:
        x = np.cumprod(1 + np.array([r['net'] for r in groups[name]]))
        plt.plot(x / np.maximum.accumulate(np.r_[1, x])[1:] - 1, label=name)
    plt.legend()
    plt.ylabel('Drawdown')
    save('drawdown')
    plt.figure(figsize=(10, 5))
    for name in ['long', 'momentum_0', 'reversal_0']:
        rows = sorted([r for r in summary if r['symbol'] == 'SPY' and r['strategy'] == name],
                      key=lambda r: r['cost_bps_side'])
        plt.plot([r['cost_bps_side'] for r in rows], [r['mean_net_session'] * 10000 for r in rows],
                 marker='o', label=name)
    plt.axhline(0, color='black', linewidth=0.5)
    plt.xlabel('Slippage bps per side, commission separate')
    plt.ylabel('Mean net bps per OOS session')
    plt.legend()
    save('cost_sensitivity')
    plt.figure(figsize=(10, 5))
    vals = [r for r in summary if r['symbol'] == 'SPY' and r['cost_bps_side'] == 0 and
            r['break_even_round_trip_bps_per_trade'] is not None]
    plt.barh([r['strategy'] for r in vals], [r['break_even_round_trip_bps_per_trade'] for r in vals])
    plt.xlabel('Gross break-even total round-trip bps per trade')
    save('cost_frontier')
    for grouping in ['fold', 'year']:
        plt.figure(figsize=(10, 5))
        for name in ['long', 'momentum_0', 'reversal_0']:
            buckets = defaultdict(list)
            for r in groups[name]:
                buckets[str(r['fold']) if grouping == 'fold' else r['date'][:4]].append(r['net'])
            plt.plot(list(buckets), [np.mean(v) * 10000 for v in buckets.values()], marker='o', label=name)
        plt.ylabel('Mean net bps/session')
        plt.legend()
        save(grouping + '_comparison')
    plt.figure(figsize=(10, 5))
    curves = defaultdict(list)
    oos = {(r['symbol'], r['date']) for r in core}
    for f in features:
        if (f['symbol'], f['date']) not in oos:
            continue
        bars = valid[(f['symbol'], f['date'])]
        late = bars.filter(bars['bar_start_et'].dt.strftime('%H:%M') >= '15:30')
        curves['positive' if f['r_pre'] > 0 else 'negative'].append(
            np.array(late['close']) / f['cutoff_price'] - 1)
    for name, values in curves.items():
        plt.plot(np.arange(30), np.mean(values, axis=0) * 10000, label=name)
    plt.ylabel('Mean cumulative gross bps from cutoff proxy')
    plt.xlabel('Minutes after 15:30')
    plt.legend()
    save('conditional_time_of_day')
    plt.figure(figsize=(10, 5))
    for name in ['long', 'momentum_0', 'reversal_0']:
        x = np.cumprod(1 + np.array([r['net'] for r in groups[name]]))
        peak, duration, durations = 1, 0, []
        for value in x:
            peak = max(peak, value)
            duration = duration + 1 if value < peak else 0
            durations.append(duration)
        plt.plot(durations, label=name)
    plt.ylabel('Sessions since wealth peak')
    plt.legend()
    save('drawdown_duration')
