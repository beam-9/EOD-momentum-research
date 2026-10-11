---
project: eod-momentum
stage_id: "STAGE_04"
stage_name: "Evidence review and next-stage decision"
report_date_utc: "2026-10-11T04:54:10.539573+00:00"
stage_status: "PASS"
empirical_verdict: "NOT_PROMISING"
real_historical_backtest_executed: true
holdout_2026_04_10_and_later_evaluated: false
repo_commit: "UNCOMMITTED_REPOSITORY"
run_ids: ["20261011T044241208535Z", "20261011T044703803065Z"]
protocol_hash: "b0ca75b6809a7a91aa23e31b6a7954c3f8aaa7b5b4d43b6f491037e0291315a3"
data_manifest_paths: ["data/manifests/underlying.json", "data/manifests/corporate_actions_2026-10-10.json"]
---

# Stage 04 — Evidence review and next-stage decision

## 1. Executive summary (5–8 sentences)

The objective was to assess the actual development evidence and select the next permitted step. Genuine bars, actions, auction samples and quote samples replaced the prior access blocker, and real development backtests were completed. All active candidates have negative mean net returns under the prescribed 3 bps per side proxy cost, making the observed result NOT_PROMISING. G3 fails and the other four robustness gates remain inconclusive. Software verification, independent reconciliation and exact analytical reproduction passed, but do not establish executable market fills. This decision memo meets Stage 04 reporting acceptance and is PASS as a reporting stage; no strategy passes promotion. Stop promotion and review methodology and missing execution evidence before deciding whether further Phase A work is justified.

## 2. Inputs and provenance

| Item | Actual source/path | Coverage/feed | Hash/manifest | Limitation |
|---|---|---|---|---|
| Raw bars | [data/processed/underlying.parquet](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/data/processed/underlying.parquet) | Alpaca explicit SIP/raw, 2023-01-03–2026-10-09; 1,608,254 bars | [data/manifests/underlying.json](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/data/manifests/underlying.json); SHA256 `435db3c8e69e96c5356a385c1941ac889a083d36ceaa0c66b186cfec5bfae2c5` | SDK response does not independently echo feed; finalized bars |
| Actions | [data/processed/corporate_actions_2026-10-10.csv](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/data/processed/corporate_actions_2026-10-10.csv) | 27 cash dividends; ex-dates through 2026-04-09 | [data/manifests/corporate_actions_2026-10-10.json](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/data/manifests/corporate_actions_2026-10-10.json) | Original publication/version times and independent exhaustiveness unknown |
| Official closes | [data/processed/development_official_closes_2026-10-10.json](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/data/processed/development_official_closes_2026-10-10.json) | 792 SPY / 777 QQQ primary-market condition-M mappings | [reports/evidence/20261011T043620658191Z_local02/official_close_catalog.json](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/evidence/20261011T043620658191Z_local02/official_close_catalog.json) | 27 / 42 missing of 819 sessions; mapping assumptions retained |
| Quote samples | [reports/evidence/20261011T043620658191Z_local02/quote_sample_audit.json](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/evidence/20261011T043620658191Z_local02/quote_sample_audit.json) | Six prespecified windows; 18,711 events | Raw payload hashes in audit | Small diagnostic sample, not fill calibration |
| Frozen protocol | [experiments/RESEARCH_PROTOCOL.md](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/experiments/RESEARCH_PROTOCOL.md) | Original protocol and registry unchanged | `b0ca75b6809a7a91aa23e31b6a7954c3f8aaa7b5b4d43b6f491037e0291315a3` | Original action path null; explicit overlay changes config digest |
| Runtime binding | [config/intake_2026-10-10.yaml](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/config/intake_2026-10-10.yaml) | Only corporate_actions_path differs | [reports/evidence/20261011T043620658191Z_local02/input_binding.json](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/evidence/20261011T043620658191Z_local02/input_binding.json) | EXPLORATORY_PROTOCOL_CHANGED; not exact frozen-config confirmation |

Credentials: PRESENT locally, omitted from artifacts. Minute-end plus 30 seconds is assumed availability, not observed receipt latency. Finalized bars and minute-open fills are **FILL_PROXY_ONLY**. Holdout begins 2026-04-10, remains **SEALED_NOT_ANALYZED**; only raw storage, hashes and coverage metadata include that period.

## 3. Changes made

| Path | Change | Why | Verification |
|---|---|---|---|
| scripts/stage02_intake.py | Explicit ignored local-env loader, preholdout probe, cached acquisition/audit | Secure reproducible intake | Ruff, compile and help check; authenticated execution |
| config/intake_2026-10-10.yaml; experiments/DATA_INTAKE_NOTE_2026-10-10.md | Authentic action input binding only | Apply existing exclusion logic without rewriting frozen lock | One-key diff and pre-outcome evidence |
| results/20261011T044241208535Z; results/20261011T044703803065Z | New immutable real-data run and reproduction artifacts | Empirical comparison and determinism | 13 identical analytical hashes |
| reports/stages; reports/PROJECT_STATUS.md; current-facing docs | Stage reports/status and honest limitations | Continuity | Frontmatter/headings/path/hash verification |

Research engine/model source and frozen original files remain unchanged. No new strategies or parameters were introduced.

## 4. Work executed (commands and observed results)

| Command | Exit | Artifact | Observed result |
|---|---|---|---|
| `PYTHONPATH=src .venv/bin/python scripts/stage02_intake.py --acquire` | 0 | [reports/evidence/20261011T043620658191Z_local02/access_and_acquisition.json](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/evidence/20261011T043620658191Z_local02/access_and_acquisition.json) | Authenticated preholdout probe and cached acquisition |
| `PYTHONPATH=src .venv/bin/python -m eod_momentum.cli --config config/intake_2026-10-10.yaml research run --phase A` | 0 twice | [results/20261011T044241208535Z/RESEARCH_REPORT.md](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/results/20261011T044241208535Z/RESEARCH_REPORT.md); reproduction `results/20261011T044703803065Z` | Genuine development WFA; reproduction is not a new strategy search |
| `.venv/bin/python scripts/verify.py --checks-only --output-dir reports/evidence/20261011T043620658191Z_local02/verification` | 0 | [reports/evidence/20261011T043620658191Z_local02/verification/commands.json](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/evidence/20261011T043620658191Z_local02/verification/commands.json) | 140 tests passed, no failures/errors/skips; Ruff, pip check and compile passed |
| Independent reconciliation and official-endpoint audit | 0 | [reports/evidence/20261011T043620658191Z_local02/independent_real_data_reconciliation.json](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/evidence/20261011T043620658191Z_local02/independent_real_data_reconciliation.json); [reports/evidence/20261011T043620658191Z_local02/official_endpoint_audit.json](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/evidence/20261011T043620658191Z_local02/official_endpoint_audit.json) | 16,520 trade records reconciled; development-only endpoint comparison |

Python 3.12.14, unchanged requirements.lock; full versions in [results/20261011T044241208535Z/environment_manifest.json](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/results/20261011T044241208535Z/environment_manifest.json). One upstream websockets deprecation warning. Supplement collectors and exact request reproduction are preserved in [reports/evidence/20261011T043620658191Z_local02/acquisition_reproduction.json](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/evidence/20261011T043620658191Z_local02/acquisition_reproduction.json). Sandbox networking initially failed without a provider response; approved network execution succeeded. Prior screenshot-derived HTTP401 evidence remains historical and was resolved by the local exact credential pair.

## 5. Empirical results — ONLY if real historical data was used

**Observed proxy-cost verdict: NOT_PROMISING; full robustness: INCONCLUSIVE.** All 28 active rule×ETF combinations have negative mean net returns at 3 bps/side; two flat controls are zero. No active candidate has a positive lower 95% mean confidence bound. This is historical research output, not observed broker profitability or losses.

1551 eligible development feature rows cover 2023-01-04–2026-04-09. Raw RTH audit excludes 17 symbol-sessions (eight early closes per ETF, plus SPY 2023-06-05 missing four minutes); feature generation excludes another 70 rows for prior-session/action conditions. No missing minutes were imputed. Of eight planned folds per ETF, SPY executes folds 1/4/5 and skips five; QQQ executes 1/2/3/4/5 and skips three. The original 95% coverage condition is unchanged. Fold 0 training coverage is 0.947791, below 0.95. Calendar-denominator and legitimate exclusions reduce coverage; this policy must be reviewed separately without outcome-driven relaxation.

**Actual OOS dates: 2024-07-08–2025-10-02, with gaps; SPY 180, QQQ 297, union 300, common 177.** The planned April 2024 first test did not execute. Full half-open train/validation/test boundaries and statuses are in [results/20261011T044241208535Z/walk_forward_folds.csv](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/results/20261011T044241208535Z/walk_forward_folds.csv). Executed folds retain rolling 12/3/3 calendar months and past-validation-only threshold selection. SPY has fewer than the 200-session guide; selected SPY momentum/reversal have 47/53 trades, below the 100-trade guide.

At the primary 3 bps/side cost, with zero additional commission as configured:

| ETF | Rule | OOS sessions | Trades | Gross bps/session | Net bps/session | Net mean 95% CI (bps) |
|---|---|---:|---:|---:|---:|---|
| SPY | flat | 180 | 0 | 0.000 | 0.000 | [0.000, 0.000] |
| SPY | long | 180 | 180 | 0.712 | -5.288 | [-8.857, -1.679] |
| SPY | short | 180 | 180 | -0.712 | -6.712 | [-10.321, -3.143] |
| SPY | momentum_0 | 180 | 180 | -0.626 | -6.626 | [-10.676, -2.688] |
| SPY | momentum_0.0025 | 180 | 124 | -1.148 | -5.282 | [-9.321, -1.691] |
| SPY | momentum_0.005 | 180 | 84 | -0.956 | -3.756 | [-7.461, -0.407] |
| SPY | momentum_0.0075 | 180 | 58 | -1.440 | -3.373 | [-6.971, -0.194] |
| SPY | momentum_0.01 | 180 | 42 | -0.832 | -2.232 | [-5.413, 0.867] |
| SPY | momentum_selected | 180 | 47 | -1.602 | -3.169 | [-6.752, -0.083] |
| SPY | reversal_0 | 180 | 180 | 0.626 | -5.374 | [-9.312, -1.324] |
| SPY | reversal_0.0025 | 180 | 124 | 1.148 | -2.985 | [-6.584, 0.937] |
| SPY | reversal_0.005 | 180 | 84 | 0.956 | -1.844 | [-5.207, 1.686] |
| SPY | reversal_0.0075 | 180 | 58 | 1.440 | -0.494 | [-3.700, 2.815] |
| SPY | reversal_0.01 | 180 | 42 | 0.832 | -0.568 | [-3.697, 2.249] |
| SPY | reversal_selected | 180 | 53 | 0.670 | -1.097 | [-4.202, 1.850] |
| QQQ | flat | 297 | 0 | 0.000 | 0.000 | [0.000, 0.000] |
| QQQ | long | 297 | 297 | 1.090 | -4.910 | [-8.167, -1.667] |
| QQQ | short | 297 | 297 | -1.090 | -7.090 | [-10.333, -3.833] |
| QQQ | momentum_0 | 297 | 297 | -2.210 | -8.210 | [-11.527, -4.858] |
| QQQ | momentum_0.0025 | 297 | 221 | -1.749 | -6.214 | [-9.289, -3.155] |
| QQQ | momentum_0.005 | 297 | 176 | -1.203 | -4.759 | [-7.798, -1.933] |
| QQQ | momentum_0.0075 | 297 | 132 | -1.106 | -3.773 | [-6.631, -1.109] |
| QQQ | momentum_0.01 | 297 | 101 | -0.793 | -2.833 | [-5.229, -0.657] |
| QQQ | momentum_selected | 297 | 109 | -0.917 | -3.119 | [-5.598, -0.934] |
| QQQ | reversal_0 | 297 | 297 | 2.210 | -3.790 | [-7.142, -0.473] |
| QQQ | reversal_0.0025 | 297 | 221 | 1.749 | -2.716 | [-5.686, 0.341] |
| QQQ | reversal_0.005 | 297 | 176 | 1.203 | -2.352 | [-5.161, 0.613] |
| QQQ | reversal_0.0075 | 297 | 132 | 1.106 | -1.561 | [-4.145, 1.234] |
| QQQ | reversal_0.01 | 297 | 101 | 0.793 | -1.247 | [-3.385, 1.048] |
| QQQ | reversal_selected | 297 | 137 | 1.062 | -1.705 | [-4.041, 0.923] |

Source: [results/20261011T044241208535Z/metrics.json](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/results/20261011T044241208535Z/metrics.json). 95% intervals use the prescribed five-date circular block bootstrap, 2000 replicates, seed2049. Flat-day means differ from mean per trade. Full expectancy per trade, compounded returns, win/loss payoffs, drawdowns and tail losses are stored for every strategy/cost in that file; none are omitted from the underlying comparison.

Artifacts retain 120 metric rows (15 rules × two ETFs × four costs), 28,620 daily rows and 16,520 trade records **across alternative strategies and cost scenarios**, not independent fills. [results/20261011T044241208535Z/execution_cost_frontier.csv](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/results/20261011T044241208535Z/execution_cost_frontier.csv) retains 0/1/3/5 bps per side. [results/20261011T044241208535Z/stress_tests.csv](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/results/20261011T044241208535Z/stress_tests.csv) retains 1140 prescribed timing, 6/9-bps friction and best-1/best-5 removal scenarios. Fold/year/regime details: [results/20261011T044241208535Z/stratified.csv](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/results/20261011T044241208535Z/stratified.csv); paired baseline lifts: [results/20261011T044241208535Z/baseline_comparisons.csv](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/results/20261011T044241208535Z/baseline_comparisons.csv); dependence-preserving joint-date inference: [results/20261011T044241208535Z/joint_date_bootstrap.json](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/results/20261011T044241208535Z/joint_date_bootstrap.json). The 100 fixed-seed random-direction controls in [results/20261011T044241208535Z/null_controls.csv](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/results/20261011T044241208535Z/null_controls.csv) are diagnostics, not independent discoveries. Eight generated charts use proxy labels. DSR/PBO are NOT_ESTIMABLE; probability/options/IBS empirical studies were NOT RUN.

The predictive bar-close endpoint in [results/20261011T044241208535Z/predictive.json](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/results/20261011T044241208535Z/predictive.json) is separate from 15:32→15:58 open-price fill-proxy returns. Supplemental official endpoint comparison on 179 SPY / 297 QQQ OOS dates leaves features and trade returns unchanged: mean absolute official-minus-minute endpoint differences are 1.640 / 1.108 bps; HAC official slope p-values are approximately 0.426 / 0.861 ([reports/evidence/20261011T043620658191Z_local02/official_endpoint_audit.json](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/evidence/20261011T043620658191Z_local02/official_endpoint_audit.json)). These incomplete catalog subsets and mapping assumptions cannot establish executable auction fills or replace the frozen previous-close proxy.

## 6. Verification and research integrity

All 16,520 signed trade returns, both-side friction, commissions and net returns independently reconcile (maximum absolute recorded errors zero). Thirty-two source-price/timing samples span both ETFs, signs and costs; source rows were filtered to development before collection. Thirty canonical-event versus independent-screening cases pass at 1e-12. No duplicate OOS rows; strict decision/order/fill chronology checked; 1176 hash-linked ledger records verified. All unsuccessful candidates remain retained.

Unchanged reproduction run `results/20261011T044703803065Z` matches 13 deterministic analytical artifact hashes exactly ([reports/evidence/20261011T043620658191Z_local02/reproducibility.json](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/evidence/20261011T043620658191Z_local02/reproducibility.json)); timestamps/manifests are intentionally not asserted identical. No engine semantics, models, thresholds, cost grid, seeds, original config, protocol, registry or lock were changed. [experiments/DATA_INTAKE_NOTE_2026-10-10.md](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/experiments/DATA_INTAKE_NOTE_2026-10-10.md) was recorded before outcomes and documents the sole input-path binding. Results are honestly EXPLORATORY_PROTOCOL_CHANGED rather than exact frozen-config confirmation. Prior no-data/401 reports remain preserved.

Holdout: **SEALED; no outcome analysis and no authorization to consume it**. No freeze/evaluate command, production seal or consumed marker was created. Raw holdout acquisition does not imply evaluation. Unknown historical bar revisions/receipts and independently exhaustive action history prevent a blanket no-look-ahead certification. Independent audits found no implementation chronology violations within the tested development paths.

## 7. Robustness gates (NOT the same as stage status)

| Gate | Status | Evidence | Remaining requirement |
|---|---|---|---|
| G1 Data | INCONCLUSIVE | [reports/evidence/20261011T043620658191Z_local02/development_quality.json](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/evidence/20261011T043620658191Z_local02/development_quality.json) | Receipts, revisions, exhaustive actions and official-close coverage |
| G2 Leakage/trials | INCONCLUSIVE | [reports/evidence/20261011T043620658191Z_local02/independent_real_data_reconciliation.json](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/evidence/20261011T043620658191Z_local02/independent_real_data_reconciliation.json) | Input-binding variance and limited coverage; untouched final holdout |
| G3 Economic net edge | FAIL | [results/20261011T044241208535Z/metrics.json](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/results/20261011T044241208535Z/metrics.json) | No positive net mean among active rules at prescribed 3 bps/side |
| G4 Stability | INCONCLUSIVE | [results/20261011T044241208535Z/stress_tests.csv](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/results/20261011T044241208535Z/stress_tests.csv) | Sparse/skipped folds; no prospective or observed latency evidence |
| G5 Deployability | INCONCLUSIVE | [DATA_ACCESS_BLOCKERS.md](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/DATA_ACCESS_BLOCKERS.md) | Representative executable quotes, broker costs, parity and prospective evidence |

The generated scorecard's generic G2 wording still says genuine WFA is required. Genuine WFA has now run; that wording does not negate the run. G2 remains INCONCLUSIVE for the specific limitations above. Original generated artifacts are preserved.

## 8. Blockers, decisions and next actions

| Priority | Blocker or decision | Who can resolve | Exact next action |
|---|---|---|---|
| P0 | Stop strategy promotion: prescribed-cost evidence is unfavorable | Research owner | Retain all results; do not search additional strategies or consume holdout |
| P1 | Coverage denominator/exclusion policy and null action-path binding | Research owner with protocol review | Review documented rules and predeclare any treatment before future economic runs; preserve this exploratory run |
| P1 | Receipt/revision/action completeness and official-close gaps | Data owner/vendor | Obtain existing authorized timestamped revisions, independent action coverage and missing primary-close records, or retain UNKNOWN |
| P1 | Fill evidence not calibrated | Data owner/vendor | Supply representative licensed NBBO event/receipt/size/condition history around entry/exit and historical applicable costs; do not purchase automatically |

**Recommended next stage:** a methodology and execution-evidence review deciding whether to stop/reframe Phase A. No new credentials or GitHub setup are needed now. The exact owner action is to review the coverage/input-binding decisions; provide additional existing licensed execution evidence only if further Phase A validation is warranted.  
**Do NOT proceed to:** holdout evaluation, additional strategy optimization, GEX/options expansion, TradingView or live trading until a separately authorized protocol and the required gates support it. Current G3 failure means there is no basis for promotion.

## 9. Artifacts to provide for ChatGPT review

- [reports/PROJECT_STATUS.md](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/PROJECT_STATUS.md)
- [reports/stages/STAGE_04_EVIDENCE_REVIEW_2026-10-10_LOCAL_ENV.md](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/stages/STAGE_04_EVIDENCE_REVIEW_2026-10-10_LOCAL_ENV.md)
- [results/20261011T044241208535Z/RESEARCH_REPORT.md](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/results/20261011T044241208535Z/RESEARCH_REPORT.md)
- [results/20261011T044241208535Z/robustness_scorecard.csv](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/results/20261011T044241208535Z/robustness_scorecard.csv)
- [DATA_ACCESS_BLOCKERS.md](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/DATA_ACCESS_BLOCKERS.md)
- [reports/evidence/20261011T043620658191Z_local02/verification/pytest.xml](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/evidence/20261011T043620658191Z_local02/verification/pytest.xml)
- [reports/evidence/20261011T043620658191Z_local02/independent_real_data_reconciliation.json](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/evidence/20261011T043620658191Z_local02/independent_real_data_reconciliation.json)
- [reports/evidence/20261011T043620658191Z_local02/reproducibility.json](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/evidence/20261011T043620658191Z_local02/reproducibility.json)

Raw licensed payloads and credential values are not part of a public review bundle.
