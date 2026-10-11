# Research report

**INCONCLUSIVE_RESEARCH_ONLY**

Primary SPY; QQQ secondary. 1551 eligible development features; 300 distinct
OOS dates. All 15 rules retained, including no-trade/negative variants. Costs 0/1/3/5 bps per side;
6/9 bps and timing/outlier stresses are diagnostic. Performance is stored in metrics.json and
all OOS daily records in daily_pnl.csv; selection evidence in model_ledger.csv.

Holdout [2026-04-10, after 2026-10-09) remains sealed. No final winner claim.
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
