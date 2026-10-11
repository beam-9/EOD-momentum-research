# EOD Momentum — Project Status

**Updated UTC:** 2026-10-11T05:06:28.656978+00:00; local work date 2026-10-10.  
**Last completed stage/status:** Stage05 architecture review PASS; Stage03 empirical coverage remains PARTIAL.  
**Real historical data available:** YES; Alpaca explicitly requested SIP/raw; 1,608,254 bars, 2023-01-03–2026-10-09; provenance retained.  
**Real Phase A WFA executed:** YES; `results/20261011T044241208535Z`; exact analytical reproduction `results/20261011T044703803065Z`.  
**Empirical verdict:** NOT_PROMISING at prescribed 3 bps/side on observed development fill proxies; full robustness remains INCONCLUSIVE. All 28 active rule×ETF combinations have negative net means.  
**Actual OOS:** 2024-07-08–2025-10-02 with gaps; SPY180 / QQQ297 sessions; 300 union / 177 common dates; 3 / 5 of eight folds executed.  
**Holdout since 2026-04-10:** SEALED; raw storage/coverage metadata only, no outcome analysis.  
**G1–G5:** G1 INCONCLUSIVE / G2 INCONCLUSIVE / G3 FAIL / G4 INCONCLUSIVE / G5 INCONCLUSIVE.  
**Verified:** Current source: 195 tests passed; lint/dependencies/compile PASS; independent Standards/Spec reviews found zero new findings. Prior runs: 16,520 records reconciled and 13 analytical artifacts reproduced; archived bytes preserved.  
**Main limitations:** Skipped folds under unchanged 95% coverage rule; EXPLORATORY_PROTOCOL_CHANGED action input binding; assumed receipt latency; incomplete official-close/action exhaustiveness; FILL_PROXY_ONLY, uncalibrated execution.  
**Next single action:** Review Erratum001, methodology and execution evidence to decide whether to stop/reframe PhaseA; no economic rerun authorized. No new credentials/GitHub setup needed.  
**Historical decision report:** [reports/stages/STAGE_04_EVIDENCE_REVIEW_2026-10-10_LOCAL_ENV.md](../reports/stages/STAGE_04_EVIDENCE_REVIEW_2026-10-10_LOCAL_ENV.md).  
**Backtest report:** [reports/stages/STAGE_03_PHASE_A_DEVELOPMENT_2026-10-10_LOCAL_ENV.md](../reports/stages/STAGE_03_PHASE_A_DEVELOPMENT_2026-10-10_LOCAL_ENV.md); **intake:** [reports/stages/STAGE_02_DATA_ACCESS_AND_COVERAGE_2026-10-10_LOCAL_ENV.md](../reports/stages/STAGE_02_DATA_ACCESS_AND_COVERAGE_2026-10-10_LOCAL_ENV.md).  
**Review bundle:** [results/20261011T044241208535Z/RESEARCH_REPORT.md](../results/20261011T044241208535Z/RESEARCH_REPORT.md); [results/20261011T044241208535Z/robustness_scorecard.csv](../results/20261011T044241208535Z/robustness_scorecard.csv); [DATA_ACCESS_BLOCKERS.md](../DATA_ACCESS_BLOCKERS.md).  
**Latest report:** [Stage05 architecture/publication](stages/STAGE_05_ARCHITECTURE_AND_PUBLICATION_2026-10-10.md).  
**Erratum:** [Best-trade stress correction](../experiments/ERRATUM_001_DROP_BEST_TRADES.md); affected old stress rows are not corrected evidence. User authorized the fix without any economic rerun.  
**GitHub:** https://github.com/beam-9/EOD-momentum-research; credentials/raw datasets excluded.  
Prior reports/results and frozen originals preserved. Evidence: `reports/evidence/20261011T043620658191Z_local02/` (research), `reports/evidence/20261011_architecture_review/` (maintenance).
