# Implementation and evidence status

**Current update — 2026-10-10 local:** Credentials PRESENT locally and authenticated SIP access succeeds. 1,608,254 genuine raw bars are retained; real Phase A WFA executed in `results/20261011T044241208535Z` with exact 13-artifact reproduction. All 28 active rule/ETF combinations have negative mean net returns at 3 bps/side. 140 tests, lint, dependency and compilation checks passed; trade reconciliation passed. G3 FAIL; G1/G2/G4/G5 INCONCLUSIVE. Holdout remains SEALED. See [reports/PROJECT_STATUS.md](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/PROJECT_STATUS.md), [reports/stages/STAGE_03_PHASE_A_DEVELOPMENT_2026-10-10_LOCAL_ENV.md](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/stages/STAGE_03_PHASE_A_DEVELOPMENT_2026-10-10_LOCAL_ENV.md) and [reports/stages/STAGE_04_EVIDENCE_REVIEW_2026-10-10_LOCAL_ENV.md](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/stages/STAGE_04_EVIDENCE_REVIEW_2026-10-10_LOCAL_ENV.md).

**Remaining limitations:** Raw history access is resolved. Twenty-seven cash dividends and partial official-close catalogs were acquired; exhaustive action/publication history, missing official closes, bar receipt/revision times and representative executable quote/arrival/size/cost evidence remain unavailable. Six quote windows are diagnostics, not calibrated fills. Corporate-action path is an explicitly disclosed exploratory overlay; original lock unchanged. Three SPY/five QQQ folds passed the unchanged coverage rule. The owner should review methodology/evidence and whether to stop Phase A; no further secrets, purchases or GitHub setup are needed. No new strategies, holdout evaluation, TradingView or live trading are authorized by these results.

**Historical baseline and prior attempts below:** Statements of no real history/tests below describe earlier finalized stages, superseded by this dated update; retained for continuity.


**Definitive status: `NO_REAL_HISTORICAL_BACKTEST`.** This document separates working software from empirical evidence. Dependencies are installed locally in `.venv`; `requirements.lock` pins the replay environment. The authoritative specification is preserved in `experiments/HANDOFF_v3.md`.

| Area | Implemented | Evidence / remaining limitation |
| --- | --- | --- |
| Phase A access/storage | Official read-only Alpaca SDK adapter, monthly cache/retries, licensed CSV/Parquet import, UTC normalization, Polars/Parquet/DuckDB checks and hashes | Access check ran; no complete credential pair, no raw history, entitlement unverified |
| Calendar/quality | XNYS session and DST handling, early-close exclusions, expected-minute and invalid-price checks | Synthetic/unit verification only; real coverage and exclusions unmeasured |
| Features/execution | As-of cutoff feature, separate predictive/execution endpoints, event-driven entry/exit chronology, conservative quote validation and hand/reference reconciliation | Fixtures establish software behavior; finalized bars/minute-open fills remain proxies and actual arrival timing unvalidated |
| Rules/trials | 15 preregistered rules: 13 fixed plus two selected; append-only hash-linked run trials, config/protocol/code manifests | No outcome trials on real data; all unsuccessful experiments must remain retained |
| Validation/inference | Rolling nested 12/3/3 month split, validation-only selection, nonoverlapping OOS dates, block bootstrap, HAC endpoint, paired-date ETF comparison, null/cost/timing/outlier diagnostics | No genuine WFA, bootstrap inference or statistical superiority conclusion |
| Final holdout | Fixed 2026-04-10 boundary, freeze hashes/rule, one-use consumed marker | Sealed, not evaluated; requires sufficient genuine development evidence |
| Reports/charts | Run directories, trade/signal schemas, proposed folds, report and scorecard; chart generation when genuine observations exist | Current missing-data outputs are explicit placeholders, not performance results |
| GEX/options | Sign/unit/as-of checks, option import schema, chain eligibility, ATM selection, bid/ask P&L utility | Isolated utilities only; complete empirical Phase B/C runners gated by inputs and separately frozen protocol |
| IBS | Independent fixed-rule ETF runner, causal prefix/ATR, overnight MTM, gap/financing marks, open losses, delayed decision/fill books and scenario ledger | Software fixture-tested; no genuine ETF history run, CFD or intraday margin validation |
| TradingView | Promotion gates documented | No indicator/strategy export; no validated rule, parity, live-feed or repaint evidence |

## What to verify and reproduce

Run the commands in `README.md` from the project root. The test suite checks malformed data rejection, calendar/timestamp invariants, event chronology, controlled fills/returns, reference parity, splits/holdout protections and later-phase utility behavior. Test counts and detailed failures belong to the generated `results/verification/pytest.xml` and the final execution summary; this document does not assert a stale count while tests evolve. Fixtures are not economic evidence. Ruff checks syntax/style and cannot establish absence of trading bias.

`replay` with missing real history completes the reporting path, records every candidate as blocked and produces no performance plots. Proposed folds are **not executed folds**. With real data, `research run --phase A` conducts the development analysis while excluding holdout rows from feature/outcome processing. `research validate` prints an existing scorecard; it is not an independent full audit and does not promote a candidate.

## Frozen planned boundaries

Target data: 2023-01-03 through the latest completed session (2026-10-09 initially). Development ends before 2026-04-10. Folds use half-open intervals: initial training 2023-01-03 to 2024-01-03, validation to 2024-04-03, first outer test to 2024-07-03, rolling quarterly. Last complete planned outer test ends 2026-04-03; remaining preholdout dates are not silently added as a partial test. Holdout is 2026-04-10 through the frozen last completed session and is never a tuning set. No real training, validation, OOS or final-holdout dates have actually been analyzed.

## Outstanding evidence and implementation gates

The no-data path, infrastructure and test fixtures are deliverable engineering work, not a completed empirical study. Genuine historical acquisition, session audit, all model/cost comparisons, complete historical execution reconciliation, out-of-sample uncertainty and final holdout remain unexecuted. Corporate-action history, official closes, quote/arrival validation and receipt/version provenance are needed for stronger execution and leakage evidence. The scorecard conservatively keeps every promotion gate inconclusive; even genuine bars alone would not justify deployment.

Phase B/C helpers require fit-for-purpose datasets, a frozen protocol, full empirical orchestration and new integration verification. Phase D has fixed-rule orchestration and a separate protocol, but no genuine historical execution. DSR/PBO and calibrated probability remain unvalidated/`NOT_ESTIMABLE`, rather than manufactured. Full CFD financing/contract/margin replication and paper-forward evidence are absent. No purchases or live broker integration occurred, and GitHub is optional. `DATA_ACCESS_BLOCKERS.md` specifies the exact inputs needed to advance.

## Phase D implementation update

The independent ETF IBS runner is now implemented (`research run --phase D`) with available-prefix checks, prior ATR, cash constraints, chronological overnight book, ACT/365 financing assumption, gap exposure, open-position MTM, decision/fill lag scenarios, hash-chained scenario trials and output charts when eligible data exists. It has fixture tests, but **no empirical run**. B/C remain data-gated utilities/interfaces; no full historical GEX or option P&L conclusion is supported.

## Completed verification

129 tests passed, 0 failed; lint, editable package install, dependency consistency and byte compilation passed. See FINAL_REPORT.md and results/verification/pytest.xml. No empirical performance was computed.
