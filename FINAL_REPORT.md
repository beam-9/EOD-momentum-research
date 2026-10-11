# Final execution and evidence report

**NO_REAL_HISTORICAL_BACKTEST**

Implemented and executed the Phase A pipeline and independent Phase D no-data report path.
Real SPY/QQQ coverage: none; real excluded-session count: not measurable. No profitability numbers,
market trade journals or performance charts are claimed. Empty tables are explicit schema artifacts.

## Verification actually executed

- `.venv/bin/python scripts/verify.py`: **129 passed, 0 failed**, one upstream SDK deprecation warning.
- `.venv/bin/ruff check src tests scripts`: PASS.
- `.venv/bin/python -m pip install --no-build-isolation --no-deps -e .`: editable packaging PASS.
- `.venv/bin/python -m pip check`: PASS. Python 3.12.14, requirements.lock pinned.
- `.venv/bin/python -m compileall -q src`: PASS.
- `data check --source alpaca --probe`: missing credentials, no probe sent (expected exit 2).
- `data fetch`: MISSING_CREDENTIALS (expected exit 2); no remote price request executed.
- `research run --phase B/C`: explicit data/protocol gates (expected exit 2).
- `replay` and `research run --phase D`: reports/manifests/scorecards generated with null performance.
- `.venv/bin/python scripts/benchmark.py`: week/year synthetic engineering profiles only.

The end-to-end fixture tests exercise storage → as-of features → event simulation → chronological
folds → all candidate/cost/stress records → bootstrap/report/charts. Seven analytical output hashes
match after changing all sealed-holdout prices. A separate hand calculation and independent
screening formula reconcile signed returns and both sides' friction. Past-close publication/revision
poison, future-price features, mixed instruments, holidays, missing exits, invalid quotes, malformed
folds and ledger tampering are rejected. Holdout reuse and changed inputs are blocked. These establish
software behavior under controlled fixtures; they do not prove accuracy on an unobserved live feed.

## Design and frozen boundaries

15 registered rules (13 fixed, 2 validation-selected); zero evaluated on genuine data. 100 fixed null
seeds are diagnostic, not optimized strategies. Primary SPY; QQQ secondary, same-date dependent.
Costs 0/1/3/5 bps per side; 3 bps conservative selection; 6/9 bps and latency/outlier stresses.
First planned training [2023-01-03,2024-01-03), validation [2024-01-03,2024-04-03), outer test
[2024-04-03,2024-07-03), step quarterly; last complete test ends 2026-04-03. Full proposed ledger:
`results/20261010T034445993998Z/walk_forward_folds.csv`.
Holdout [2026-04-10, after 2026-10-09] remains sealed and never analyzed. No empirical split ran.

## Implemented versus gated

Phase A: official read-only adapter/cache/import, UTC/ET calendar and quality audit, causal features,
15 rules, canonical event engine, independent parity, per-side costs, nested chronological selection,
paired-date inference, tails/drawdowns, null/stress/stratified comparisons, append-only trials,
immutable holdout selection, chart/report generators and reproducibility manifests.
Phase D: independent fixed-rule ETF proxy runner, prior ATR, decision/fill lag, cash limits, ACT/365
financing assumption, gap/overnight/open losses and daily economic accounting. Never a CFD replica.
Phase B/C: schema import and isolated point-in-time GEX/sign and actual option-NBBO utilities tested;
complete historical empirical runners require their unavailable datasets and further orchestration.
DSR/PBO honestly NOT_ESTIMABLE; no probabilities, option-derived spot proxies or Pine alerts invented.

All G1–G5 INCONCLUSIVE. Missing data, receipt/version history, corporate actions, official auction
closes, NBBO fill validation, genuine WFA and final holdout prevent any robustness verdict on edge.
No live-trading interface or indicator exists. Existing repository artifacts were preserved.

Phase A output: `results/20261010T034445993998Z`. Independent IBS output: `results/ibs_20261010T034458620111Z`.
Detailed blockers: DATA_ACCESS_BLOCKERS.md. Test XML, commands, dependency profile and hand-calculated
trace: results/verification/. No GitHub setup is required; lawful local data access is the next need.
