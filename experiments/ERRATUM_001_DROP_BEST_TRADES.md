# Erratum 001 — best-trade removal diagnostic

Recorded 2026-10-10 America/Vancouver / 2026-10-11 UTC. Original frozen protocol, registry, config and lock remain unchanged.

The original Phase A implementation ranked every session by net return before selecting the best one/five observations to remove. A flat zero-return session can outrank a negative executed trade. Consequently, this did not consistently implement the registered “drop best 1/5 trades” stress. Removed trades also retained nonzero exposure minutes in the diagnostic metric input.

The user explicitly authorized correction and documentation, **without rerunning research**. `drop_best_trades(rows, count)` now ranks only executed records (`q != 0`), resolves ties by stable chronological input order, caps removal at the available executed trades, and changes the selected dates to flat observations with zero net/gross/fees/slippage/exposure. It preserves calendar dates and does not mutate the base book. Regression cases cover losing sparse books, ties, zero/fewer-than-five trades and source immutability.

Affected historical artifacts: the `drop_best_1` and `drop_best_5` rows of `results/20261011T044241208535Z/stress_tests.csv` and its exact reproduction `results/20261011T044703803065Z/stress_tests.csv`. These local files remain byte-for-byte unchanged and their affected rows are superseded as validation evidence by this erratum, **not recomputed**. Prior finalized reports are retained and must be read with this correction. All other historical outputs remain archived; the underlying primary-cost arithmetic does not use this diagnostic. No new economic interpretation or robustness promotion is made in this architecture stage.

Any future run must retain a new run ID, code hashes and this erratum identifier. It will not exactly reproduce the old diagnostic artifacts. A future protocol review must decide whether and how a corrected development run is authorized. Holdout since 2026-04-10 remains sealed. No economic runner was executed for this correction.
