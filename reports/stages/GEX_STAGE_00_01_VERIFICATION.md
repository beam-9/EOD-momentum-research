# GEX Stage00/01 verification evidence — 2026-10-11

Baseline latest inspected commit `32c843ab5ef6fb2dc4d7f4aefcc364719652e873`; delivery revision is this file's containing commit. Status **PASS software/preservation; browser findings separately scoped; D0 BLOCKED, D1 NOT EVALUATED**.

## Executed checks

` .venv/bin/python scripts/verify.py --checks-only --output-dir reports/evidence/gex_v2_2026-10-11/verification ` ran with loopback socket access for HTTP tests. **210 passed,0failed,0errors,0skips in29.06s**. One websockets.legacy upstream deprecation warning. Ruff **PASS**, pip check **PASS: no broken requirements**, compileall **PASS**. Exact commands/exit codes, stdout/stderr and JUnit retained locally in that immutable directory. Baseline preflight independently ran195 tests;15 additional cases cover read-only demo behavior, opt-in fixtures, screenshot-transcription arithmetic, escaping, route allowlist/traversal, write refusal, loopback binding, Host rebinding and JSON response policies.

` .venv/bin/python scripts/verify_gex_preservation.py --hash-private-data --output reports/evidence/gex_v2_2026-10-11/preservation.json ` **PASS**:103 old tracked files unchanged (current README/status/publication excluded); original README/status archives exact; canonical private data hash unchanged; no data deserialization. Existing tags `review/empty-baseline` and `review/initial-import` retained. No holdout seal or consumed marker is present; old boundary2026-04-10 remains unconsumed. Hash/file preservation is corroboration, not by itself proof of all historic access behavior.

Remote read-only command `git ls-remote https://github.com/beam-9/GEX-indicator.git HEAD` returned baseline `32c843ab5ef6fb2dc4d7f4aefcc364719652e873`. `origin` updated to renamed URL; no history rewrite. Installed handoff hash matches supplied file exactly.

## Browser verification

The expect skill was used for actual Chromium interactions on loopback. Browser results/evidence and audit limitations are recorded in `reports/evidence/gex_v2_2026-10-11/browser.json`. Both default and fixture modes rendered their required labels; default had no price/GEX timestamp, fixture remained NO TRADE, both flip names stayed distinct, writes returned405,390px viewport had no horizontal overflow, and no console errors were observed. Final status heading was checked after its correction. Screenshots `ui_default.png` and `ui_fixture.png` remain in that private evidence directory. Initial accessibility audit found one manual color-use check (signs also appear numerically), one heading issue corrected and browser-confirmed, and three expect-tool overlay findings. The final combined accessibility audit stalled; **no full accessibility certification is claimed**. This is an engineering rendering test, with no external feed/data access or statistics.

## Publication and review

Indexed/history publication guard **PASS** (242 blobs scanned; no values logged); current-document local-link checks **PASS**. Whitespace diagnostics in exact supplied/archived Markdown reflect retained hard line breaks; those sources remain byte-preserved. The delivered two-axis review is recorded in `docs/reviews/GEX_FOUNDATION_REVIEW_2026-10-11.md`. No credential values, .env, licensed raw response, canonical market archive or ignored evidence files are staged. The [sanitized delivery manifest](../../docs/gex/DELIVERY_MANIFEST_2026-10-11.json) hashes the retained evidence and supplied sources so local artifacts can be checked without publishing them.

No economic research, synthetic profitability statistics, fills, source procurement, broker permission changes or live execution were performed. Full causal engineering and independent statistical evidence remain pending; 210 passing software tests do not pass D0–D5.
