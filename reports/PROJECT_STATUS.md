# GEX Confluence Research — Project Status

Updated **2026-10-11 America/Vancouver**. Current repository: [beam-9/GEX-indicator](https://github.com/beam-9/GEX-indicator); local directory/distribution stays `eod-momentum`. Baseline inspected: `32c843ab5ef6fb2dc4d7f4aefcc364719652e873`; working branch `codex/gex-foundation-stage00-01`. The containing Git commit records the delivered revision.

| Stage / gate | Actual state | Evidence / next step |
|---|---|---|
| GEX00 pivot | **PASS** for handoff Section10 foundation | [Stage00](stages/GEX_STAGE_00_PIVOT_AND_HYGIENE.md): installed v2, archived old docs, new protocol DRAFT, preserved history/data, unavailable/TEST_ONLY UI. |
| GEX01 data qualification / D0 | **BLOCKED** | [Stage01](stages/GEX_STAGE_01_DATA_FEASIBILITY.md), [provider matrix](../docs/GEX_DATA_FEASIBILITY.md). No qualified point-in-time historical/live-compatible GEX. |
| GEX02 causal engines / D1 | **NOT IMPLEMENTED / NOT EVALUATED** | Demo is display-only; full gamma/EMA/profile, target/signal causal parity and golden fixtures remain next engineering stage. |
| GEX03 historical economics / D2–D3 | **NOT RUN** | Requires qualified data and a frozen new protocol before outcomes. No candidate profitability evidence. |
| GEX04 prospective / D4 | **NOT RUN** | No live GEX connection, alerts or prospective collection. |
| GEX05 option execution / D5 | **NOT RUN** | Real eligible NBBO/sizes/cost/settlement evidence required. |

**Verification:** 210 tests passed (195 preserved plus15 new UI checks); Ruff, dependency consistency and compile passed. One upstream websockets deprecation warning. [Verification evidence/report](stages/GEX_STAGE_00_01_VERIFICATION.md) includes browser results and limitations. Publication guard and byte-preservation checks are recorded there. No economic replay occurred.

**Available data:** private genuine Alpaca SIP SPY/QQQ underlying minute archive unchanged:1,608,254 bars,2023-01-03–2026-10-09. It includes sealed dates and was only byte-hashed here. One historical option bar at2024-03-08T15:00Z is genuinely accessible, but feedUNVERIFIED and gamma/OI absent. Live OPRA authentication returned409(insufficient subscription); no subscriptions or market quotes requested. [Actual probes](research/ALPACA_GEX_ACCESS_FINDINGS_2026-10-11.md). Neither establishes GEX history/live readiness.

**New research:** [protocol DRAFT](../experiments/gex_v1/PROTOCOL_DRAFT.md), [22 planned entries](../experiments/gex_v1/registry.csv), zero executed trials. Gamma regimes, portfolio flip roots versus strike crossings, walls, corridors, expiry concentration and EMA/profile confluences are hypotheses. Matched controls and simpler component ablations are mandatory. Exact primary endpoint, parameters, source/model, timing/fold dates, multiplicity/budget and independent new holdout remain unresolved; no freeze exists.

**Implemented UI:** `PYTHONPATH=src .venv/bin/python -m gex_indicator.ui --port 8765`, default DATA_UNAVAILABLE/NO TRADE. Optional `--test-fixture` displays generic synthetic TEST_ONLY/NO LIVE GEX cells and context. No model calculations, provider reads, credential reads, live alerts or orders. Pine external-data limitations documented; Python remains primary. Demo has no validated probabilities or profitability claims.

**Preservation:**103 prior tracked files unchanged apart from current README/status/publication docs; archived README/status byte-exact; canonical archive hash `435db3c8e69e96c5356a385c1941ac889a083d36ceaa0c66b186cfec5bfae2c5`. Old protocol/registry/lock/config/code/results/tags preserved. **Phase A holdout beginning2026-04-10 remains SEALED and unconsumed**, not reassigned. No GEX outcomes were evaluated on any date.

**Unchanged Phase A historical state:** genuine run `results/20261011T044241208535Z`, reproduction `results/20261011T044703803065Z`;15 registered rules,28 active rule×ETF mean net returns negative at assumed3bps/side. SPY180/QQQ297 OOS sessions,3/5 of8 folds respectively; G3FAIL, G1/G2/G4/G5INCONCLUSIVE. Execution assumptions and [erratum001](../experiments/ERRATUM_001_DROP_BEST_TRADES.md) remain documented; original economics were not rerun. These findings neither validate nor refute GEX. [Exact archived prior status](../docs/gex/archive/EOD_PROJECT_STATUS_2026-10-11.md).

**Immediate next single action:** qualify a lawfully supplied existing provider sample against the three declared preholdout dates and [schema/rights checklist](../docs/GEX_DATA_FEASIBILITY.md). Quant Data is the first aggregate candidate, not selected/approved; Databento/Cboe and other licensed sources are alternatives. Need model/cell/wall/flip semantics, historical publication/OI clocks, actual coverage, live parity and retention/derived-display rights. If no existing access, continue offline Stage02 engineering or obtain a vendor quote only with owner authorization; do not purchase/create subscriptions. Freeze choices before economic inspection. Sunday is not a live RTH coverage test.

[Pivot decision](../docs/PIVOT_DECISION_2026-10-11.md) · [installed specification](../docs/RESEARCH_DIRECTION_GEX.md) · [screenshot dictionary](../docs/GEX_SCREENSHOT_FIELD_DICTIONARY.md) · [publication rules](../docs/PUBLICATION.md). Earlier `reports/gex/` missing-document preflight remains historical; its missing-v1 blocker is superseded by v2.
