---
project: gex-confluence-research
stage_id: "STAGE_00"
stage_name: "Repository preservation and pivot preflight"
report_date_utc: "2026-10-11T09:33:30.055975+00:00"
report_date_local: "2026-10-11 America/Vancouver"
stage_status: "PARTIAL"
empirical_verdict: "NOT_APPLICABLE"
real_historical_backtest_executed: false
holdout_2026_04_10_and_later_evaluated: false
repo_commit: "32c843ab5ef6fb2dc4d7f4aefcc364719652e873"
authoritative_gex_handoff_available: false
run_ids: []
protocol_hash: "LEGACY_UNCHANGED; GEX_PROTOCOL_NOT_REGISTERED"
data_manifest_paths: ["data/manifests/underlying.json"]
---

# GEX Stage00 — Repository preservation and pivot preflight

## 1. Executive summary (5–8 sentences)

The objective was to inspect and preserve the existing project before pivoting. Baseline32c843a, original research artifacts and the sealed holdout were recorded without outcome analysis. Exact copies of the prior README and project status were archived, and a separate pivot branch was created. Existing software verification passed all195 tests and required checks. The active README/status now describe the requested GEX direction while explicitly marking the missing authoritative documents. No new indicator logic or research protocol was invented. Stage00 is PARTIAL because exact handoff/proposed-README acceptance cannot be checked until the files are available.

## 2. Inputs and provenance

| Item | Actual source/path | Evidence/limitation |
|---|---|---|
| User authorization | 2026-10-11 pivot request | New GEX/EMA8/21/50/HVN/trigger/invalidation/target direction; stages00/01 only |
| Required handoff | GEX_Confluence_Codex_Handoff_v1.md | NOT AVAILABLE in accessible project/Downloads/filename index; path requested |
| Proposed README | User-referenced attachment | NOT AVAILABLE; provisional root README uses explicit request only |
| Existing source | Git baseline32c843a; Python3.12.14; requirements.lock | Preserved source and frozen original research files |
| Genuine underlying history | data/manifests/underlying.json | 1,608,254 bars previously acquired; unchanged dataset SHA256435db3c8e69e96c5356a385c1941ac889a083d36ceaa0c66b186cfec5bfae2c5; no new price analysis |
| Options sample | One authenticated March8,2024 option bar | Local raw SHA256f6a583e4106dc8792c8cab30e79a099e5966e9192a1c14a8cacd8cfcac89a407; feed unverified; gamma/OI absent |
| Live OPRA permission | Authentication-only connection using existing local credentials | Error409, insufficient subscription; no channel subscription/market prices |
| Credentials | PRESENT locally | Values omitted, no new credentials required for performed checks |
| Public source evidence | reports/research/GEX_DATA_SOURCE_OPTIONS_2026-10-11.md | Official documentation reviewed; no provider sample/production acceptance |

Holdout begins2026-04-10 and remains SEALED_NOT_ANALYZED. No original holdout price/outcome was inspected. Finalized-bar latency and historical publication/receipt limitations remain unchanged.

## 3. Changes made

| Path | Actual change | Purpose | Verification |
|---|---|---|---|
| docs/gex/archive/EOD_README_2026-10-11.md | Exact baseline README copy | Retain previous entry point | Byte comparison with baseline Git blob |
| docs/gex/archive/EOD_PROJECT_STATUS_2026-10-11.md | Exact baseline status copy | Retain prior research verdict/state | Byte comparison with baseline Git blob |
| README.md | Provisional GEX direction and clear missing-spec status | Reflect user request without inventing handoff content | Relative links and publication checks |
| reports/PROJECT_STATUS.md | New active direction, legacy holdout/results pointers, blockers | Session continuity | Stage evidence references |
| docs/gex/FOUNDATION_SCOPE_AND_BLOCKERS.md | Reuse inventory and unresolved definitions | Avoid guessed setups/models/platform capabilities | Existing code inspection; explicit NOT IMPLEMENTED labels |
| reports/research/*.md | Vendor, actual Alpaca access and TradingView feasibility notes | Source-backed data/platform decisions | Official documentation and sanitized actual requests |
| reports/gex/STAGE_00*; STAGE_01* | Detailed separate partial reports | Distinguish work performed from acceptance | Original nine-section reporting structure |

No src, scripts, tests, dependencies, frozen configs/protocols/registry/locks, historical results or old finalized reports were modified. No new indicator module, strategy model or parameter set was registered.

## 4. Work executed (commands and observed results)

| Command/action | Observed result | Evidence |
|---|---|---|
| git status/log/remote inspection | Clean baseline32c843a; existing beam-9/EOD-momentum-research remote | Preservation baseline |
| git switch -c codex/gex-foundation-stage00-01 | Exit0 | Isolated pivot branch; prior main retained |
| rg/find/mdfind for referenced files | No matching GEX handoff/proposed README located | Missing paths requested from user; no replacement spec invented |
| .venv/bin/python scripts/verify.py --checks-only --output-dir reports/evidence/gex_stage00_01_2026-10-11/verification | Exit0; 195 passed; no failures/errors/skips; Ruff/pip check/compile PASS | Local commands.json and pytest.xml |
| Official documentation review | Source and platform inventories created | Linked source notes |
| Initial historical option-bar request with feed=opra | HTTP400; request included an undocumented feed argument; error body not retained | Original sanitized evidence retained; not entitlement denial |
| Corrected documented historical option-bar request | HTTP200; one preholdout minute; pagination remains; no gamma/OI fields | Local corrected probe evidence and raw hash |
| OPRA WebSocket connect/auth/disconnect only | Error409 insufficient subscription; zero subscribe messages | Local alpaca_opra_auth_only.json; official error table |
| Byte/hash preservation checks | 104 prior tracked files unchanged, excluding the two archived/replaced entry points; original underlying hash unchanged; no seal/consumed marker created | reports/evidence/gex_stage00_01_2026-10-11/preservation.json |

Python3.12.14, requirements.lock unchanged. One existing upstream websockets deprecation warning; pip cache permission warning did not affect the passing checks. No vendor package, Terminal, subscription, paid job or account setting was installed/created/changed. Read-only network probes used existing credentials and excluded secrets from diagnostics. Actual request paths/parameters are documented in the Alpaca access note.

## 5. Empirical results — ONLY if real historical data was used

**NO GEX HISTORICAL BACKTEST OR LIVE INDICATOR EXECUTED.** No simulated profitability, entry reliability, target hit rate or statistical edge was computed. One real option bar establishes limited historical access/schema only; prices were not printed or analyzed. Existing historical EOD metrics remain archived and are not evidence for the new direction. EMA/HVN/trigger/invalidation/target behavior for the GEX indicator remains NOT IMPLEMENTED pending the authoritative specification.

## 6. Verification and research integrity

Baseline preservation verified 104 prior tracked files byte-for-byte, exact archived README/status copies, and the canonical underlying-data hash. No engine/source tests were edited, no economic runner or holdout-freeze/evaluate command was run, and no experiment count or frozen research hash was changed. The probe contract and historical request are from March2024, before the holdout. OPRA probing stopped at authentication with no market-data channel subscription or price request.

195 existing software tests passed, including fixture-only chronology/holdout protections and publication-guard cases. These tests are not GEX-indicator tests and do not validate new confluence logic. No real dataset was imported into canonical underlying storage. Raw probe responses/local evidence remain ignored; staged content/history are scanned before publication. The old best-trade-removal erratum remains applicable. The missing handoff prevents an exact new-spec compliance review or stage acceptance claim.

## 7. Robustness gates (NOT the same as stage status)

| Gate | Status | Evidence | Remaining requirement |
|---|---|---|---|
| New-stage specification | INCONCLUSIVE | Missing handoff/proposed README | Read authoritative documents and map exact acceptance criteria |
| GEX data readiness | INCONCLUSIVE | Source inventory and access findings | Authentic point-in-time gamma/OI/contract/spot inputs; verified model/timestamp semantics |
| New indicator causality/trials | NOT EVALUATED | No indicator implemented or trials registered | Freeze explicit setup/profile/EMA/trigger rules from handoff before empirical work |
| Economic edge/stability | NOT EVALUATED | No new economic study | Registered independent development protocol; no optimization or holdout reuse |
| Read-only delivery | INCONCLUSIVE | TradingView feasibility | Licensed provider and legitimate external-data/presentation route |

These are provisional feasibility observations, not invented handoff gates. Legacy EOD scorecard remains G1/G2/G4/G5 INCONCLUSIVE, G3 FAIL; the pivot does not reset or reinterpret it.

## 8. Blockers, decisions and next actions

| Priority | Blocker/decision | Owner | Exact next action |
|---|---|---|---|
| P0 | Authoritative handoff and proposed README unavailable | User | Provide local paths to both files; then reconcile every Stage00/01 criterion |
| P1 | Historical GEX-ready gamma/OI inputs unavailable | User/data owner | Supply an existing licensed Cboe/ThetaData/ORATS export or Databento raw sample with field/time/license provenance; do not buy automatically |
| P1 | Existing Alpaca live OPRA access rejected409 | User/provider | Decide whether an already licensed alternative exists or separately authorize an entitlement decision; no activation/subscription performed |
| P1 | EMA/profile/setup/model choices undefined without handoff | User/spec | Confirm universe/timeframe/session, warmup, GEX units/sign/expiry, HVN inputs/bins/anchor and trigger/invalidation/target logic |
| P2 | Pine external-data route unverified | User after data selection | Choose Python read-only chart, clearly manual/as-of Pine levels, or verified TradingView vendor feed; new Pine Seeds is not an assumed solution |

**Recommended next stage:** complete specification intake and reconcile Stage00/01 findings; only then proceed to a registered missing-aware indicator foundation.  
**Do NOT proceed to:** arbitrary strategy rules/optimization, live channel subscriptions, purchases, holdout evaluation, trades or deployment on the basis of this partial preflight.

## 9. Artifacts to provide for review

- [Current status](../PROJECT_STATUS.md)
- [GEX data-source inventory](../research/GEX_DATA_SOURCE_OPTIONS_2026-10-11.md)
- [Actual Alpaca access findings](../research/ALPACA_GEX_ACCESS_FINDINGS_2026-10-11.md)
- [TradingView feasibility](../research/TRADINGVIEW_GEX_DELIVERY_FEASIBILITY_2026-10-11.md)
- [Foundation scope/blockers](../../docs/gex/FOUNDATION_SCOPE_AND_BLOCKERS.md)
- [Archived EOD entry points](../../docs/gex/archive/)
- Local-only verification/preservation/probe evidence: reports/evidence/gex_stage00_01_2026-10-11/

The original reporting template's nine sections were reused provisionally. These reports do not pretend to implement acceptance criteria from an unread document. No secrets or licensed raw payloads belong in the published review bundle.
