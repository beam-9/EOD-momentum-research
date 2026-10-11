import numpy as np
from scipy.stats import norm


def block_bootstrap(values, *, samples=2000, block=5, seed=2049):
    """Rows are distinct ordered dates; columns retain cross-asset dependency."""
    if samples <= 0 or block <= 0:
        raise ValueError('Bootstrap samples/block must be positive')
    x = np.asarray(values, dtype=float)
    if x.ndim == 1:
        x = x[:, None]
    n = len(x)
    if n < max(20, 2 * block):
        return {'status': 'NOT_ESTIMABLE', 'reason': 'Too few independent dates', 'n_dates': n}
    if not np.isfinite(x).all():
        raise ValueError('Nonfinite bootstrap input')
    rng = np.random.default_rng(seed)
    # Equal committed capital per instrument; no independent ticker-row sampling.
    means, sharpes = [], []
    for _ in range(samples):
        starts = rng.integers(0, n, size=int(np.ceil(n / block)))
        idx = ((starts[:, None] + np.arange(block)) % n).ravel()[:n]
        draw = x[idx].mean(axis=1)
        means.append(draw.mean())
        sd = draw.std(ddof=1)
        sharpes.append(draw.mean() / sd * np.sqrt(252) if sd > 0 else np.nan)
    finite = np.asarray(sharpes)[np.isfinite(sharpes)]
    return {'status': 'COMPUTED', 'n_dates': n, 'block': block, 'samples': samples, 'seed': seed,
            'mean_ci95': np.quantile(means, [0.025, 0.975]).tolist(),
            'sharpe_ci95': np.quantile(finite, [0.025, 0.975]).tolist() if len(finite) else None}


def metrics(rows):
    if not rows:
        return {'status': 'NO_OBSERVATIONS', 'sessions': 0, 'trades': 0}
    x = np.array([r['net'] for r in rows])
    g = np.array([r['gross'] for r in rows])
    active = np.array([bool(r['q']) for r in rows])
    trades = x[active]
    wealth = np.r_[1, np.cumprod(1 + x)]
    peak = np.maximum.accumulate(wealth)
    dd = wealth / peak - 1
    duration = longest = runloss = maxloss = 0
    for ret, d in zip(x, dd[1:]):
        duration = duration + 1 if d < -1e-14 else 0
        longest = max(longest, duration)
        runloss = runloss + 1 if ret < 0 else 0
        maxloss = max(maxloss, runloss)
    sd = x.std(ddof=1) if len(x) > 1 else 0
    downside = np.sqrt(np.mean(np.minimum(x, 0) ** 2))
    loss_sum = -trades[trades < 0].sum()
    q5 = float(np.quantile(x, 0.05))
    return {'status': 'COMPUTED', 'sessions': len(x), 'trades': int(active.sum()),
            'no_trade_sessions': int((~active).sum()), 'longs': sum(r['q'] > 0 for r in rows),
            'shorts': sum(r['q'] < 0 for r in rows), 'traded_fraction': float(active.mean()),
            'mean_gross_session': float(g.mean()), 'mean_net_session': float(x.mean()),
            'median_net_session': float(np.median(x)),
            'mean_net_trade': float(trades.mean()) if len(trades) else None,
            'median_net_trade': float(np.median(trades)) if len(trades) else None,
            'win_rate': float((trades > 0).mean()) if len(trades) else None,
            'avg_win': float(trades[trades > 0].mean()) if (trades > 0).any() else None,
            'avg_loss': float(trades[trades < 0].mean()) if (trades < 0).any() else None,
            'profit_factor': float(trades[trades > 0].sum() / loss_sum) if loss_sum > 0 else None,
            'sharpe_252_including_flat_days': float(x.mean() / sd * np.sqrt(252)) if sd else None,
            'sortino_252': float(x.mean() / downside * np.sqrt(252)) if downside else None,
            'max_drawdown': float(dd.min()), 'max_drawdown_duration_sessions': longest,
            'current_drawdown_duration_sessions': duration, 'worst_consecutive_loss_sessions': maxloss,
            'worst_session': float(x.min()), 'q05': q5,
            'cvar05': float(x[x <= q5].mean()), 'q01': float(np.quantile(x, 0.01)),
            'compounded_return': float(wealth[-1] - 1), 'turnover_units': int(2 * active.sum()),
            'slippage_total_return_units': sum(r['slippage'] for r in rows),
            'commission_total_return_units': sum(r['fees'] for r in rows),
            'exposure_fraction_of_rth': sum(r['exposure_minutes'] for r in rows) / (390 * len(rows)),
            'break_even_round_trip_bps_per_trade': float(g.sum() / active.sum() * 10000)
            if active.sum() else None}


def hac_regression(x, y, lag=5):
    x, y = np.asarray(x), np.asarray(y)
    if len(x) < 30 or np.std(x) == 0:
        return {'status': 'NOT_ESTIMABLE'}
    design = np.column_stack([np.ones(len(x)), x])
    inverse = np.linalg.pinv(design.T @ design)
    beta = inverse @ design.T @ y
    score = design * (y - design @ beta)[:, None]
    meat = score.T @ score
    for k in range(1, min(lag, len(x) - 1) + 1):
        cross = score[k:].T @ score[:-k]
        meat += (1 - k / (lag + 1)) * (cross + cross.T)
    se = np.sqrt(np.maximum(np.diag(inverse @ meat @ inverse), 0))
    return {'status': 'COMPUTED', 'intercept': float(beta[0]), 'slope': float(beta[1]),
            'slope_hac_se': float(se[1]), 'lag': lag,
            'p_value_normal_approx': float(2 * norm.sf(abs(beta[1] / se[1]))) if se[1] else None,
            'interpretation': 'Predictability of bar-close proxy, not executable profitability'}


def multiplicity(n_dates, variants):
    return {'DSR': {'status': 'NOT_ESTIMABLE', 'reason': 'Effective independent trial count not established'},
            'PBO': {'status': 'NOT_ESTIMABLE', 'reason': 'No prespecified independent CSCV partitions'},
            'n_dates': n_dates, 'deterministic_variants': variants,
            'warning': 'All variants and stresses disclosed. Intervals are unadjusted exploratory intervals; '
                       'dependent parameter search is not independent confirmation.'}
