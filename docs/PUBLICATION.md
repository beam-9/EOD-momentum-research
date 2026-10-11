# GitHub publication and local research evidence

The project has its own Git repository, rooted at `eod-momentum/`; unrelated files in the parent trading workspace are excluded. GitHub remote: https://github.com/beam-9/EOD-momentum-research.git.

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
