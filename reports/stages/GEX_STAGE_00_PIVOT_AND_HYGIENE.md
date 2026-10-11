# GEX Stage 00 — Pivot, repository hygiene and protocol foundation

**Status: PASS for the Section10 Stage00 deliverables; research remains UNVALIDATED.**

**Local date:** 2026-10-11 America/Vancouver. **Inspected latest commit / preservation baseline:** `32c843ab5ef6fb2dc4d7f4aefcc364719652e873`. **Working branch:** `codex/gex-foundation-stage00-01`. This report describes the subsequent working-tree changes; its containing Git commit identifies the delivered revision. Remote `https://github.com/beam-9/GEX-indicator.git` HEAD matched the baseline during read-only inspection.

**Authority:** [installed v2 handoff](../../docs/RESEARCH_DIRECTION_GEX.md), SHA256 `dd617d615653b3b8e5513ff782627fbfce1c8ecc4f09dd8be901ceec8098a84c`. The earlier missing-v1 preflight reports in `reports/gex/` remain preserved; their missing-document blocker is superseded, not a current blocker. New work follows Section10: stop before economic outcomes.

**Preservation:** the repeatable byte audit checks 103 prior tracked files unchanged, excluding only current README/status/publication documentation. Prior README/status archives are byte-exact. The frozen Phase A protocol remains SHA256 `b0ca75b6809a7a91aa23e31b6a7954c3f8aaa7b5b4d43b6f491037e0291315a3`; canonical underlying archive remains SHA256 `435db3c8e69e96c5356a385c1941ac889a083d36ceaa0c66b186cfec5bfae2c5`. Hashing does not deserialize or evaluate prices. The **2026-04-10 onward Phase A holdout remains sealed**, not reassigned to GEX, with no outcome inspection, economic replay, strategy optimization or trade during this stage. Archived tags/history and the diagnostic erratum remain intact.

## Completed implementation and changed files

- Installed exact supplied handoff at `docs/RESEARCH_DIRECTION_GEX.md`; retained proposed README source under `docs/gex/specifications/` and merged truthful current capability/status into root README.
- Updated current remote/publication guidance; retained local directory/distribution/import paths. Archived prior README/status in `docs/gex/archive/` without changing historical reports.
- Added `docs/PIVOT_DECISION_2026-10-11.md`, `experiments/gex_v1/PROTOCOL_DRAFT.md`, and separate `registry.csv`: DRAFT, no source selected, no economic trials executed, no new holdout assigned.
- Added `docs/GEX_SCREENSHOT_FIELD_DICTIONARY.md`. The supplied handoff's image transcription is an illustrative UX reference; original GEX screenshots were not independently supplied/inspected in this stage. Unlabeled 129,473 is not GEX dollars or observed dealer inventory.
- Added isolated `src/gex_indicator/` read-only UI plus tests, and byte-preservation verifier `scripts/verify_gex_preservation.py`. Setuptools already discovers the new package; no legacy package rename or dependency changes.
- Updated `reports/PROJECT_STATUS.md`, current foundation blockers, Stage00/01 reports and source-feasibility documentation. Earlier preflight reports remain historical.

## Hypotheses and controlled comparisons

Gamma regimes, repriced portfolio roots (distinct from per-strike crossings), significant walls, low-density corridors, expiry concentration, EMA8/21/50 and prior/partial-as-of profiles are **hypotheses**. The draft requires matched walls ranks2–5/round numbers, distance/volatility/grid-matched corridor placebos, placebo flips, and component ablations. L4flip is monitor-only; L5conflict is NO TRADE. Exact thresholds, source, primary endpoint, fold dates and separate holdout require a documented freeze before outcomes. No candidate has positive or negative results yet; planned trials are not evidence.

## Demo artifact and figures

The loopback demo defaults to DATA_UNAVAILABLE/NO TRADE. Optional TEST_ONLY displays generic synthetic illustrative chart/heatmap values, never screenshot-derived market observations. Both modes suppress trading candidates and return no calibrated probability, execution, live feed or P&L claim. It reads no `.env`, legacy market files or external services. Browser evidence is listed in the verification report; screenshot fixtures are engineering figures only. Complete gamma/EMA/profile/target engines remain Stage02 work.

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

## Gate status, limitations and next action

D0 **BLOCKED** (no qualified historic/live GEX); D1 **NOT EVALUATED** (golden causal engine parity pending); D2–D5 **NOT RUN**. Read-only UI rendering does not advance these gates. Prior Phase A remains G3FAIL, other gatesINCONCLUSIVE, with all28 active rule×ETF means negative under assumed3bps/side; these are unchanged archival results, not GEX findings.

Next single action: qualify one existing licensed GEX sample using the [Stage01 checklist](../../docs/GEX_DATA_FEASIBILITY.md), or choose continued offline Stage02 engineering without economic claims. Review README, pivot decision, protocol DRAFT, screenshot dictionary, UI tests and Stage01 report. No purchase/subscription/permissions/trading action has been taken.
