---
project: eod-momentum
stage_id: "STAGE_02"
stage_name: "Authenticated SIP intake — local credentials"
report_date_utc: "2026-10-11T04:42:39.559093+00:00"
stage_status: "PARTIAL"
empirical_verdict: "NOT_APPLICABLE"
real_historical_backtest_executed: false
holdout_2026_04_10_and_later_evaluated: false
repo_commit: "UNCOMMITTED_REPOSITORY"
run_ids: ["20261011T043620658191Z_local02"]
protocol_hash: "b0ca75b6809a7a91aa23e31b6a7954c3f8aaa7b5b4d43b6f491037e0291315a3"
data_manifest_paths: ["data/manifests/underlying.json", "data/manifests/corporate_actions_2026-10-10.json"]
---

## 1. Executive summary

Local `.env` credentials successfully authenticated with Alpaca, resolving the prior screenshot-derived HTTP 401 blocker. A fresh SIP request for SPY and QQQ on 2024-03-08 returned all 390 regular-session minutes for each symbol with no duplicates or missing minutes. The requested raw history was acquired: 1,608,254 bars across 46 monthly checkpoints, targeting 2023-01-03 through 2026-10-09. Development session checks passed 810 SPY sessions and 811 QQQ sessions; every excluded date/reason is retained. Authenticated corporate actions returned 27 cash dividends, normalized using ex-date with no unresolved economic dates. Closing-auction access succeeded and a development-only primary-exchange catalog was created, with incomplete coverage and unobserved receipt times. Stage 02 is PARTIAL because stronger point-in-time/quote/official-close completeness remains unresolved. At this report's finalization **NO REAL HISTORICAL BACKTEST has yet executed**; authentic data is now ready for a clearly qualified development-only run.

## 2. Inputs and provenance

| Item | Actual source/path | Coverage/feed/as-of status | SHA256/manifest | Limitation |
|---|---|---|---|---|
| Raw minute history | `data/raw/alpaca/*.json`; `data/processed/underlying.parquet` | SPY/QQQ raw; SIP route explicitly requested and accepted; requested 2023-01-03–2026-10-09 | `data/manifests/underlying.json`; Parquet `435db3c8e69e96c5356a385c1941ac889a083d36ceaa0c66b186cfec5bfae2c5` | SDK bars do not echo independent feed field; receipt/revision timing assumed |
| Corporate actions | Authenticated Alpaca v1 corporate-actions endpoint; normalized CSV | 2023-01-03–2026-04-09; 13 SPY and 14 QQQ cash dividends | `data/manifests/corporate_actions_2026-10-10.json` | Raw all-type response retained; independent completeness and original publication times unverified |
| Official closes | Authenticated SIP auction endpoint; `data/processed/development_official_closes_2026-10-10.json` | 792 SPY and 777 QQQ mapped development closes | `reports/evidence/20261011T043620658191Z_local02/official_close_catalog.json` | Of 819 expected dates per symbol, 27 SPY and 42 QQQ lack a qualifying near-close primary-M event; mapping/late-event limitations retained; no receipt times |
| Config/protocol | Frozen originals plus `config/intake_2026-10-10.yaml` | All strategy/timing/cost/fold settings identical; only corporate-actions input path bound | `reports/evidence/20261011T043620658191Z_local02/input_binding.json`; `experiments/DATA_INTAKE_NOTE_2026-10-10.md` | Overlay honestly classified EXPLORATORY_PROTOCOL_CHANGED; exact frozen-config confirmation not claimed |

Credentials are PRESENT in the explicitly loaded local ignored `.env`, never printed or copied into evidence. Minute timestamps are aware UTC minute starts. First-availability is ASSUMED minute-end + 30 seconds, not observed historical receipt timing. Extended-session bars are stored; only complete XNYS regular sessions are eligible. Raw holdout bars may be stored and hashed, but holdout signals/returns/outcomes were not computed. No purchases or account changes occurred. User-authorized local research use does not imply redistribution rights; raw licensed data stays local.

## 3. Changes made

| Path | Change | Why | Tests added/updated |
|---|---|---|---|
| `scripts/stage02_intake.py` | Reproducible explicit local-env loader, fresh development-date SIP probe, optional full cached acquisition and audit | Avoid secret disclosure and preserve acquisition provenance | Existing adapter regression suite; CLI help/lint/compile; final software verification to follow |
| `data/raw/`, `data/processed/`, `data/manifests/` | Genuine vendor observations and hashed source records | First authenticated data intake | Strict normalization and independent DuckDB/Parquet row reconciliation |
| `config/intake_2026-10-10.yaml` | Separate runtime copy binds authenticated action file only | Apply original action exclusions without rewriting frozen config | Exact one-key diff recorded before outcome analysis |
| `experiments/DATA_INTAKE_NOTE_2026-10-10.md` | Explicit overlay/endpoint qualification | No silent protocol change | Hash recorded before outcomes |
| Reports/status | New immutable report and current resume state | Preserve earlier finalized reports | Section/path checks |

## 4. Work executed

| Command | Exit status | Run ID / artifact path | Notes |
|---|---|---|---|
| Explicit local-env probe via `/tmp/eod_local_data.py` | Wrapper 0, sandbox transport blocked | `reports/evidence/20261011T043537938982Z_local02/` | No entitlement conclusion from sandbox failure |
| Same probe with authorized network access | 0; SIP success | `reports/evidence/20261011T043546763357Z_local02/` | Both symbols complete 390/390 RTH minutes |
| `PYTHONPATH=src .venv/bin/python /tmp/eod_local_data.py --acquire` | 0; full acquisition success | `reports/evidence/20261011T043620658191Z_local02/access_and_acquisition.json` | Persisted 1,608,254 bars and raw hashes; reproducible helper saved as scripts/stage02_intake.py |
| Authenticated corporate-action and auction probes | 0; endpoint successes | `reports/evidence/20261011T043620658191Z_local02/supplementary_access.json` | CA raw parser preserves unknown categories; no total cap |
| Development-only paginated auction collection | 0; endpoint success | `reports/evidence/20261011T043620658191Z_local02/official_close_catalog.json` | SIP; no dates on/after holdout boundary cataloged |
| Ruff formatted acquisition helper / `ruff check scripts/stage02_intake.py` | Final check 0 | Script | Initial temporary compact style was formatted before acceptance |

Python 3.12.14 and existing lock retained. Development audit: 819 expected XNYS sessions per symbol. Eight early-close dates are excluded for both; SPY additionally lacks four minutes on 2023-06-05 (386/390). Audit excludes rather than imputes these observations. The full date/reason list is `reports/evidence/20261011T043620658191Z_local02/excluded_development_sessions.json`; further action/prior-session exclusions will be generated by the unchanged feature builder. Known action dates and dependent next-session features are excluded by the frozen logic. No sample windows or thresholds were changed.

## 5. Empirical results — only if real historical data was used

Authentic data **intake and quality counts only**, no strategy outcomes at this stage. No trades, expectancy, net/gross P&L, uncertainty or drawdown has yet been computed. Stage 03 may now run the 15 unchanged registered procedures, clearly labeled development-only / FILL_PROXY_ONLY / EXPLORATORY_PROTOCOL_CHANGED because the action-input binding changes the config digest. No official-close field is silently substituted into the frozen previous-minute proxy signal. Holdout remains excluded from feature/outcome processing.

## 6. Verification and research integrity

Strict normalization rejected no returned invalid/ambiguous bar schema; audit retained all failures. Raw payloads and original retrieval times are preserved; SDK cached replay is deterministic. Frozen config/protocol/registry hashes match their original lock. The input overlay changes exactly corporate_actions_path and was written before real outcome analysis. No research engine or model source changed. Authentication values are not logged. Holdout: **SEALED / NOT ANALYZED**, no freeze or evaluation call. Official-close catalog mapping uses SPY primary exchange P and QQQ Q, condition M, scheduled close through close+5 minutes, retaining the last qualifying event; this is an explicit audit mapping, not historical receipt proof. Full raw events and unmatched dates remain inspectable. Official endpoint docs: https://docs.alpaca.markets/us/reference/corporateactions-1 and https://docs.alpaca.markets/us/reference/stockauctions-1. Corporate-action publication delays and final-bar revisions remain unverified, so no fully point-in-time execution claim is supported.

## 7. Robustness gates

| Gate | PASS/FAIL/INCONCLUSIVE | Evidence path | Remaining requirement |
|---|---|---|---|
| G1 Data | INCONCLUSIVE | `reports/evidence/20261011T043620658191Z_local02/development_quality.json`; action/auction manifests | Original receipts/revisions, independent action completeness, full official-close mapping and NBBO |
| G2 Leakage/trials | INCONCLUSIVE | Frozen lock; input note | Real run causal reconciliation; input-only config variance remains disclosed |
| G3 Economic net edge | INCONCLUSIVE | No economic run yet | Development OOS evidence |
| G4 Stability | INCONCLUSIVE | No economic run yet | Folds/cost/latency/outliers |
| G5 Deployability | INCONCLUSIVE | Input note | Verified quotes/latency/platform and future prospective evidence |

## 8. Blockers, decisions and next actions

| Priority | Blocker or decision | Who can resolve | Exact next action |
|---|---|---|---|
| Decision | Eligible authenticated data exists; bad dates excluded | Project | Run original 15 procedures using documented action-input overlay; retain all trials and mark fill proxy/config variance |
| P1 | Exact frozen-config binding differs by external input path | Future protocol work package | Keep originals intact; never label overlay exact frozen-config validation or consume holdout from it |
| P1 | Receipts/revisions/NBBO and exhaustive official close evidence missing | Data owner/vendor | Identify existing authorized sources; no paid procurement here |

**Recommended next stage:** Stage 03 — genuine development-only WFA with original rules and explicit overlay/proxy labels.  
**Do NOT proceed to:** sealed holdout, new strategies, indicator or live trading.

## 9. Artifacts to provide for ChatGPT review

- [PROJECT_STATUS.md](../PROJECT_STATUS.md)
- This stage report
- `reports/evidence/20261011T043620658191Z_local02/access_and_acquisition.json`, `development_quality.json`, `excluded_development_sessions.json`, `supplementary_access.json`, `official_close_catalog.json`, `input_binding.json`
- [Data-input treatment](../../experiments/DATA_INTAKE_NOTE_2026-10-10.md)
- No empirical RESEARCH_REPORT or scorecard yet. Do not share raw licensed data or `.env`.
