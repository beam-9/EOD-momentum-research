# EOD Momentum — Project Status

**Updated UTC:** 2026-10-11T04:54:10.539573+00:00; local work date 2026-10-10.  
**Last completed stage/status:** Stage 04 PASS (decision/report); Stage 03 PARTIAL; Stage 02 PARTIAL.  
**Real historical data available:** YES; Alpaca explicitly requested SIP/raw; 1,608,254 bars, 2023-01-03–2026-10-09; provenance retained.  
**Real Phase A WFA executed:** YES; `results/20261011T044241208535Z`; exact analytical reproduction `results/20261011T044703803065Z`.  
**Empirical verdict:** NOT_PROMISING at prescribed 3 bps/side on observed development fill proxies; full robustness remains INCONCLUSIVE. All 28 active rule×ETF combinations have negative net means.  
**Actual OOS:** 2024-07-08–2025-10-02 with gaps; SPY180 / QQQ297 sessions; 300 union / 177 common dates; 3 / 5 of eight folds executed.  
**Holdout since 2026-04-10:** SEALED; raw storage/coverage metadata only, no outcome analysis.  
**G1–G5:** G1 INCONCLUSIVE / G2 INCONCLUSIVE / G3 FAIL / G4 INCONCLUSIVE / G5 INCONCLUSIVE.  
**Verified:** 140 tests passed; lint/dependencies/compile passed; 16,520 alternative strategy/cost trade records independently reconciled; 13 deterministic reproduction artifacts identical.  
**Main limitations:** Skipped folds under unchanged 95% coverage rule; EXPLORATORY_PROTOCOL_CHANGED action input binding; assumed receipt latency; incomplete official-close/action exhaustiveness; FILL_PROXY_ONLY, uncalibrated execution.  
**Next single action:** Review methodology and execution evidence to decide whether to stop/reframe Phase A; do not retune, promote or consume holdout. No new credentials/GitHub setup needed.  
**Latest report:** [reports/stages/STAGE_04_EVIDENCE_REVIEW_2026-10-10_LOCAL_ENV.md](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/stages/STAGE_04_EVIDENCE_REVIEW_2026-10-10_LOCAL_ENV.md).  
**Backtest report:** [reports/stages/STAGE_03_PHASE_A_DEVELOPMENT_2026-10-10_LOCAL_ENV.md](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/stages/STAGE_03_PHASE_A_DEVELOPMENT_2026-10-10_LOCAL_ENV.md); **intake:** [reports/stages/STAGE_02_DATA_ACCESS_AND_COVERAGE_2026-10-10_LOCAL_ENV.md](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/stages/STAGE_02_DATA_ACCESS_AND_COVERAGE_2026-10-10_LOCAL_ENV.md).  
**Review bundle:** [results/20261011T044241208535Z/RESEARCH_REPORT.md](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/results/20261011T044241208535Z/RESEARCH_REPORT.md); [results/20261011T044241208535Z/robustness_scorecard.csv](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/results/20261011T044241208535Z/robustness_scorecard.csv); [DATA_ACCESS_BLOCKERS.md](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/DATA_ACCESS_BLOCKERS.md).  
Prior reports/results and frozen originals preserved. Evidence: `reports/evidence/20261011T043620658191Z_local02/`.
