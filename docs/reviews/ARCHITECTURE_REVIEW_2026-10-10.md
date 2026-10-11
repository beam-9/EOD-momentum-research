# Architecture review — 2026-10-10 local / 2026-10-11 UTC

Applied skills: `/Users/beam.t/.codex/skills/code-review/SKILL.md` and `/Users/beam.t/.codex/skills/codebase-design/SKILL.md`. The user chose an initial-import review followed by architecture changes. Two independent subagents reviewed Standards and Spec separately, then re-reviewed the committed fixes.

Initial fixed point: `review/empty-baseline` (`bd5d70f`). Initial import: `review/initial-import` (`4a7a03b`). Commands: `git diff review/empty-baseline...review/initial-import`; `git log review/empty-baseline..review/initial-import --oneline` (one import commit).

Architecture fixed point: `review/initial-import`. Reviewed implementation commit: `9dd1e751f8da849301da4687f35e74c0ca199271`. Commands: `git diff review/initial-import...9dd1e751f8da849301da4687f35e74c0ca199271`; `git log review/initial-import..9dd1e751f8da849301da4687f35e74c0ca199271 --oneline` (one refactor commit).

Standards sources: pyproject.toml tooling configuration, existing import-safe verify.py/cli.py conventions and the skill's labeled Fowler heuristics. No dedicated CODING_STANDARDS/CONTRIBUTING or issue-tracker configuration exists. The missing setup was disclosed; handoffs provided the spec directly. Specs: experiments/HANDOFF_v3.md, experiments/RESEARCH_PROTOCOL.md, the supplied next-stage handoff and the user's explicit correction-without-rerun authorization.

## Standards

Initial review found three actionable issues:

1. Possible Divergent Change in the intake script: top-level `args = p.parse_args()`, `f = fetch(...)` and `raise SystemExit(...)` combine unrelated side effects and prevent ordinary importing/testing. The fix supplies guarded main and callable run_intake.
2. Credential cleanup used `os.environ.pop(n, None)` for every supported name, deleting pre-existing caller credentials. Scoped loading now restores the exact previous values on success and failure.
3. Protocol and holdout invariants used removable `assert` statements. Explicit checked failures now run before provider requests, also when Python optimization is enabled.

Final independent review: no concrete introduced documented-standard violations or actionable baseline smells. All three initial findings are resolved. The intake module provides depth through a small interface; its provider seam has real and test adapters. Snapshot handling concentrates version/provenance complexity within persist. No broad framework or speculative adapters were added.

Operational limitations: hooks need documented local installation and are bypassable. Active dataset and manifest replacement uses two filesystem operations, not a crash-atomic transaction; immutable snapshots retain recovery evidence. The current interface assumes one writer.

## Spec

Initial review found three actionable issues:

1. The protocol says “drop best 1/5 trades,” but the implementation ranked flat sessions too. The fix ranks executed trades only and clears removed exposure. Erratum001 explicitly qualifies the old diagnostic rows, preserves old outputs and forbids an unapproved economic rerun.
2. The handoff says “Preserve append-only experiment ledgers and original manifests” and “Source data must be hash-traceable.” Active dataset replacement now archives immutable original/replacement data and manifest bytes, verifying collisions and recording missing legacy provenance as unknown.
3. Portable empirical reconstruction was incomplete: the historical action path is machine-specific and collector code was ignored local evidence. The committed corporate-action command reconstructs the archived CSV byte-for-byte from the authentic local raw envelope and documents a new exploratory input binding on another machine. It rejects unsupported categories/holdout ex-dates and retains the earlier provider record explicitly.

Final independent review: no new actionable findings; all three initial findings addressed. No research runner or holdout evaluation was executed. Representative quote/receipt evidence, official-close completeness and independent action exhaustiveness remain disclosed research limitations rather than claimed fixes. The publication guard scans staged contents and reachable historical versions; no obvious selected-file bypass was found, but it is not a universal secret detector.

**Review totals:** Standards — 3 initial findings resolved, 0 new findings; strongest initial issue was import-time side effects and credential mutation. Spec — 3 initial findings resolved, 0 new findings; strongest initial issue was incorrect best-trade removal.
