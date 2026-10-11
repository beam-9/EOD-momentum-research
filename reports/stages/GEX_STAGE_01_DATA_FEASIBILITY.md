# GEX Stage 01 — Historical/live data feasibility

**Status: BLOCKED for D0 qualification.** Source audit and bounded existing-access checks are completed; no qualified primary GEX source or historical GEX backtest exists.

**Local date:** 2026-10-11 America/Vancouver. **Inspected latest commit / preservation baseline:** `32c843ab5ef6fb2dc4d7f4aefcc364719652e873`. **Working branch:** `codex/gex-foundation-stage00-01`. This report describes the subsequent working-tree changes; its containing Git commit identifies the delivered revision. Remote `https://github.com/beam-9/GEX-indicator.git` HEAD matched the baseline during read-only inspection.

**Authority:** [installed v2 handoff](../../docs/RESEARCH_DIRECTION_GEX.md), SHA256 `dd617d615653b3b8e5513ff782627fbfce1c8ecc4f09dd8be901ceec8098a84c`. The earlier missing-v1 preflight reports in `reports/gex/` remain preserved; their missing-document blocker is superseded, not a current blocker. New work follows Section10: stop before economic outcomes.

**Preservation:** the repeatable byte audit checks 103 prior tracked files unchanged, excluding only current README/status/publication documentation. Prior README/status archives are byte-exact. The frozen Phase A protocol remains SHA256 `b0ca75b6809a7a91aa23e31b6a7954c3f8aaa7b5b4d43b6f491037e0291315a3`; canonical underlying archive remains SHA256 `435db3c8e69e96c5356a385c1941ac889a083d36ceaa0c66b186cfec5bfae2c5`. Hashing does not deserialize or evaluate prices. The **2026-04-10 onward Phase A holdout remains sealed**, not reassigned to GEX, with no outcome inspection, economic replay, strategy optimization or trade during this stage. Archived tags/history and the diagnostic erratum remain intact.

## Available data and actual access evidence

| Source/check | Actual observation | Coverage / timestamp / quality conclusion |
|---|---|---|
| Preserved underlying Alpaca SIP archive |1,608,254 private raw SPY/QQQ minute bars,2023-01-03–2026-10-09; preserved from legacy intake | Archive extends into old sealed interval; no price/outcome reads in this stage. OHLCV does not establish exact volume-at-price or options GEX. |
| Initial narrow historical option request |HTTP400 with unsupported `feed=opra`; no retained body | Invalid request is not an entitlement failure. Retained as failed access experiment. |
| Corrected documented historical options request |HTTP200,one SPY240308C00510000 minute bar,2024-03-08T15:00Z; next-page token | Only one historical contract/minute, not full coverage. Returned `c,h,l,n,o,t,v,vw`; gamma and OI absent. Actual feed **UNVERIFIED**, no historical receipt/publication semantics established. |
| Alpaca live OPRA auth-only |WebSocket connected,auth error409:insufficient subscription |No subscribe messages,quotes or channel data. Live coverage/latency not measured. No new entitlement requested. |
| Other vendors |Official documentation only; no credentials, payload or licensed dataset supplied |Advertised capability is not verified retrievability, schema parity, rights or model correctness. |

Exact request parameters, observed failures, error semantics and official links are in [authenticated findings](../research/ALPACA_GEX_ACCESS_FINDINGS_2026-10-11.md). The corrected private response SHA256 is `f6a583e4106dc8792c8cab30e79a099e5966e9192a1c14a8cacd8cfcac89a407`. Raw response remains at `data/raw/alpaca/gex_documented_bar_probe_2026-10-11.json`, ignored. Sanitized evidence/probe code remain in `reports/evidence/gex_stage00_01_2026-10-11/`. No raw prices or credentials enter Git. Request receipt logs are probe evidence, not reconstructed historical receipts.

## Provider comparison and selection decision

[Feasibility matrix](../../docs/GEX_DATA_FEASIBILITY.md) separates historical/live capability, units/sign conventions, flip/cell definitions, rights, advertised coverage and actual access. It incorporates Quant Data, Databento, Cboe, Massive, Intrinio, Alpaca and other documented candidates, plus [earlier source inventory](../research/GEX_DATA_SOURCE_OPTIONS_2026-10-11.md). The matrix’s SSRN verification section distinguishes publisher metadata from independently verified study results.

**No vendor selected.** Quant Data is the first targeted aggregate-GEX candidate if already licensed access exists; Databento/Cboe are raw-data/historical alternatives. A latest chain or EOD dataset is not intraday point-in-time history. OPRA quotes alone do not reveal dealer positions; prior published OI, model sign, IV/rate/dividend inputs and contract adjustments are necessary for reconstruction. Provider wall/flip semantics must be named, not silently replaced.

Three historical dates must be predeclared and tested for each candidate before selection; they are pending legitimate GEX access, not passed by the single Alpaca bar. The live session test is pending entitlement and an open session: local Sunday2026-10-11 is closed. No latency distribution, coverage completeness, full-chain correction behavior or live/historical parity claim is possible from auth-only access.

## Costs, rights and external blockers

Existing credential probes made no purchase,subscription or account change. Future query/full-universe/storage costs are **NOT ESTIMATED** without product scope and provider quote. No numeric free/paid promise is accepted from marketing. Personal/commercial use, raw retention, derived exposure display and redistribution rights remain unverified per provider. Licensed samples and written rights are required before broad acquisition/publication. Raw vendor data remains private.

Missing: historical chain/GEX with event/publication/receipt semantics, OI as-of, multipliers/corporate actions, eligible roots/expiries, actual model units/signs/flip definitions, live-compatible same-method feed, licensed usage, schema coverage samples, stale/revision behavior and measured latency. Official-close/corporate-action limitations of prior price research remain archived and must be revisited for new source-specific definitions; no silent assumption change is made.

## Executed verification and reproducibility

Initial preflight software check independently re-ran **195 tests PASS**, Ruff, pip dependency check and compile; source logs at `reports/evidence/gex_stage00_01_2026-10-11/verification/`. New delivery verification and browser evidence are recorded in the companion [verification report](GEX_STAGE_00_01_VERIFICATION.md); use its exact final counts, not an assumed baseline count.

Commands (from the actual project root, private data is not needed except optional byte hashing):

```sh
.venv/bin/python scripts/verify.py --checks-only --output-dir reports/evidence/gex_v2_2026-10-11/verification
.venv/bin/python scripts/verify_gex_preservation.py --hash-private-data --output reports/evidence/gex_v2_2026-10-11/preservation.json
PYTHONPATH=src .venv/bin/python -m gex_indicator.ui --port 8765
PYTHONPATH=src .venv/bin/python -m gex_indicator.ui --port 8766 --test-fixture
.venv/bin/python scripts/check_publication.py --staged --history
```

Evidence destinations are immutable: choose a new path if replaying an existing command. The preservation output is PASS with103 unchanged files and two exact archives; private underlying hash PASS, no market-data deserialization. Credentials, raw option sample and browser/private evidence remain ignored. The sanitized [delivery manifest](../../docs/gex/DELIVERY_MANIFEST_2026-10-11.json) records source/evidence hashes. This is reproducible engineering verification, not empirical profitability evidence.

## Results, robustness verdict and next single action

D0 **BLOCKED**; D1pending; D2–D5NOT RUN. **INCONCLUSIVE / NO GEX ECONOMIC EVIDENCE**. Zero GEX strategy trials,zero historical GEX outcome tests,zero options-profit or forward-performance observations. The rejected400 request and409 entitlement failure are retained; successful200 access is not promoted into an economics result. Synthetic UI is not evidence of prediction or verified fills.

Next single action: supply an **already licensed** Quant Data or alternative sample/access method and usage terms, using the matrix checklist (paths/setup only; no secrets in chat). If none exists, owner must decide whether to seek a vendor quote or continue offline engineering; any paid plan/subscription/new permission requires separate explicit approval. Freeze source/model, dates, endpoints, thresholds and independently authorized new holdout before Stage03. Stage02 can proceed only as conspicuously TEST_ONLY causal-engine work while D0 remains blocked. Stop before economic outcomes as required by handoff Section10.

**Latest implementation commit inspected and independently reviewed:** `d4bd311e764fbd5383fcfb1f68e2c8f30d035dc2`; Standards0 / Spec0 actionable findings. [Two-axis review](../../docs/reviews/GEX_FOUNDATION_REVIEW_2026-10-11.md). Subsequent documentation-only delivery commit records review/provenance; no economic analysis or code change followed.
