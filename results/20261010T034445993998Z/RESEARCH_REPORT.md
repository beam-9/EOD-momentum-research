# Research report

**NO_REAL_HISTORICAL_BACKTEST**

Missing credentials and licensed minute-bar files. No empirical profitability, trade logs, confidence intervals, or performance charts exist.
Empty tables are schema artifacts, not simulated zero-return results.

Target SPY/QQQ: 2023-01-03–2026-10-09. Real coverage: **none**.
Holdout: [2026-04-10, after latest completed session), sealed; never evaluated.
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
