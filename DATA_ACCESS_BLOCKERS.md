# Data-access blockers

**Architecture maintenance — Stage05, 2026-10-10 local:** 195 tests and lint/dependency/compile checks PASS. Independent Standards/Spec reviews resolved all six initial findings with zero new actionable findings. Intake is import-safe, credential state is restored, future dataset versions retain immutable provenance, and Git publication guards exclude secrets/restricted data. The authorized best-trade diagnostic correction is documented in [Erratum001](experiments/ERRATUM_001_DROP_BEST_TRADES.md); affected historical stress rows are not corrected evidence. No economic rerun occurred. Original data, results, frozen protocol and sealed holdout are preserved. See [Stage05 report](reports/stages/STAGE_05_ARCHITECTURE_AND_PUBLICATION_2026-10-10.md) and [current status](reports/PROJECT_STATUS.md).

**Current update — 2026-10-10 local:** Credentials PRESENT locally and authenticated SIP access succeeds. 1,608,254 genuine raw bars are retained; real Phase A WFA executed in `results/20261011T044241208535Z` with exact 13-artifact reproduction. All 28 active rule/ETF combinations have negative mean net returns at 3 bps/side. 140 tests, lint, dependency and compilation checks passed; trade reconciliation passed. G3 FAIL; G1/G2/G4/G5 INCONCLUSIVE. Holdout remains SEALED. See [reports/PROJECT_STATUS.md](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/PROJECT_STATUS.md), [reports/stages/STAGE_03_PHASE_A_DEVELOPMENT_2026-10-10_LOCAL_ENV.md](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/stages/STAGE_03_PHASE_A_DEVELOPMENT_2026-10-10_LOCAL_ENV.md) and [reports/stages/STAGE_04_EVIDENCE_REVIEW_2026-10-10_LOCAL_ENV.md](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/stages/STAGE_04_EVIDENCE_REVIEW_2026-10-10_LOCAL_ENV.md).

**Remaining limitations:** Raw history access is resolved. Twenty-seven cash dividends and partial official-close catalogs were acquired; exhaustive action/publication history, missing official closes, bar receipt/revision times and representative executable quote/arrival/size/cost evidence remain unavailable. Six quote windows are diagnostics, not calibrated fills. Corporate-action path is an explicitly disclosed exploratory overlay; original lock unchanged. Three SPY/five QQQ folds passed the unchanged coverage rule. The owner should review methodology/evidence and whether to stop Phase A; no further secrets, purchases or GitHub setup are needed. No new strategies, holdout evaluation, TradingView or live trading are authorized by these results.

**Historical baseline and prior attempts below:** Statements of no real history/tests below describe earlier finalized stages, superseded by this dated update; retained for continuity.


**Status: `NO_REAL_HISTORICAL_BACKTEST`.** Target SPY/QQQ raw one-minute history is 2023-01-03 through 2026-10-09, extending only to the latest fully completed exchange session on later runs. Genuine acquired coverage is **none**. There are no empirical trade counts, returns, excluded-session counts, confidence intervals or cost-frontier estimates to report.

## Access actually checked

`data/manifests/access_check.json` records no complete supported environment credential pair and no `data/processed/underlying.parquet`. No local SPY/QQQ minute history was found during the workspace preflight. `data check --probe` recorded `NOT_SENT_MISSING_CREDENTIALS` and `feed_entitlement: UNVERIFIED`. An absent credential is not proof of vendor unavailability, license eligibility or rejected entitlement. No secret values are stored.

## Phase A: required acquisition

1. Existing authorized historical-data credentials, or licensed local files, for raw SPY and QQQ minute-start UTC OHLCV over the target period. Default provider is Alpaca, requested feed SIP. Actual earliest/latest bars and returned feed must be verified. IEX is a separately qualified research dataset, not equivalent consolidated volume or executable NBBO.
2. Complete timestamp/source/feed/adjustment provenance, retrieval dates and immutable raw-file hashes. Historical final bars are insufficient to prove original publication timing: actual first-receipt and revision/version timestamps are needed to validate latency assumptions. Current minute-end-plus-30-second availability is modeled.
3. Historical splits/distributions and the price treatment for every relevant date. Configure an authenticated `corporate_actions_path` CSV with `symbol,date,kind`; known action dates are excluded under the frozen raw-price protocol. Missing actions block G1; they are not silently assumed absent.
4. Official previous regular-session auction closes and an identified official cutoff-to-auction research endpoint. Current 15:59 minute-close values are labeled proxies and cannot establish official-auction parity.
5. Representative underlying NBBO with quote event/receipt times, bid/ask prices and sizes, feed, correction rules, coverage around order arrival and the scheduled close-period exit. Current minute-open fills and additive friction are stressable proxies; they do not prove realized spread, slippage, executable size or broker fill quality. Stock borrow availability/fees and capital assumptions require further evidence for deployable short execution.

The public software can be installed and tested without these inputs. The data fetcher is read-only. No subscriptions, purchases, paid jobs, broker account changes or order permissions were requested. Costs/entitlements require confirmation by the data owner/vendor; this project makes no price or licensing promises.

## Phase B: historical GEX

Missing: point-in-time historical chains, prior-night OI with effective publication dates, Greeks/IV with construction details, spot snapshots, contract multipliers and liquidity denominators available at decision time. Dealer inventory signs are assumptions requiring explicit alternate conventions; OI does not observe dealer inventory. GEX/sign/unit/as-of utilities exist, but the empirical phase runner and separately frozen protocol are gated. No GEX series or performance is invented.

## Phase C: 0DTE options

Missing: historical listed contract definitions, OCC/root identifiers, strikes/expiries, exercise/settlement conventions, multipliers, chain availability history, executable NBBO and sizes at entry/exit, receipt/correction times and fees. SPX/SPXW needs its own verified settlement and contract treatment. Databento OPRA/Cboe or another licensed dataset may be suitable only after actual coverage and rights are verified. Import currently stores supplied option snapshots as **unvalidated**. ATM selection and conservative bid/ask utilities do not constitute a historical options backtest. Underlying P&L is never substituted for option P&L.

## Phase D: IBS and genuine CFD replication

The independent ETF-proxy runner and its separate protocol are implemented. A real run needs authentic intraday ranges as of each decision, prior completed ATR history, corporate actions, overnight marks and financing assumptions. Without underlying history the CLI writes a no-data Phase D report. Daily marks cannot validate intraday margin breaches.

Exact US100/US30/US500/JP225 broker replication additionally needs the identified broker's authentic 2016–2026 quotes/trades, historical spreads, point/lot values, contract changes, financing/swap schedules, initial/maintenance margin, forced-liquidation rules and session calendars. ETF/index data is a labeled proxy only. For Tokyo cash proxies, close is 15:00 JST through 2024-11-01 and 15:30 from 2024-11-05; the later 15:25–15:30 collection window is not continuous-market execution. A CFD must use its actual sessions and fill behavior.

## Deployment remains blocked

All five robustness gates are unresolved with absent data. Probabilities are unvalidated; DSR/PBO are `NOT_ESTIMABLE`; no holdout has been consumed. Pine live-input support, non-repainting and Python/Pine parity would require new evidence after research passes. GitHub setup does not remove any of these blockers. Acquire authorized inputs, run the documented Phase A sequence, inspect full losing/winning results and preserve the sealed holdout before considering later phases.

## Phase D implementation update

The independent ETF IBS runner is now implemented (`research run --phase D`) with available-prefix checks, prior ATR, cash constraints, chronological overnight book, ACT/365 financing assumption, gap exposure, open-position MTM, decision/fill lag scenarios, hash-chained scenario trials and output charts when eligible data exists. It has fixture tests, but **no empirical run**. B/C remain data-gated utilities/interfaces; no full historical GEX or option P&L conclusion is supported.

## Next-stage access reverification — 2026-10-09 America/Vancouver

Current resume authority: [reports/PROJECT_STATUS.md](reports/PROJECT_STATUS.md).
Versioned evidence: `reports/evidence/20261010T044931128515Z/access_check.json` and
`data_access_command.json`. The command returned exit 2: all supported credential
variables ABSENT, no local processed bars, `NOT_SENT_MISSING_CREDENTIALS`; entitlement
remains UNVERIFIED. No provider request or historical backtest occurred. Previous
access and result manifests were preserved. Candidate local Pine CSVs are diagnostic
exports, not a licensed canonical raw minute-history dataset.

**Next action from the data owner:** configure an existing authorized complete
`APCA_API_KEY_ID` / `APCA_API_SECRET_KEY` pair in the local runtime environment
(or the complete supported ALPACA aliases), then resume Stage 02. Never send the
values in chat. The CLI does not load `.env` automatically. Alternatively provide
the absolute path to licensed raw SPY/QQQ minute OHLCV CSV/Parquet with source,
actual feed, UTC minute-start convention, adjustment policy and usage provenance.
Requested coverage remains 2023-01-03 through completed XNYS session 2026-10-09.
No purchase, trading permission or GitHub repository is needed for this step.

Corporate actions require authenticated `symbol,date,kind` split/distribution
history. The frozen config's `corporate_actions_path: null` is an intake ambiguity:
setting a real path changes its digest and currently labels the run exploratory.
Document provenance-only config treatment before empirical analysis; do not silently
rewrite the lock. Missing actions never mean no actions. Official auction/previous
closes, NBBO with event/receipt times and sizes, and bar revision/receipt evidence
remain separately unverified. All robustness gates remain INCONCLUSIVE, and the
2026-04-10 holdout remains SEALED.

## Stage 02 resumption — 2026-10-10 America/Vancouver

The user clarified that credentials were only supplied in an image, not configured
locally. Authorized ephemeral OCR-assisted read-only use reached Alpaca for SPY/QQQ
raw SIP history on **2024-03-08** and received **HTTP 401 Unauthorized**. No bars
were returned. Evidence: `reports/evidence/20261011T035339523222Z_resume02/authenticated_probe.json`. This is authentication
failure for the attempted values; image transcription error remains possible. It
is **not** proof of SIP entitlement denial. No IEX fallback, purchase or order occurred.

**Exact next owner action:** configure the exact active pair as local supported
environment variables, or place it in a local ignored `.env` and provide its path
only. Do not send secret values in chat. Existing CLI does not auto-load `.env`.
Then retry the same pre-holdout SIP probe. Full acquisition and Stage 03 are NOT RUN.
Corporate-action history and frozen-null path treatment, official previous/auction
closes, NBBO and receipt/revision evidence remain unresolved. Holdout since
2026-04-10 stays sealed; all gates remain INCONCLUSIVE. See reports/PROJECT_STATUS.md.
