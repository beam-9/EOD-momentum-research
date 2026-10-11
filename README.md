# End-of-day momentum research

**Current verdict (2026-10-10 local): NOT_PROMISING on observed genuine development data at 3 bps/side; full robustness INCONCLUSIVE.** Real Alpaca SIP history and Phase A WFA now exist. All 28 active strategy/ETF combinations have negative net means. Fills remain proxies; skipped folds and explicit corporate-action input binding limit confirmation. See [reports/PROJECT_STATUS.md](/Users/beam.t/Documents/ChatGPT/trading/eod-momentum/reports/PROJECT_STATUS.md) and the latest stage reports before interpreting results.

This project implements the research contract in `experiments/HANDOFF_v3.md`, beginning with price-only SPY momentum and reversal, QQQ as a secondary replication, and simple baselines. It contains no live order interface. GEX, option and IBS utilities do not constitute completed empirical studies. TradingView deployment remains gated.

## Setup and exact replay

The project targets Python 3.11+; the installed and locked environment is **Python 3.12.14**. Use Python 3.12 for the exact lock (NumPy/SciPy versions require 3.12). Python 3.11 resolution is not verified. A local `.venv` is already installed in this workspace. GitHub is optional: it helps collaboration and versioned releases but supplies neither market data nor empirical validation. No paid service, broker trading permission or account change is required to run offline checks.

From the project directory:

```sh
cd /Users/beam.t/Documents/ChatGPT/trading/eod-momentum
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
PYTHONPATH=src .venv/bin/python -m pytest -q --junitxml=test-report.xml
.venv/bin/ruff check src tests
PYTHONPATH=src .venv/bin/python -m eod_momentum.cli --config config/default.yaml replay
```

The final command is the one-command replay. With no processed real data it writes a timestamped `results/` directory containing manifests, proposed folds, trial records, explicit blocked metrics and an inconclusive scorecard. Empty trade schemas and placeholders are **not zero-return backtests**. No performance charts are generated without observations. Tests use separately labeled fixtures; replay does not manufacture a synthetic market history.

## Acquire authorized data

The access check uses environment-variable presence without logging values:

```sh
PYTHONPATH=src .venv/bin/python -m eod_momentum.cli --config config/default.yaml data check --probe
PYTHONPATH=src .venv/bin/python -m eod_momentum.cli --config config/default.yaml data fetch
PYTHONPATH=src .venv/bin/python -m eod_momentum.cli --config config/default.yaml replay
```

`data check --probe` returns exit code 2 when neither credentials nor processed history exists. Historical missing-credential/401 attempts remain preserved; the 2026-10-10 local-env probe succeeded. Supply an existing lawful read-only data credential pair through your local environment: `APCA_API_KEY_ID` with `APCA_API_SECRET_KEY`, or `ALPACA_API_KEY` with `ALPACA_SECRET_KEY`. `.env.example` documents names; the CLI does **not** automatically load `.env`. Do not paste secrets into reports or commit them. The official Alpaca historical-data SDK is used; no trading client or order is created. Entitlement, feed and historical coverage must be verified by an actual successful request. A SIP request is not silently replaced by IEX.

Alternatively import a licensed user-supplied CSV/Parquet file:

```sh
PYTHONPATH=src .venv/bin/python -m eod_momentum.cli --config config/default.yaml data import --path /absolute/path/history.parquet --source YOUR_VENDOR --feed YOUR_FEED --timestamp-convention minute-start-utc
PYTHONPATH=src .venv/bin/python -m eod_momentum.cli --config config/default.yaml research run --phase A
```

Required columns: `symbol,timestamp_utc,open,high,low,close,volume`; UTC timestamps must be timezone explicit and label the minute **start**. Supply raw transaction prices, not adjusted history. Optional `first_available_at_utc` and `revision_available_at_utc` describe actual receipts. Without receipts, minute-end plus 30 seconds is explicitly an **assumption**, never observed latency. Finalized historical bars and minute-open fills remain `FILL_PROXY_ONLY`. The importer rejects marked synthetic data, duplicates, ambiguous timestamps and invalid price/volume data. Raw payloads/import files, normalized Parquet and SHA256 provenance are retained. DuckDB independently checks Parquet row counts.

For the explicit local-env preholdout access check/acquisition, use:

```sh
PYTHONPATH=src .venv/bin/python scripts/stage02_intake.py --acquire
```

For exact latest analytical reproduction against the retained local dataset:

```sh
PYTHONPATH=src .venv/bin/python -m eod_momentum.cli --config config/intake_2026-10-10.yaml research run --phase A
```

This overlay binds genuine corporate actions only and is explicitly `EXPLORATORY_PROTOCOL_CHANGED`; the frozen original remains unchanged. Do not rerun acquisition if you intend to reproduce the precise retained data hash.

## Frozen research protocol

`config/default.yaml`, `experiments/RESEARCH_PROTOCOL.md`, `registry.csv` and `protocol_lock.json` define the preregistration. Review them before acquiring or analyzing outcomes. Changed config/protocol/registry hashes are labeled exploratory; do not overwrite the original lock or move the holdout to improve outcomes. Historical target: 2023-01-03 through the latest fully completed XNYS session, initially 2026-10-09. Exclude early closes, incomplete sessions, invalid data and known action dates. Authentic action and auction catalogs are now retained; independent exhaustiveness, mapping gaps and original publication timing remain evidence limitations.

The feature uses the previous regular-session final-minute close to the 15:29 bar close (economic cutoff 15:30 ET). Decision is 15:31, primary entry 15:32 and exit 15:58. Both entry and scheduled exit require order submission strictly before eligible fill events. Final-minute closes are labeled proxies for official auction closes. The paper-style cutoff-to-close endpoint is reported separately from executable P&L.

There are **15 evaluated rules**: 13 fixed rules (flat, always long, always short, momentum/reversal at five thresholds each) and two validation-selected threshold procedures. The 100 fixed random-direction seeds form a diagnostic null distribution; they are not 100 independent discoveries or a seed search. All failed, inactive and selected variants stay in the trial ledger. Costs span 0/1/3/5 bps per side plus commission; selection uses 3 bps per side. Prespecified timing, double/triple friction and best-trade-removal scenarios are stresses, not optimization choices.

Rolling folds use 12 calendar months of training, three of validation and three of disjoint outer testing. Thresholds are selected on past validation only; deterministic rules need no fitting. Initial fold: train `[2023-01-03,2024-01-03)`, validation `[2024-01-03,2024-04-03)`, test `[2024-04-03,2024-07-03)`. The last complete planned test ends 2026-04-03. Every date interval is start inclusive/end exclusive. Final holdout starts **2026-04-10** and remains sealed. The latest run executes three SPY and five QQQ folds; actual OOS spans 2024-07-08–2025-10-02 with gaps. Holdout remains unevaluated.

Inference uses a seeded five-date circular block bootstrap with 2,000 replicates. Joint SPY/QQQ comparisons resample by date, preserving cross-asset dependence; they do not count both ETFs as independent daily evidence. HAC predictive regression remains distinct from trading metrics. DSR/PBO default to `NOT_ESTIMABLE` without defensible assumptions. No probability model has been validated.

After genuine development evidence, freeze a single rule and evaluate the holdout once:

```sh
PYTHONPATH=src .venv/bin/python -m eod_momentum.cli --config config/default.yaml holdout freeze --run /absolute/path/results/DEVELOPMENT_RUN
PYTHONPATH=src .venv/bin/python -m eod_momentum.cli --config config/default.yaml holdout evaluate
```

Freeze rejects absent/synthetic data, changed hashes and insufficient development evidence. Evaluation checks frozen code/config/data/protocol and creates an exclusive consumed marker before analysis; a failed attempt also consumes the untouched holdout. Do not delete seals to retry. These commands have not evaluated real history here and cannot establish deployability by themselves.

## Outputs and boundaries

Each `results/<UTC-run-id>/` contains configuration/code/environment/data manifests; session exclusions; all trial records; signals/trades; daily/fold/benchmark results; cost frontier; null diagnostics; stress tests; inference; `RESEARCH_REPORT.md`; and `robustness_scorecard.csv`. With real, sufficient history, the chart runner writes equity, drawdown/duration, costs, fold/year and conditional time-of-day figures. With absent data it writes `charts/NOT_GENERATED.md` instead. See the generated manifests for actual command context and coverage; filenames alone do not imply analysis ran.

Promotion requires every handoff gate to pass. The current scorecard has G3 FAIL and G1/G2/G4/G5 INCONCLUSIVE. Representative NBBO/arrival validation, official closes, corporate actions, immutable receipt/version history, untouched holdout and prospective evidence are unresolved. No Pine indicator, option-return translation, broker CFD replication or live-trading bot is delivered. `research run --phase B` or `C` fails explicitly at its data/protocol gate; their isolated utilities are tested only. `research run --phase D` runs the independent fixed-rule ETF IBS proxy, or writes a null-performance report without data. Its protocol is `experiments/IBS_PROTOCOL.md`: SPY 0.20/QQQ 0.10, known range by the 15:55 decision, 15:56 fill proxy, prior ATR(20), close marks, overnight gaps, open losses and configured financing. Delayed decision/fill scenarios are separate books. Continuous state is attributed by calendar MTM; it is not pooled with intraday WFA. Unknown corporate actions, exact CFD swaps/margin, quotes and intraday liquidation remain blockers.

## One-command verification

```sh
.venv/bin/python scripts/verify.py
```

This writes a new timestamped verification directory, runs pytest with XML output, lint,
dependency/compile checks, the read-only credential check, Phase A replay and gate report.
The access-check exit code 2 is an expected documented missing-access result.
For software-only reverification without probing data access or running economic replay:

```sh
.venv/bin/python scripts/verify.py --checks-only
```

Use `--output-dir /absolute/path/NEW_DIRECTORY` to choose a new evidence location;
existing directories are refused. Previous `results/verification/` evidence is preserved.
For an independent access check that preserves the original access report, append
`--report-path /absolute/path/NEW_ACCESS_REPORT.json` to `data check --probe`.
Run `.venv/bin/python scripts/benchmark.py` for a **synthetic engineering-only** week/year
profile; it does not benchmark actual vendor I/O or economic performance.
`results/verification/` retains commands, tests, profiles and the hand-calculated event trace.

For a configured IBS run:

```sh
PYTHONPATH=src .venv/bin/python -m eod_momentum.cli research run --phase D
```

Optional IBS configuration keys are `ibs_capital` (100000), `ibs_risk_currency` (1000),
`ibs_annual_financing` (0; ACT/365 proxy), and `ibs_max_mark_age_seconds` (60 at baseline).
These are assumptions; no broker historical financing or margin schedule has been acquired.
