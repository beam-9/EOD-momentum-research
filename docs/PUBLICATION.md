# GitHub publication and local research evidence

The project has its own Git repository, rooted at `eod-momentum/`; unrelated files in the parent trading workspace are excluded. GitHub remote: https://github.com/beam-9/GEX-indicator.git.

Versioned content includes source, tests, lock file, frozen research records, stage reports, hashes/provenance, and an allowlist of aggregate research summaries and charts. `.env`, raw/normalized market datasets, detailed trades/signals/daily prices, one-session price traces and local evidence directories remain local and ignored. Existing research evidence is preserved on disk. A fresh clone therefore has software and aggregate results, not vendor data or secrets. Do not force-add local datasets. Provider usage rights are not expanded by this repository.

Enable the checked-in commit and push hooks after cloning:

```sh
git config core.hooksPath .githooks
python3 scripts/check_publication.py --staged --history
```

The guard scans actual indexed contents and every reachable committed file version, including deleted files. It rejects restricted paths, known local credential values, recognizable key/token/private-key patterns and symlinks/submodules requiring review. It prints filenames and codes only. It supplements ignore rules and is not a universal secret detector. When a local `.env` exists its credential assignments are compared in memory; values never enter reports. Hooks can be bypassed, so rerun the guard immediately before pushing. Only `.env.example` with empty placeholders belongs in Git.

`review/empty-baseline` and `review/initial-import` pin the authorized initial-import review. Subsequent architecture fixes are compared with `review/initial-import`; review results are in `docs/reviews/ARCHITECTURE_REVIEW_2026-10-10.md`. Historical report links containing original absolute local paths describe the retained workspace; they are not downloadable data URLs. Use the repository's relative links below for published summaries:

- [Project status](../reports/PROJECT_STATUS.md)
- [Stage 03 report](../reports/stages/STAGE_03_PHASE_A_DEVELOPMENT_2026-10-10_LOCAL_ENV.md)
- [Stage 04 review](../reports/stages/STAGE_04_EVIDENCE_REVIEW_2026-10-10_LOCAL_ENV.md)
- [Aggregate metrics](../results/20261011T044241208535Z/metrics.json)
- [Generated report](../results/20261011T044241208535Z/RESEARCH_REPORT.md)
- [Robustness scorecard](../results/20261011T044241208535Z/robustness_scorecard.csv)
- [Diagnostic erratum](../experiments/ERRATUM_001_DROP_BEST_TRADES.md)

The original frozen config and dated intake overlay are historical records. A copied corporate-action input path on another machine necessarily has a different config digest and must stay explicitly exploratory. Never rewrite `protocol_lock.json` to conceal that difference. Consult the latest architecture-stage report before starting another run. No research rerun or holdout evaluation is authorized by repository setup.

## GEX pivot publication (2026-10-11)

Remote HEAD was verified as `32c843ab5ef6fb2dc4d7f4aefcc364719652e873` at the renamed repository; `origin` now uses its current URL. The local project directory and original Python distribution remain `eod-momentum`; the new isolated `src/gex_indicator/` package is discovered by the existing setuptools configuration. No history rewrite or Phase A replay is part of the pivot.

The authoritative v2 handoff is [installed verbatim](RESEARCH_DIRECTION_GEX.md). Its reference claims require independent source qualification; the new protocol remains [DRAFT](../experiments/gex_v1/PROTOCOL_DRAFT.md). The previous README and status are archived byte-for-byte in [docs/gex/archive](gex/archive/). Earlier preflight reports retain their original chronology and are superseded by the v2 [Stage 00](../reports/stages/GEX_STAGE_00_PIVOT_AND_HYGIENE.md) / [Stage 01](../reports/stages/GEX_STAGE_01_DATA_FEASIBILITY.md) reports. A TEST_ONLY browser fixture is not published market data or performance evidence.
