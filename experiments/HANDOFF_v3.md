# Codex Handoff v3: End-of-Day Momentum & IBS — Research, Backtesting, Walk-Forward Validation, and Indicator Deployment

**Status:** Final pre-implementation specification; **no market-data backtests or walk-forward runs have been executed by this handoff**.  
**Prepared:** 2026-10-09; **final preflight:** 2026-10-09  
**Target:** Python 3.11+ research repository, repeatable CLI pipeline, results and executive summary; only **after validation**, a non-repainting TradingView decision-support indicator and a separate Pine strategy parity check.  
**Instruments:** SPY primary; QQQ secondary; SPX/SPXW 0DTE only in a later phase with suitable option quotes. IBS is an explicitly separate mean-reversion benchmark; CFD results require actual CFD data.  
**Clock:** `America/New_York`; handle EST/EDT transitions via IANA time zone.  
**Latest eligible date:** most recent **fully completed** US market session when the pipeline executes; never include a partially completed trading day.

## Version 3: final decisions and launch order

**Retained from v2:** pre-registered hypotheses, immutable trial ledger, leakage-safe time rules, nested chronological walk-forward, honest cost models, qualified overfitting diagnostics (DSR/PBO), distinct IBS overnight benchmark, gated non-repainting Pine deliverables. **New in v3:** a concrete software architecture, vectorized-to-event-driven reconciliation, minimal working vertical slice, dependency/licensing choices, Tokyo auction correction, explicit execution decisions and a final launch readiness contract. An unsuccessful strategy is a valid research outcome.

**Execution priority:** **P0** = genuine 1-minute SPY/QQQ data, strict event-time integrity, simplest baselines, costs and WFA; **P1** = trial ledger, stress tests, bootstrap inference and data-backed scorecard; **P2** = IBS proxy, licensed GEX / 0DTE where data actually exists, optional DSR/PBO, indicator after gates. Never block P0 on P2 data access. For DSR/PBO, tests of invalid assumptions must result in `NOT_ESTIMABLE` rather than manufactured numbers.

### Read this first — non-ambiguous project contract

1. **Primary deliverable now:** a running, inspectable **Python research project** for SPY (primary) and QQQ (secondary), with genuine historical data where authorized, reproducible price-only baseline tests, chronological walk-forward, trade logs, leakage/quality tests and an evidence-based verdict. **No auto-trader.**
2. **Do not confuse hypotheses:** M1 predicts the **last half-hour** (tested with a realistically later entry); IBS buys near an intraday **low** and can hold for days. Compare them as separate horizons and risk exposures. Dealer GEX is a later, data-dependent increment.
3. **Start small:** pass an end-to-end Phase A vertical slice (data → as-of feature → model → time-ordered fill → P&L → folds → report) before adding optimization frameworks, ML, options, GEX, CFD replicas, dashboards or Pine.
4. **Success means evidence, not a required winner:** if no genuinely available dataset supports an executable conclusion, deliver working tested infrastructure and transparent blockers; synthetic fixtures are **tests only**.
5. **Cost policy:** no purchases, paid cloud jobs, subscriptions, broker integrations, credential disclosure, unlicensed scraping or real orders without separate explicit authorization. Existing lawful credentials may be used for read-only market data.
6. **Implementation choice:** Python 3.11+; Polars/Parquet/DuckDB for data; NumPy for calculations; **event-driven backtester authoritative** for final results; Numba or open-source VectorBT optional for screenings. Rust/C++/QuantConnect LEAN/NautilusTrader are not mandatory and must pass a measured cost–benefit assessment before adoption.

### Definition of a complete first milestone

Codex must be able to demonstrate, with **one documented CLI sequence**, a legitimate data-access check, import/fetch, session-quality audit, timestamp-correct 15:30 feature computation, M0/M1 models, event-driven 15:32→15:58 trades, cost sensitivity, non-overlapping OOS walk-forward logs, blocked final holdout until selected rule is frozen, tests and final PASS/FAIL/INCONCLUSIVE explanation. If real data is unavailable, deliver the same pipeline with clearly labeled **test-only synthetic fixtures** and no headline profitability claim.

## 0. Instruction to Codex

> Implement the research project described below, **starting with evidence and not a TradingView indicator or live-trading bot**. A TradingView indicator is a gated, final deliverable only if the strategy survives validation and its required data can be made available in Pine. Inspect the current repository first and preserve existing code. Prioritize the smallest **working, reproducible, leakage-safe** end-to-end version using accessible historical SPY/QQQ 1-minute prices. Obtain data when permitted and credentials are available, run the backtests and walk-forward analysis, save real results, and report findings candidly. Then implement the historical-GEX module only if **point-in-time GEX inputs** are available. Do **not** fabricate datasets, performance, GEX histories, option prices, fills, or backtest results. If data or credentials are missing, complete the working infrastructure/tests and write `DATA_ACCESS_BLOCKERS.md` identifying exactly what is needed. Continue with data-independent tests and any legitimate available data; do not stop at a design-only plan.

### Non-negotiables

1. **No look-ahead:** every signal and filter must be computable from information actually available before order submission.
2. **No data substitution masquerading as equivalent:** a price-only momentum model is not a paper replication; open-interest-based GEX is not observed dealer inventory; ETF returns are not 0DTE option returns.
3. **Two distinct performance endpoints:** (a) the paper-style approximately 15:30-to-close predictability endpoint; (b) an execution endpoint with verified data publication latency and **entry no earlier than 15:32 ET by default**, flattening around 15:58 ET. Earlier fills are sensitivity scenarios only with independently verified timing.
4. **Nested, chronology-safe walk-forward evaluation:** fit/select/calibrate on past train + validation only; no inspecting outer test folds or final holdout to change rules and then representing those as untouched.
5. **Cost-aware reporting:** report gross and net outcomes, uncertainty, trading frequency, and sensitivity to assumptions.
6. **Fail loudly:** incomplete quotes, stale data, unsupported calendar sessions, ambiguous bar timestamps, missing historical GEX, and data-provider access failures must not be silently imputed.
7. **Never place real orders or request brokerage API trading permissions.** Research/paper simulation only.
8. **Audit every experiment:** maintain an immutable model/threshold/trial ledger; incorporate unsuccessful trials into selection-bias assessments.
9. **A pretty indicator is not a valid result:** no probability badges, profitable claims, GEX labels, or trade alerts unless backed by out-of-sample calibration, verified live-accessible inputs, and reproducible Python↔Pine signal parity.
10. **Stop / no-trade is an acceptable outcome.** Negative findings and unavailable data must be explicit.

## 1. Research context: exactly what we are testing

### Original empirical motivation

- Heiner Beckmeyer and Mathis Moerke (2021), *End-of-Day Momentum in the Cross-Section and Option Hedging*, studies individual-stock price pressure during the **last 30 minutes** conditional on stock returns through 15:30 and option market-maker gamma.
- Barbon, Beckmeyer, Buraschi, and Moerke (2022 revision), *Liquidity Provision to Leveraged ETFs and Equity Options Rebalancing Flows: Evidence from End-of-Day Stock Prices*, studies both options dealer hedging and leveraged-ETF rebalancing.
- The papers' historical results do **not** validate a strategy on SPY, QQQ, SPX, or 0DTE option premiums. The project is an **out-of-sample extension**, not a claim to reproduce the published long-short equity results.

### Target research questions

**RQ1. Price-only:** Conditional on the return from the previous regular-session close to 15:30, is the remaining close-period price change predictably in the same direction? Does a reversal strategy do better?

**RQ2. Gamma interaction:** Are the relationships systematically different under estimated negative vs positive dealer gamma? Does signed estimated hedging *pressure* have additional predictive value beyond prior price direction, volatility, liquidity, and time effects?

**RQ3. Robustness:** Do the findings survive realistic execution assumptions, rolling walk-forward tests, regime variation, publication lags, alternative dealer-position conventions, and a completely untouched final holdout?

**RQ4. Options translation (later):** If historical executable option quotes are available, does a specified SPY/QQQ/SPXW intraday option strategy show positive net expectancy? Never infer this from spot returns alone.

### Expected directional mechanism (hypothesis, not an empirical conclusion)

- Dealers **short gamma:** price increases may require hedging buys; price falls may require hedging sells; potential continuation.
- Dealers **long gamma:** hedging may sell rallies and buy dips; potential mean reversion.
- Strong effects should plausibly depend on **estimated hedge demand relative to closing-session liquidity**, not raw GEX magnitude alone.
- Dealer inventory is generally **not directly observable** from public option open interest. Models must clearly label positioning assumptions.

## 2. Scope and priorities

### Phase A — MVP, mandatory

1. Data adapters for 1-minute adjusted/unadjusted as appropriate **regular-hours** price bars for SPY and QQQ, preferably consolidated SIP; persist raw payloads and normalized Parquet.
2. Exchange calendar/daylight-savings handling, bar completeness and provider quality checks.
3. Research endpoints and mechanical, non-optimized baseline strategies.
4. Rolling/anchored walk-forward test engine, costs, inference, plots and reports.
5. Unit/integration tests, synthetic **tests-only** fixtures, and working CLI.
6. Run against **genuinely acquired historical data** if possible.

### Phase B — historical dealer GEX, mandatory only when appropriate inputs exist

1. Historical point-in-time option chain, previous-night OI, Greeks/IV and spot snapshots with `available_at` timestamps.
2. Explicit GEX inventory-sign assumptions and sensitivity scenarios.
3. Hedging-pressure ranking and gamma-conditioned models.
4. Repeat exact testing protocol; contrast with Phase A.

### Phase C — tradeable 0DTE options, only with option NBBO and chain history

1. Historical point-in-time SPY/QQQ/SPXW option definitions, expiration styles, strikes, Greeks (if used for selection), and NBBO snapshots.
2. Option-contract selection before entry, conservative ask/bid executions, 0DTE risk rules and early exit.
3. Explicit comparison to underlying-based strategies with separate P&L columns and metrics.
4. No option-equity P&L estimates using assumed static deltas or observed option closing-price bars as fills.

### Phase D — IBS mean-reversion comparison, an independent benchmark

- Implement separately from the Beckmeyer mechanism: `IBS = (last_eligible_price - low_so_far)/(high_so_far - low_so_far)`; reject/skip a zero-range day, never divide by zero. Capture **range available by actual check timestamp**, not full day's high/low if the day has not ended.
- Reference rules supplied by user: at **15:55 New York** for US100, US30, US500 (US market days), or **15:25 Tokyo** for JP225 (Japan calendar): open long when IBS below thresholds of 0.10, 0.20, 0.20 and 0.30 respectively; on later eligible daily checks close when IBS > 0.50; one position per index; no stops/targets; default sizing corresponds to **1 completed daily ATR(20) adverse movement = 1,000 units of account currency**. Document this as a **third-party strategy description, not a proved recommendation**. If an entry and exit condition happen on a given bar, orders cannot fill before their actual decision time.
- **Same-event timing:** An IBS check at 15:55 or 15:25 is a *decision deadline*, not permission to know the final price/high/low of a bar that has not completed or disseminated. Apply the same `available_at` and after-submission fill requirements as M1; run +1/+2 minute decision/fill-lag stress tests and clearly mark 15:55 entries that could not fill before the cash close. For a post-2024-11-05 TSE cash proxy, do not assign a fill inside the 15:25–15:30 pre-close collection window as a continuous-market trade.
- **Instrument integrity:** US100/US30/US500/JP225 are often broker-specific CFD names. Only reproduce the user's broker-specific 2016–2026 claims with authentic **point-in-time CFD trades/quotes, spreads, point values, lot increments, financing/swap schedules, margin, contract revisions and live session calendars**. A QQQ/SPY/DIA/Nikkei ETF or index-price IBS test is a useful **proxy, not a replication**; label it accordingly. Do not assert that 'real historical spreads', financing or quoted slippage were tested without the relevant files and units.
- **Holding-period integrity:** the first daily check with IBS > 0.50 may occur many days later. Track open positions, overnight gaps, continuous financing/swap, corporate actions, maintenance margin, forced liquidation, and mark-to-market risk throughout holding periods. No stop is not a loss bound. ATR must be calculated using information genuinely available **before entry** (default prior fully completed daily bar). Gap/overnight exposure and ruin/margin-call risk are mandatory outputs.
- **IBS validation:** no mixing IBS trades with 15:30→15:58 intraday trades as if horizons were comparable. Align economic risk, capital, sample dates and exposure in common benchmark comparisons; separately assess overlapping multi-day labels and fold-boundary handling. Use historically correct Tokyo exchange-hour and closing-auction rules (see next bullet).
- **Tokyo timing correction:** The Tokyo Stock Exchange cash close was **15:00 JST through 2024-11-01** and **15:30 JST from 2024-11-05**. At 15:25–15:30 after the change, the TSE cash market is in **pre-close order acceptance, not ordinary continuous execution**. A historical “5 minutes before close” cash-market proxy therefore maps approximately to **14:55 JST before the change**, versus a **pre-auction 15:25 JST signal after the change**. Keep signal sampling, order acceptance and executable fill as separate timestamps. A broker's `JP225` CFD may have different quote/session and fill behaviour: require its actual historical contract specification and quotes; otherwise classify a JP225 result as an illustrative proxy. Source: https://www.jpx.co.jp/english/corporate/news/monthly-headline/202411.html
- **Source caveat:** Kakushadze & Serur's *151 Trading Strategies* (SSRN 3247865) describes ETF mean reversion as background; the Springer title is currently labeled **RETRACTED BOOK** (reason not established here). Neither source verifies the user's exact CFD rules or a claimed ten-year backtest. Use the IBS description as a testable externally proposed rule, not independent efficacy evidence.

### Phase E — indicator deployment and paper-forward monitoring (gated, later)

- Export only a **locked, validated** rule or a correctly calibrated probability model and its required features. Produce a Pine v6 **indicator** (decision support) and a separate Pine v6 **strategy** (platform parity simulation), not a broker bot.
- Include trading time, signal direction, historical-sample size, expected **net** edge, calibrated probability and confidence caveat, no-trade regime, and invalidation/time-exit where estimable. If no strategy passes, deliver a clearly labeled exploratory/research indicator with **no claims of profitable signals**.
- Verify that all inputs, especially GEX, auction imbalance and historical volatility metrics, can really be sourced via TradingView Pine. Pine `request.*()` can request supported feeds; it is **not a general arbitrary external HTTP-data client**. When unsupported, do not hard-code today's GEX into old bars or invent a Pine history. Provide an external dashboard or an explicitly manual/limited integration instead.
- Compare every historical Pine signal against an exported Python reference signal with precise ET date/time alignment. Check non-repainting on real-time vs reloaded charts, `request.security` confirmed-bar semantics, `lookahead_off` or documented safe higher-timeframe access, plot location and alerts timing. No future bar index or finished-day IBS high/low at a pre-close decision.
- Allow **paper-only shadow mode**, daily logging of generated signals/quotes as actually observed, and prospective tracking with zero retroactive feature revisions. Deploy only after forward-evidence review and explicit new user instruction for any live trading.

### Phase F — closer paper replication, optional

Build a 50–200-name historical liquid-equities cross-sectional portfolio and, if feasible, model leveraged ETF constituent flows. This matters because the source papers' core tests are cross-sectional rather than single-index binary signals. Requirements include *point-in-time* constituents/universes, survivorship-bias controls and historical liquidity.

## 3. Historical data, sources, feasibility and provenance

### Requested initial sample

- Target **2023-01-03 to most recent completed session**; extend earlier if the selected vendor offers quality data.
- Use 2023–2026 where available, without implying all feeds have that range.
- Run SPY and QQQ independently, then compare; never pool both as independent daily observations in confidence intervals.
- Record corporate actions, distributions, market holidays, half-days, feed, timezone, data limits and any gaps.

### Data-source priority / selection

| Need | Candidate | What it actually provides | Limitations / conditions |
| --- | --- | --- | --- |
| Historical 1-minute SPY/QQQ underlying | Alpaca historical stock bars | 1-minute OHLCV, with feed choice | Verify actual account access and **which feed** was returned. IEX-only data is not equivalent to consolidated SIP, especially for volume. |
| Consolidated underlying tape | Alpaca SIP, Databento US equities, another approved vendor | Higher-quality consolidated trade and possibly NBBO data | May require subscription/licensing; verify exact entitlement and historical coverage. |
| Historical option quotes/Greek/OI | Cboe DataShop Option Quote Intervals | Available 1-minute options snapshots, optional Greeks and OI; historical vendor coverage | Paid data; OI reflects prior night's clearing report, not dealer inventory. |
| Historical option NBBO | Databento `OPRA.PILLAR` | Historical consolidated options NBBO/definitions, including ETF and SPX contracts | Licensing and start-date limitations; OI/Greeks may require separate source/calculation. |
| Research paper | Beckmeyer/Moerke 2021; Barbon et al. 2022 | Mechanism and stock cross-sectional study designs | Do not port their historical returns to this new strategy. |

Official vendor/paper links (re-check availability at implementation time):

- Original 2021 paper: https://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2021-Leeds/papers/EFMA%202021_stage-2049_question-Full%20Paper_id-237.pdf
- 2022 expanded paper: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3925725
- Author's paper page: https://www.abarbon.com/papers/liquidity-provision-to-leveraged-etfs-and-equity-options-rebalancing-flows
- Alpaca historical stocks: https://docs.alpaca.markets/us/v1.1/docs/historical-stock-data-1
- Alpaca market data FAQ: https://docs.alpaca.markets/us/docs/market-data-faq
- Cboe option quote intervals: https://datashop.cboe.com/option-quote-intervals
- Cboe DataShop OI FAQ: https://datashop.cboe.com/faqs
- Databento options: https://databento.com/docs/examples/options/equity-options-introduction
- Databento historical options NBBO: https://databento.com/docs/examples/options/nbbo-resampling
- SPXW trading hours (validate current rules): https://www.cboe.com/tradable-products/sp-500/spx-options/spx-specifications

### Avoid overclaiming free data

Alpaca publicly describes free IEX-based stock feeds and SIP-access limitations, while older FAQ wording about delayed historical SIP access differs across pages. **Discover and verify the actual historical feed and entitlement by test request; do not assume SIP is free**. If only IEX is available, it can power a smoke test or a clearly labeled exploratory backtest; it does **not** validate consolidated-volume liquidity or professional execution assumptions. No historical point-in-time option-positioning source means **Phase B cannot be run legitimately**; do not use today's option chain to reconstruct 2023.

### Schemas

`underlying_1m`: `symbol`, `timestamp_utc`, `bar_start_et`, `bar_end_et`, `first_available_at_utc` (nullable when not historically observed), `assumed_available_at_utc` (nullable/modelled), `availability_basis`, `open`, `high`, `low`, `close`, `volume`, `vwap` (optional), `trades` (optional), `feed`, `source`, `retrieved_at`, `is_adjusted`, `quality_flags`. NEVER populate historically observed availability from an arbitrary backtest assumption.

`daily_sessions`: `date_et`, `regular_open_et`, `regular_close_et`, `is_early_close`, `prev_regular_close`, `official_regular_close`, `prev_close_source`, `session_quality`.

`option_snapshots` (Phase B/C): `timestamp_utc`, `available_at_utc`, `underlying`, `occ_symbol`, `root`, `expiry_date`, `option_type`, `strike`, `multiplier`, `exercise_style`, `settlement_type`, `bid`, `ask`, `bid_size`, `ask_size`, `last`, `iv`, `delta`, `gamma`, `open_interest`, `oi_asof_date`, `underlying_mark`, `source`, `quality_flags`.

`gex_snapshots` (Phase B): `asof_et`, `available_at_et`, `underlying`, `dealer_sign_model`, `included_expiries`, `signed_gex_dollars_per_1pct`, `estimated_hedging_dollars`, `closing_liquidity_dollars_reference`, `normalized_pressure`, `coverage_fraction`, `quality_flags`.

All persisted tables must identify the provider and the information-availability timestamp separately from the observation timestamp.

## 4. Exact timing and definitions (no timestamp leakage)

**Standard full session:** 09:30:00–16:00:00 ET. Half-days must be detected; initially **skip them** and report how many were excluded.

**Research cutoff:** `15:30:00 ET` marks the *economic end of the earlier-return interval*, not necessarily the instant of executable knowledge. The 15:29:00 bar covers 15:29:00–15:29:59 and is **not automatically disseminated or finalized at 15:30:00**. For example, Alpaca documents bar publication shortly after minute-end and subsequent updates from late trades. Explicitly store `bar_start`, `bar_end`, `first_available_at`, `revision_available_at` (when actual feed data exists), and `signal_decision_at`.

**Trade-decision default:** at `15:31:00 ET` use only observations known or *conservatively assumed available* by then; prohibit bars labeled 15:30 or later unless actual arrival timestamps establish availability. **Primary fill proxy:** earliest eligible marketable fill after decision, default 15:32:00 first eligible trade/open ± execution costs, **not the 15:31:00 open**. A 15:32 bar-open proxy is admissible only if the simulated order is sent **strictly before the first execution event** and remains eligible; otherwise advance to the next event. Using vendor-final historical bars without their original publication versions is a latency approximation, which must be flagged as such and stress-tested by delaying the signal one more minute. An alternative low-latency 15:31 entry is permitted only as a labeled diagnostic where as-of observation and decision timestamps validate it.

**Research endpoint:** `r_pre = P(15:30 cutoff) / previous official regular close - 1`; `r_close = official regular close / P(15:30 cutoff) - 1`. Identify the last trade strictly before 15:30 when tick data exists, otherwise specify the price proxy from the last completed 15:29 minute. Use the latest eligible economic mark and record its actual time. **Do not confuse historical observation time with live data availability.** This endpoint assesses conditional predictability only; it is **not** an executable fill assumption.

**Trade endpoint (primary):** submit after signal computation; default proxy buy/sell at **15:32:00 ET first eligible bar open** plus friction, issue the *scheduled exit order before 15:58:00* and flatten at **15:58:00 ET first eligible bar open** minus friction. Neither bar-open price is a guaranteed fill. Verify that the modeled order arrives before the simulated execution event; if that cannot be verified with minute bars, label the assumption and stress-test 1–2-minute delays. With consolidated historical NBBO, model executable side-of-market prices and size. Historical finalized bar OHLC alone cannot prove that exact open was available after simulated latency; flag `FILL_PROXY_ONLY` and downgrade deployability unless validated on quotes/ticks. Never pretend a session's 16:00 official close was a guaranteed fill.

**Diagnostics:** 15:32→15:45, 15:32→15:55, 15:32→15:58 and 15:32→15:59, plus a clearly labeled fast-execution 15:31 case **only if justified**; predeclare 15:58 as the primary intraday exit. Include 15:30/15:31/15:32 availability and 15:35/15:36 signal-lag sensitivity checks.

**Delayed signal check:** 15:35 signal and earliest later executable fill (e.g., 15:36–15:37, depending on bar publication assumptions), retaining 15:58 exit, as robustness for real-time computation/GEX latency.

**All stop/target logic:** default none. If introduced in a later version, use eligible next-event fills and explicit intrabar sequencing conventions. OHLC data alone cannot resolve the path if target and stop hit in the same minute; use conservative precedence or skip ambiguous bars.

**Prices:** signals and returns must use a consistent total-return or raw-price convention; for short intraday execution use tradeable raw prices; dividend/split handling is material for previous-close-based features. Explicitly flag ex-dividend gaps and rerun excluding them to avoid mistaken pre-close momentum.

## 5. Signals, benchmarks and parameter grid

First construct daily features **before** computing a trade decision:

- `r_pre`: previous regular-session close → latest available mark by 15:30.
- `r_morning`: 09:30 → 12:00.
- `r_afternoon`: 12:00 → 15:30.
- `r_1430_1530`: 14:30 → 15:30.
- `rv_lookback`: realized intraday volatility using only minutes through cutoff; specify a fixed lookback.
- `range_location`: 15:30 price in the available day's range up to cutoff (not full-day range).
- `dollar_volume_pre`: trading volume observed by cutoff.
- `closing_volume_reference`: mean last-half-hour dollar volume from **previous** N completed sessions, never from current post-15:30 volume.
- `event_flags`: only known-in-advance session/event data where available; no reliance on future realized news.

### Model M0: true controls

1. **Flat / zero-position** benchmark.
2. **Always long** SPY/QQQ, same entry/exit.
3. **Always short**, with clearly stated short-sale/borrow simplifications.
4. **Coin-flip/label-permutation** negative control (fixed seed, report distribution; not a tradeable model).

### Model M1: price-only momentum

- If `r_pre > theta`, long; if `r_pre < -theta`, short; otherwise flat.
- Start at **theta = 0** as the zero-tuning baseline.
- Compare a **reversal** mirror model: opposite trade direction under identical eligibility.
- Validation-only threshold grid: `theta` in `{0, 0.0025, 0.0050, 0.0075, 0.0100}` (absolute return; e.g. 0.0025 = 0.25%).
- Optional use `r_1430_1530` as a *separately labeled* lookback; do not change baseline definition after viewing results.

### Model M2: gamma-conditioned price direction (only if historical, point-in-time GEX available)

- Compute `direction = sign(r_pre)`.
- Given estimated net dealer gamma `GEX`, define `predicted_hedge_direction = sign(-GEX * r_pre)` (**dealer delta-hedge change direction**, not an observed order-flow label).
- `M2a`: momentum **only** on estimated negative-GEX sessions; otherwise flat.
- `M2b`: reversal **only** on estimated positive-GEX sessions; otherwise flat.
- `M2c`: trade in `predicted_hedge_direction`, allowing flat when the model is uncertain or magnitude below a validation-selected threshold.
- Include an **interaction regression** `r_close ~ r_pre + GEX_normalized + (r_pre * GEX_normalized) + controls` with temporally robust uncertainty; report coefficient signs/effects without claiming causality.
- For GEX sign ≈ 0, explicitly define a no-trade or ambiguous bucket.

### Model M3: normalized estimated hedging pressure (Phase B)

For each eligible option `i`, under a **stated dealer-position sign assumption** `s_i`:

`dollar_gex_per_1pct = SUM_i(s_i * option_gamma_i * open_interest_i * contract_multiplier_i * underlying_price^2 * 0.01)`

If `r_pre` is a decimal price return, approximate hedge-demand sign/magnitude under locally stable Greeks:

`estimated_hedge_dollars = -(r_pre / 0.01) * dollar_gex_per_1pct`

`normalized_pressure = estimated_hedge_dollars / expected_last_30m_dollar_volume`

Notes:
- This is a **modelled, linearized proxy**, not the paper's proprietary inventory measure and not an actual dealer-order forecast.
- The `0.01` factor denotes a one-percentage-point price move. Label units explicitly in code and reports.
- Where historical dealer directional inventories are unavailable, compare at least two coherent sign conventions and one sign-agnostic gamma magnitude measure. Do **not** treat call-OI-minus-put-OI signs as established truth.
- Reconstruct option Greeks at the historical underlying mark with a documented pricing method if Greeks are not purchased; document IV availability, time-to-expiry and 0DTE near-expiry numerical instability.
- Include *all relevant expirations* in the default exposure model and run separate 0DTE-only sensitivity; do not mistake a single-strike or single-expiry picture for net dealer gamma.
- Compare `normalized_pressure` against an unnormalized model; select threshold only using validation segments.

### M4: combined leveraged-ETF rebalancing proxy (optional)

Implement only with credible historical fund exposures/holdings, leverage ratios and point-in-time AUM/flows. Never claim a QQQ proxy perfectly reproduces the paper's LETF constituent-level flows. Keep this as a later, clearly distinguishable experiment.

## 6. Walk-forward, holdout, and anti-overfitting protocol

### Research preregistration, versioning and multiple comparisons (REQUIRED BEFORE FITTING)

- Freeze a human- and machine-readable `RESEARCH_PROTOCOL.md` **before analyzing strategy outcomes**. It must define primary asset, primary target, 15:32→15:58 execution window, costs, baseline model, metrics, sample dates, validation method, final holdout dates, model universe, data exclusions, and a finite experiment budget.
- Register candidate families (M0/M1/M2/M3/IBS), parameter grids, feature transforms, alternate signal times, exit times, filtration choices and threshold changes in `experiments/registry.csv`. Increment `trial_id` even if a trial fails or produces negative findings; mark **pre-registered vs exploratory**.
- Preserve exploratory findings separately from confirmatory findings. Never make exploratory OOS performance 'confirmatory' by renaming a split. Report how many unique variants were attempted (and any unlogged/manual trials) alongside the best result.
- Freeze file hashes for the final holdout, strategy code and parameter-selection logic at the time of final evaluation; testing only once does **not** mean after looking at holdout plots and reworking the code.

### Suggested structure

- Chronological sessions only; never shuffle.
- **Final untouched holdout:** reserve approximately the most recent **6 completed calendar months** if doing so leaves enough development data; mark and freeze holdout boundaries *before* exploratory model inspection. If insufficient, select a proportionate chronological holdout and document the compromise. Do not silently shift the holdout after seeing its outcome. A subsequent change consumes that holdout and requires genuinely newer prospective data for final confirmation.
- On preceding development period, **rolling** walk-forward folds:
  - Train: previous **12 months**.
  - Validation: following **3 months**, used to select signal threshold/hyperparameters from the finite prespecified grid.
  - Outer OOS test: following **3 months**, frozen once selected. The **inner** selection/calibration procedure must use only data occurring strictly before the outer test (with no label crossing the test boundary).
  - Step forward by **3 months**, rolling the train window. Optionally compare expanding train.
  - All training features and normalization statistics must come only from information available during the corresponding training period.
- If insufficient months for a fold, **skip** it transparently; do not reuse observations out of order.
- For simple deterministic baselines (theta 0), still evaluate on the exact same out-of-sample fold dates.
- After development, choose a **single frozen candidate rule** based only on development walk-forward tests/validation and inspect the untouched final holdout **once**. If holdout fails, report failure; do not retune on holdout and present a repaired score as untouched.
- Report both per-fold results and stitched **strictly out-of-sample** trading records, dates, parameter values, and coverage. Keep test periods **non-overlapping** when stitching. Fold-level model selection is allowed using only the immediately preceding training/inner-validation data; evaluation results from earlier outer folds may inform a predeclared adaptive rule, but not an unlogged manual search for a better final chart.
- Include an explicit record of every parameter family tested. Do not search arbitrarily wide grids or backfit numerous filters.

### Purging, embargo, and overlapping outcomes

- Each labeled prediction must carry `feature_available_at`, `decision_at`, `label_start_at`, `label_end_at`. Fixed same-day 15:32–15:58 intraday labels on **non-overlapping trading days** ordinarily need **no arbitrary multi-day embargo**; adding one without cause discards data needlessly.
- Where labels overlap split boundaries (e.g., IBS held days or options that span a later target window), **purge** training samples whose outcome windows intersect validation/test periods. Apply an empirically justified embargo only for serially carried state or adjacent leakage; document amount and rationale. Ensure any open IBS positions at a fold boundary are handled without crossing evaluation/training P&L or revealing their eventual exit to a past model.
- Cross-sectional stocks or SPY+QQQ same-day observations share a date-level dependency cluster. With longer holding periods, dependency may span several dates. Never treat 2 tickers × 250 days as 500 independent macro observations.
- Combinatorial Purged CV/CSCV can be added as an **overfitting diagnostic** when many candidates and adequate samples exist; it does not replace genuine chronological walk-forward or the untouched holdout. Avoid combinatorial permutations of time being mistaken for deployable OOS simulations.

### Statistical validation

- Compute mean session return and mean trade return with bootstrap confidence intervals **resampling by trading date**, keeping same-day SPY and QQQ together. Consider blocks of consecutive dates for serial dependence.
- For regression inferences, use heteroskedasticity and autocorrelation consistent standard errors (Newey–West/HAC), justify lag choice.
- Report estimated lift over the always-long baseline and M1 alongside absolute model performance.
- Implement **Deflated Sharpe Ratio (DSR)** as a secondary diagnostic only with documented observation count/effective dependence, return skew/kurtosis, candidate count and the dependence among trials. Prefer reporting **'not estimable/reliable'** to a dubious number when trials or samples are insufficient. Never replace fold-wise net P&L and confidence intervals with DSR alone.
- Estimate **Probability of Backtest Overfitting (PBO)** via combinatorially symmetric cross-validation on a **prespecified, aligned matrix of candidate strategy returns** only when enough independent partitions and alternatives exist. Label CSCV's time-combination limitation and show PBO uncertainty; do not portray its pseudo-OOS partitions as a real chronological forward test.
- If evaluating a sizable strategy zoo, optionally implement **White's Reality Check** or **Hansen's SPA** test using a block/bootstrap-based benchmark-differential matrix, with correct common dates and appropriately dependent resampling. Otherwise use simpler familywise/BH-style sensitivity disclosures and the complete trial ledger; tests must match the actual experiment family.
- Use a correction or candid warning for multiple hypotheses/models explored; show all tried variants in a model ledger.
- Include null/randomized controls with seed and distribution, **not** just a selected best random seed.
- Holdout and walk-forward metrics must be separated from any in-sample fit statistics.

## 7. Execution, slippage and P&L

### Execution realism and order-flow microstructure: prioritized tests

- Compare **trade-bar proxies vs actual bid/ask quotes** on a representative licensed subset; determine whether minute `open` is defensible given order-arrival time and volume. Specify market-vs-limit orders and pessimistic nonfill assumptions; model no-trade if a quote is stale or spread too wide.
- Separate bid/ask spread, commissions, slippage/latency, adverse selection and size-dependent market impact; count each component once. Use both fixed conservative sensitivity and (where measured) conditional costs by volatility, spread and volume.
- **Break-even cost frontier:** for each model estimate maximum allowable total round-trip costs for positive expected net return, and show whether it exceeds realistic quoted costs. Compute gross signal return distributions *before* assuming options leverage.
- **Auction microstructure:** distinguish continuous trading in the final minutes from the official closing auction. NYSE Arca (common ETF listing venue), NYSE and Nasdaq have different imbalance publications/cutoffs. An official closing print is not a guaranteed 15:58 executable price. If auction imbalance features are added, use only historically licensed disseminated data available **before the specific decision**, and create a separate post-15:50 model rather than leaking auction outcomes into the 15:30 model.
- Stress simultaneous adverse moves in SPY and QQQ, late-day spreads, extraordinary closing volumes, broker/platform delays, early closes, outliers and market halts. Test order size against reported quote depth / volume caps (with actual quotes) instead of infinite execution at a printed trade price.
- Do **not** presume a hypothetical broker's historical spread, OTC index CFD slippage, swap, margin or fees apply to SPY/QQQ ETF shares or SPXW options.

### Underlying SPY/QQQ trade simulator

- Primary underlying strategy holds at most **one position per instrument per session**; flat overnight; no pyramiding.
- Evaluate **unlevered notional returns** with position sign `q ∈ {-1,0,+1}`.
- Gross return = `q * (exit_price / entry_price - 1)`.
- Treat commissions and slippage as **per-side**, not round-trip; net return must explicitly subtract both entry and exit friction.
- Preset slippage sensitivity: `{0, 1, 3, 5}` basis points **per side**; baseline 1 bp/side is exploratory and **3 bps/side is the conservative robustness case**, not a certified fill model.
- If bid/ask quotes are available, implement spread-crossing buy-at-ask/sell-at-bid plus additional latency/market-impact assumptions. Do not double-charge spread under inconsistent models.
- Variable position size should not drive claimed alpha: primary returns should use constant notional per trade. Portfolio P&L should define whether both symbols can trade concurrently and account for overlapping exposure.
- Apply no-interest/no-borrow baseline only as a simplified model; disclose implications for shorting and compare long-only implementation.
- Return diagnostics must include number of eligible sessions, no-trade sessions, executed trades, market exposure, turnover and friction totals.
- No capital-constrained claims unless capital, fractional shares, commissions, margin, locate and financing assumptions are specified.

### Portfolio risk, position sizing and realistic opportunity cost

- Primary comparisons use normalized one-unit underlying notional; then separately simulate an explicit capital budget (e.g. paper portfolio), cash allocation, SPY/QQQ correlation, maximum simultaneous notional, long/short permissions, financing, and overnight vs intraday capital usage. Never imply a 1-bp ETF edge equals a 1% option return.
- For any overnight IBS or multi-day positions, model unrealized equity at every session, time-in-market, margin requirement changes, gap losses, overnight financing, broker-liquidation assumptions, max adverse excursion and risk-of-ruin scenarios; no stop is an **unbounded tail relative to the ATR sizing budget** for CFDs.
- Evaluate drawdown duration and **time to recovery**, largest 1%/5% losses, expected shortfall/CVaR, worst consecutive losses, and risk concentration on event days. Do not call leveraged CFD results capital-adjusted unless lot and margin specifications are exact.
- Benchmark the opportunity cost of idle capital vs a cash yield or simple passive exposure as a secondary economic comparison (using knowable point-in-time rates, not future rates). Compare strategies on matched session dates, net return **per eligible day**, net return **per executed trade**, and net return **per unit of committed capital**; IBS and intraday momentum cannot be fairly ranked using annualized trade returns alone.

### 0DTE option simulator (Phase C, with real option NBBO)

- Underlying signal derived without option-close leakage; choose 0DTE contract **at/after the entry time** from definitions already listed at that time.
- Prespecified primary selection: **nearest ATM call for long-up direction, nearest ATM put for long-down direction**, tie-break deterministically. Separately test delta target 0.40–0.55 only with point-in-time Greeks.
- Enter **long single-leg** option at contemporaneous **ask**, exit at contemporaneous **bid** by **15:55 ET** (earlier than the underlying exit). No short naked options or credit selling.
- Contract selection must be based on timestamped listings, never a reconstructed chain that includes strikes first listed later that day.
- Reject contracts with zero/stale quotes, crossed/locked markets, illiquid size, missing expiration details or excessively wide spreads; prespecify filter thresholds (e.g. quote age <30 seconds, spread/mid <= 20%) then sensitivity test stricter thresholds.
- Option quote intervals are snapshots/summary bars; if exact contemporaneous NBBO is unavailable, label the fill model an approximation and **do not** claim executable fill certainty.
- Account for actual 100x or adjusted deliverable multiplier, explicit option fees, per-contract commissions and quote-level slippage.
- Long premium max loss equals paid premium plus costs; estimate capital used and tail-loss risks separately.
- Exclude uncertain corporate-action/settlement contracts; implement SPY/QQQ ETF physical settlement vs SPXW European-style cash settlement correctly. Never model holding a same-day expiring option through settlement as equivalent to receiving a midquote mark.
- Do not optimize strike/delta, option exit, take-profit and stop-loss simultaneously on one small sample.
- If the relevant NBBO history is absent, **do not report any 0DTE option P&L numbers**.

### Options-only robustness requirements beyond price-direction accuracy

- Distinguish probability of an **upward underlying move** from probability that **a specific long call/put is profitable net of spread and theta**. Report call/put P&L and notional risk separately from underlying predictive accuracy.
- Analyze option IV, IV crush, bid/ask as a fraction of option premium, 0DTE theta/gamma path dependence, effective delta drift, discrete strike selection, minimum tick sizes, quote sizes and fees. Option payoff and loss after every realistic fill must use listed contract specs and option quotes; no extrapolation from stock close.
- Recheck SPX/SPXW vs ETF expiry, last trading, exercise/assignment/settlement and broker closeout rules before ever expanding beyond a fully flattened long-option test. Avoid carry-through-expiry when exact operational rules are missing.
- Dealer GEX: inventory sign remains a hypothesis unless supported by participant-position data; model cross-hedging into futures, offsetting expiries and time-of-day gamma changes. Run leave-out-one-expiry, alternate dealer sign, GEX magnitude vs normalized closing liquidity and stale-OI sensitivities, and **do not** imply OI updated intraday.

## 8. Data quality and mandatory leakage tests

Implement validations for:

1. Unique `(symbol, timestamp)` / `(occ_symbol, timestamp)` and monotonic time.
2. UTC ↔ ET round trips across DST boundaries and session opening/closing times.
3. Exchange holidays, half-days, missing minutes, halts, data vendor outages.
4. Consistent bar timestamp convention and actual price availability at signal cutoff.
5. No intraday feature uses any row after the relevant cutoff.
6. Rolling features use **only prior completed sessions**; proper lag for OI and historical holdings.
7. Clear adjustment methodology on ex-dividend and split dates; no future split-adjustment information silently interpreted as historical transaction prices.
8. GEX as-of/availability timing: historical chain recorded at or before cutoff, option OI timestamp from previous OCC nightly report when appropriate; forbid EOD option OI, Greeks or gamma curves reconstructed from later spot values.
9. Every simulated fill occurs **after** order decision; on a valid market session and in the specified open interval.
10. Options Greeks finite; 0DTE T approaches zero numerically; stale/locked/crossed/wide NBBO excluded.
11. Out-of-sample dates never overlap test/training and no preprocessing `fit()` sees test data.
12. Tests include a deliberate **future-information poison** fixture that proves the engine rejects data where `available_at > signal_time`.
13. Tests ensure a large **positive** previous price change under **negative** GEX implies **positive expected hedge direction** under the stated dealer hedging formula; invert scenarios too.
14. No made-up `Close[15:30]` alignment: test the 15:29 completed bar vs still-forming 15:30 bar and historical bar first-publication/revision latency. No bar-open 15:31 fills from an order decided at 15:31.
15. Causal prefix-invariance test: recompute signals after appending/randomizing future bars; **all earlier signals must remain byte-identical**; likewise test replaying historical trades online bar-by-bar vs a full-vectorized batch computation.
16. Calibrator/scaler/threshold fit only on training/inner-validation data; every classifier probability uses a dated, cross-fit or separate calibration segment.
17. Fold positions and multi-day labels (IBS) cannot leak eventual exit time across a validation boundary. Purge overlap, carry economic P&L correctly and never double count.
18. Random delayed-quote, spread spike, missing-bar, bad tick, venue-switch, halt, early close and broker-rejection fixtures trigger documented fallback/no-trade rather than forward-filled signals.
19. If optional Pine is produced, verify exported Python signal/reference parity and **non-repainting** under chart reload, higher-timeframe `request.security` and live/replay confirmation.
20. Reconciliation tests: share multiplier vs contract count, calendar P&L vs trade P&L, sum of spread/slippage/fees, and terminal equity. No unrealized multi-day losses hidden outside the trade log. Independently verify vectorized-screening ↔ event-driven canonical trade and cost parity on identical controlled fixtures.
21. 3:50/3:55 auction imbalance inputs may not appear in any 15:30 feature; non-point-in-time daily volatility/VIX open-close or economic surprise can't be a known-in-advance filter.
22. Deliberately malicious 'future price' feature and reversed bar availability timestamps must cause test failure, not artificially improved scores.

## 9. Main metrics and decision criteria

At a minimum report **per strategy, instrument, date range, fold, and horizon**:

- Number of sessions, number of trades, coverage, long/short split and traded-days fraction.
- Mean/median returns per trade and per eligible session; gross and net, with **per-side cost** assumption.
- Win rate and wins/losses sizes; expected P&L and profit factor with caveats.
- Annualized Sharpe (explicit convention, including how no-trade days are handled), Sortino and maximum compounded drawdown.
- Exposure, turnover, cumulative net-equity curve, monthly and quarterly returns, worst day, 5th percentile daily result, and consecutive-loss distribution.
- Time-of-day average conditional-return curves: positive vs negative `r_pre`, negative vs positive GEX where available.
- Difference vs price-only momentum, always long, always short, and no-trade; effect sizes and confidence intervals.
- A predictive statistic (e.g. sign hit rate, correlation/regression coefficient) **separately** from trade profitability.
- For any probability displayed in an indicator: **reliability/calibration curve**, Brier score and log loss versus climatology, performance and sample count in 5–10 prespecified probability bins, directional vs profitable-trade event definitions, and confidence intervals. A '68%' display requires a historically calibrated prediction; never derive it from a recent hit-rate bin with 7 examples.
- **Precision and uncertainty:** report independent-day/trade sample size, uncertainty of mean net return, breakpoint/cost frontier, bootstrap distribution of Sharpe, and where possible interval estimates of tail risk. For jointly trading SPY/QQQ, resample same calendar days jointly.
- **Stress testing:** latency +1/+2 minutes, 2×/3× modeled spread and slippage, missing favorable best trades, worst macro days, alternate feed, alternate exit by minutes, gap crashes, and instrument proxy differences. Put stress outcomes adjacent to the headline, not buried in an appendix.
- **Model-search correction:** best observed Sharpe, DSR diagnostic where valid, PBO diagnostic where valid, number of tested strategies, and explanation of statistical assumptions. Don't use a numeric DSR/PBO as a pass/fail certificate.
- Results across {0,1,3,5} bps/side and exit-time robustness.
- Distinct option-level metrics once Phase C exists: contracts traded, premium spent, average quote spread, commissions, option return distribution, and net dollar P&L on stated capital.

### Decision gates and robustness scorecard (predeclare, do not reverse-engineer)

A candidate may graduate to a *candidate research indicator* only if all hard gates pass:

- **G1 — Data:** traceable and fit-for-purpose history, credible availability timestamps; no critical missing sessions or undocumented approximations; paper-based price effect distinguished from executable P&L.
- **G2 — Leakage / trials:** passing causal and event-time tests, real chronology-safe nested WFA, experiment ledger, genuinely untouched final holdout; sample and trial count are reported.
- **G3 — Economic net edge:** positive estimated net expectation on stitched chronological OOS **and** conservative cost stress (e.g. 3 bp/side for liquid ETF proxy), over chosen flat/long/reverse baselines, with uncertainty interval displayed. A confidence interval spanning zero means 'inconclusive' unless separately prespecified.
- **G4 — Stability:** no sole profitable fold/month/event responsible for all profit; positive/negative regime decomposition and outlier dependence examined; reasonable signal retention under adjacent parameter values and moderate latency/cost changes.
- **G5 — Deployability:** each live input obtainable before decision from the actual intended platform, low repaint risk, realistic fills, sensible risk bounds; calibration adequate if presenting probabilities.

Add a `robustness_scorecard.csv` with gate-level PASS / FAIL / INCONCLUSIVE, exact evidence location, and unresolved limitations. **FAIL or INCONCLUSIVE on a hard gate means no claim of validated profitability and no live signal recommendation.** Do not tune arbitrary numerical cutoffs using final holdout results.

### Verdict rubric (do not target a magic Sharpe)

- **Promising:** multiple independent walk-forward folds show positive net expectancy at conservative cost, a useful confidence interval, reasonable trade count, and positive untouched holdout without changing the rules.
- **Inconclusive:** too few independent dates/trades, GEX unavailable, unstable feed, wide uncertainty, sign convention sensitivity, or profitability disappears under plausible costs.
- **Not supported:** effect is consistently absent, flips sign unpredictably, or is materially negative after costs. Say so plainly.

As diagnostic targets, aim for **at least ~200 independent out-of-sample trading dates and ~100 actual trades** for meaningful reporting; these are *minimum evidence guides*, not a promise of statistical power. If unavailable, report lower effective sample and avoid definitive conclusions. Trading dates, not ticker-day rows, are the independence unit when jointly trading SPY and QQQ.

## 10. Stratified analysis and failure investigation

Report all prespecified buckets (and counts) without fitting the bucket cuts using test data:

- SPY vs QQQ separately.
- Positive/negative/near-zero pre-15:30 daily return, and absolute move quartiles determined in training.
- Low vs high trailing realized volatility; rising vs falling day; above/below contemporaneously computable VWAP (if available).
- Day of week, month, quarter, options expiration/non-expiration.
- Half-day exclusions; known major scheduled macro days only if a reliable known-in-advance calendar exists.
- Negative, neutral and positive estimated GEX; strong vs weak normalized pressure; alternate dealer-sign assumptions.
- Pre/post major time intervals where sample coverage allows (2023, 2024, 2025, 2026).
- Scheduled CPI, FOMC, NFP, major earnings or monthly/quarterly OPEX, options expiration, quarter-end/month-end, index rebalance days **only with historically known schedule and event timestamps**. Add a leave-event-out ablation; not every source will expose all events, so label unavailable buckets.
- Intraday range quartiles, close-to-close trend vs intraday trend, prior 5-day direction, volatility-of-volatility, previous overnight gap, earnings-driven tech concentration, dealer gamma-flip proximity (only point-in-time), and liquidity stress **as a small, pre-registered subset**; avoid feature zoo mining.
- Event-day dependence: are results driven by a handful of the strongest trend days?
- Sensitivity to outliers: keep raw full-sample headline but report robust trimmed/winsorized **diagnostics**, not cherry-picked primary result.

## 10A. Predictive modelling / regime filters: only after simple benchmarks

- Begin with deterministic sign/threshold baselines and one interpretable logistic or regularized linear model if data suffices. Never start with dozens of ML architectures. Compare incremental information content via out-of-sample ablations: `(returns only)` → `+ volatility/liquidity` → `+ IBS` → `+ true historical GEX` (when available).
- Train conditional probability estimates **with only past data** and separately calibrate on past held-out segments (sigmoid or other justified calibrator); test stability across years. Calibrate *probability of the endpoint event*, not a generic 'chance trade wins', and separately estimate risk/reward/EV after costs.
- Threshold/no-trade gate should maximize a **predeclared risk-aware utility** (e.g. expected net return with constrained drawdown or log-utility) on training/validation, not on evaluation. Compare against probability = sample base rate and sign momentum, and include a neutral/no-trade class.
- Use feature stability and importance only as *diagnostics*; plausible economic explanation is a hypothesis, not causal proof. Avoid look-ahead feature rankings, hindsight-selected macro regimes and ex-post dealer GEX assignments.

## 11. Implementation requirements

### Architecture decision (normative, not a shopping list)

**Python 3.11+ is the orchestration and research language.** Optimize only measured bottlenecks. Avoid imposing Rust/C++, a paid terminal, a proprietary framework or a complex live-trading stack on a small daily-signal dataset.

| Layer | Preferred tool | Mandatory contract |
| --- | --- | --- |
| Immutable raw and normalized data | Apache Parquet (`pyarrow`), **Polars** lazy processing | Preserve provider payloads, provenance, schema versions, UTC timestamps, adjustment conventions and session quality. |
| Investigative queries | **DuckDB** on Parquet, not an always-running database server | Point-in-time joins using availability dates; deterministic session-scoped queries. |
| Signal calculations | **NumPy**, Polars, small pure Python functions | Deterministic `features_asof(cutoff)` and `generate_signal(features, frozen_params)` callable identically in research and replay. |
| Rapid candidate screening (optional) | **Numba** acceleration and/or **open-source VectorBT** | For screening **only**, explicitly shift signals after formation and reconcile with event-driven executions; never use paid VectorBT PRO features without authorization. |
| **Authoritative** transaction simulation | Small audited **event-driven Python engine** initially | Clock events, info-availability events, decisions, submit/acknowledge, fills/rejections, position updates, fees, risk, mark-to-market and explicit scheduled flattening. No fill before valid information and order arrival. |
| Independent engine choice (optional) | **NautilusTrader** or **QuantConnect LEAN** | Evaluate licensing, data adapters, reproducibility, correct ETF/order/CFD/option semantics and operational complexity first. If adopted, document why; do not run two incompatible truths. |
| Evaluation | `scipy`, `statsmodels`, `scikit-learn` | All preprocessing inside train folds; chronological outer folds and genuinely untouched final holdout; correct independent date clustering. |
| Charts/reporting | `matplotlib` + Markdown/CSV first; Plotly/Streamlit optional later | Report generated from saved reproducible real results; do not build a dashboard before validating data and P&L. |
| Deployment | Pine Script v6, only after locked validation | Exact signal-condition parity when inputs exist in TradingView; otherwise use a separately labeled Python decision dashboard. |

**A single canonical event record** shall have `event_id`, `event_time_utc`, `information_available_at_utc`, `event_kind`, `symbol`, `payload_source`, and stable ordering; order records also need `decision_time`, `submitted_at`, `eligible_at`, `filled_at`, `fill_price`, `size`, `fees`, `slippage_model`, `reject_reason`. Only persist observed timestamps as observed; modelled latency must be tagged `ASSUMED`.

**Engines must agree:** On the same test fixture with identical signals, fills, costs, rounding and position rules, vectorized fast screening must produce the same trades and daily P&L as the canonical event-driven engine within declared floating-point tolerances. If disagreement remains, block candidate promotion; the event-driven engine takes precedence until the discrepancy is resolved. Explicitly test neutral/no-trade days, session end, empty/partial sessions and delayed orders. **Do not rely on VectorBT defaults** for order fill timing, bar prices, intrabar paths or fees.

**Reasonable dependencies:** core `numpy`, `polars`, `pyarrow`, `duckdb`, `exchange_calendars`, `scipy`, `pandas` for adapter interoperability; optional `numba`, `vectorbt`, `statsmodels`, `scikit-learn`, `plotly`, `streamlit`, `nautilus_trader`. Pin dependency versions in a lockfile using `uv` or another standard packaging workflow; write a `pyproject.toml` with `core`, `dev`, `research`, `options` and `dashboard` dependency groups/extras as appropriate. Do not install everything or require API keys just to run unit tests.

**Scale policy:** profile wall time, CPU, memory and peak dataset volume on a representative 1-week and 1-year sample before parallelism or Rust. Document baseline speed. Optimize Parquet partition pruning, Polars lazy scans, signal caching and safe batch processing first. Any accelerator implementation must pass reference parity tests and deterministic reruns.

**Read-only data adapters:** avoid bespoke vendor SDKs if maintained official clients suffice. Respect rate limits, licenses and entitlements; no paid cloud account creation. Strongly prefer consolidated SIP/NBBO for final economic results. IEX-only bars, historical finalized OHLC and unobserved quote timestamps support **exploration**, not exact-execution claims.

**Engineering references (as of 2026-10-09):** https://docs.pola.rs/user-guide/concepts/lazy-api/ · https://duckdb.org/docs/data/parquet · https://vectorbt.dev/api/portfolio/base/ · https://nautilustrader.io/docs/latest/concepts/backtesting/ · https://www.quantconnect.com/docs/v2/lean-engine/getting-started .

### Minimal vertical slice before optimization

1. Download/import 2 trading days of genuinely licensed/accessible underlying bars (or fixture-only when offline); validate RTH, ET↔UTC and bar completeness, persist Parquet and quality report.
2. Compute only M0+M1 on prior-close-to-15:30 features; verify `available_at <= decision_time` and fill time after order eligibility. Produce a one-day traced event log that explains every input and order state.
3. Replay chronologically with simple constant-notional P&L; compare gross/0/1/3/5 bps per-side, explicit sign conventions and baseline to a hand-calculated unit-test case.
4. Add chronological train/validation/outer-test fold generator and pre-frozen latest-six-month holdout boundary; run with all eligible genuine bars. Record folds even if thresholds do not generate trades.
5. Add date-block bootstrap and robustness scorecard, then produce first genuine research report; only **after** this milestone expand to M2/M3/IBS/0DTE.

### Suggested repository structure

```text
eod-momentum/
  README.md
  AGENTS.md                         # concise instructions for future Codex runs
  pyproject.toml
  .env.example                      # names only, no credentials
  .gitignore                        # ignore credentials & licensed raw data
  config/
    default.yaml
    data_sources.yaml
    experiments.yaml
  src/eod_momentum/
    __init__.py
    cli.py
    calendar.py
    schemas.py
    data/
      base.py
      alpaca.py
      databento.py               # optional behind installed extras
      cboe_import.py             # imported files, not automatic piracy/scraping
      normalization.py
      quality.py
      cache.py
    features/
      price.py
      gamma.py
      pressure.py
      asof.py                      # point-in-time feature availability gate
    strategies/
      baselines.py
      gamma_models.py
      ibs.py                      # independent overnight mean-reversion benchmark
    backtest/
      events.py
      fills.py
      costs.py
      reconciliation.py           # event-driven vs screening parity
      engine.py
      options.py
    validation/
      walk_forward.py
      event_purging.py
      statistics.py
      calibration.py
      multiplicity.py            # DSR/PBO where samples permit
      scorecard.py
      leakage.py
    reporting/
      figures.py
      tables.py
      report.py
  tests/
    test_calendar.py
    test_price_bar_availability.py
    test_signs_and_units.py
    test_costs.py
    test_walk_forward.py
    test_purging_ibs.py
    test_probability_calibration.py
    test_ibs_units_and_financing.py
    test_prefix_invariance.py
    test_no_lookahead.py
    test_option_nbbo.py
    test_engine_parity.py
    test_event_ordering.py
    test_tokyo_close_change.py
    fixtures/                     # tiny clearly synthetic test data only
  data/
    raw/                          # gitignored
    processed/                    # gitignored
    manifests/
  experiments/
    registry.csv                 # include unprofitable/failed trials
    RESEARCH_PROTOCOL.md         # frozen predeclared outcomes
  results/
    <timestamped_run_id>/
      run_manifest.json
      data_quality.json
      walk_forward_folds.csv
      signals.parquet
      trades.parquet
      daily_pnl.csv
      baseline_comparisons.csv
      model_ledger.csv
      robustness_scorecard.csv
      execution_cost_frontier.csv
      calibration.csv             # when predicting probabilities
      multiplicity.json          # numerical where valid; explain if not
      data_provenance.json
      reconciliation_report.json
      environment_manifest.json
      metrics.json
      charts/
      RESEARCH_REPORT.md
  indicator/                     # create only after validation gates
    eod_indicator.pine
    eod_strategy.pine
    parity_test_report.md
  DATA_ACCESS_BLOCKERS.md          # create only when unresolved
```

### Packaging / dependency discipline

- Prefer `uv` or pip with a resolved, committed lockfile and `pyproject.toml`; verify clean installation under Python 3.11+ on macOS/Linux. Record exact package versions in each run. Keep dependencies licensed, available and compatible.
- Core storage/research: `polars`, `numpy`, `pyarrow`, `duckdb`, `exchange_calendars`, plus `pandas` for vendor interoperability if helpful; official `alpaca-py` or Databento SDK **only behind data-provider extras**.
- Validation: `scipy`, `statsmodels`, `scikit-learn` and relevant bootstrap/inference code. Codebase QA: `pytest`, `ruff` plus optional type checking.
- Optional acceleration/screening: `numba` and **community/open-source `vectorbt`**. VectorBT PRO is a separate commercial product; do not silently assume access.
- Optional dashboards/engines: `plotly`, `streamlit`, NautilusTrader or LEAN only when clearly justified and approved. Neither Rust nor C++ is required by default.
- Include `requirements` / `pyproject` constraints that allow **offline synthetic-fixture tests** without fetching broker data, connecting accounts or installing large UI/option stacks.

### Important additional engineering constraints

- Keep immutable `raw/` objects, original feed receipt/availability timestamps when possible, data vendor revisions and file SHA256; maintain **as-of** canonical tables rather than substituting today's corrected view of history as originally known.
- Avoid unlimited model/grid searches: cap parameter families and record any trial budget increase. Generate `strategy_definition.json` specifying entry, exit, lookback, calibration, risk and time conventions so both Python and Pine read the same locked decisions.
- Unit-test point/percent/basis-point conversions (SPY returns, SPX points, CFD index points, contract notional, ATR in price points vs account currency), including round-trip fees by *side*. Include a deterministic 3-minute hand-reconciled trace proving no same-bar signal fill, and an engine-parity test with a known trade ledger.
- Where provider history is only daily adjusted close or synthetic delayed quotes, explicitly label economic signal research only; do not produce executable minute-level trading results.

### CLI to implement

```bash
# Diagnose credentials and actual feed access; do not print secrets
python -m eod_momentum.cli data check --source alpaca

# Acquire/canonicalize underlying minute bars; download only eligible historical range
python -m eod_momentum.cli data fetch --symbols SPY QQQ --start 2023-01-03 --source alpaca

# Generate signal-cutoff features; reject missing/ambiguous sessions
python -m eod_momentum.cli features build --config config/default.yaml

# Run price-only strategies and walk-forward with costs
python -m eod_momentum.cli research run --phase A --config config/default.yaml

# Import licensed historical option snapshots and build model-based GEX
python -m eod_momentum.cli data import-options --path /path/to/licensed-files
python -m eod_momentum.cli research run --phase B --config config/default.yaml

# Independent IBS benchmark (ETF proxy if actual CFD history unavailable)
python -m eod_momentum.cli research run --phase D --config config/default.yaml

# Option P&L, only with valid historical quote data
python -m eod_momentum.cli research run --phase C --config config/default.yaml

# Validate and report gates before considering an indicator
python -m eod_momentum.cli research validate --config config/default.yaml

# Re-run tests
pytest -q
```

Adapt CLI details reasonably, but expose equivalent documented commands. Configuration must supply all user-adjustable dates/times/thresholds/fees, not code edits.

### Reproducibility requirements

- Persist config SHA256/hash, source IDs/links, data timestamps, Git commit, interpreter/dependency versions, random seed, data-quality exclusions and UTC acquisition time in `run_manifest.json`.
- Cache raw data; support resumable paginated fetch with rate-limit handling and incremental updates, then deterministic normalized transformations.
- Keep licensed vendor payloads private and out of Git; no credential values or full data keys in logs.
- Save **every** candidate and fold (including losers), not only the winning result.
- One command should regenerate all analysis artifacts from locally cached data.
- If no credentials/data: tests must run from tiny synthetic fixtures, but reports must clearly read `NO_REAL_HISTORICAL_BACKTEST` and must **not** display synthetic profitability as results.

## 12. Deliverables & acceptance tests

### Must deliver (MVP)

1. Working research code in repo with dependency installation and CLI.
2. `README.md` with setup, dataset coverage/permissions, exact timestamps and commands.
3. Genuine historical SPY/QQQ processed dataset **if legally/technically available**; explicit provider entitlement and feed description. `DATA_ACCESS_BLOCKERS.md` otherwise; synthetic fixtures cannot satisfy this real-data requirement.
4. Walk-forward-fold ledger + OOS trade journal, with zero-cost and cost-adjusted versions, preregistered objective, and complete trials registry.
5. `RESEARCH_REPORT.md` explaining performance, probability calibration where applicable, DSR/PBO validity or insufficiency, data-snooping controls, latency/quote realism, tail risks, final holdout and verdict.
6. Charts: cumulative net P&L, fold net-return comparison, cost sensitivity, breakeven-cost frontier, time-of-day conditional returns, per-year outcomes, drawdowns and drawdown duration, calibration plot if probabilistic, IBS overnight equity/underwater curve, optional gamma regime comparison.
7. Unit/integration tests and a passing test summary; include order-event traces, reference hand-calculation and vectorized/event engine parity. A failed core test blocks promotion.
8. `DATA_ACCESS_BLOCKERS.md` with exact vendor access/field/cost/data range needs if Phase B/C or true CFD IBS replication cannot proceed.
9. `robustness_scorecard.csv` with explicit deployable vs experimental verdict and gate evidence.
10. **Only after gates pass and after verifying Pine input feasibility:** an indicator design/export spec, optionally Pine code with signal parity tests; don't treat Pine as mandatory MVP if research fails.

### Codex run order

**Pass 0:** Inspect existing repository and preserve work; freeze a testable protocol and experiment ledger (primary timeframe, endpoints, sample, thresholds, costs, holdout, success gates); select Python + Parquet/Polars/DuckDB and the canonical event-driven execution contract. Validate actual provider entitlement and date availability. Do not start by installing large optional engines or writing Pine.
**Pass 1:** Implement the smallest vertical slice: 2 days of valid history (or clearly synthetic unit fixtures offline); trace feature `available_at` → decision → order → fill → ledger and prove parity with a hand-checked case. Establish calendar, normalized data contracts and leakage tests.  
**Pass 2:** Connect historical stock feed, fetch/cache genuine 1-minute SPY/QQQ where accessible, audit quality, implement M0/M1 signals and canonical **event-driven**, costed 15:32→15:58 Phase-A trading results; optional vectorized screening requires parity.  
**Pass 3:** Implement quote/latency-aware costs, sealed holdout and nested chronological WFA for Phase A, leakage/purge tests and bootstrap inference; generate costs frontier, reports, full trial ledger and robustness gates. Only after Phase A succeeds as a functioning research pipeline, add independently labeled IBS proxy, probability model and optional multiplicity diagnostics when defensible.  
**Pass 4:** Check for point-in-time options data in repo or credentials. If absent, add import interfaces, documented requirements and stop **only the unavailable phase**, not the completed core research.  
**Pass 5:** Where legitimately available, implement Phase B/C and true broker-specific IBS, re-run identical validation, update report. Do not portray proxy results as a vendor/broker-specific replication.  
**Pass 6:** Run tests and reproducibility check, inspect every result for leakage/survivorship and selection bias; provide results and failures, with a PASS/FAIL/INCONCLUSIVE deployment scorecard.  
**Pass 7 (strictly gated):** If evidence passes, export fixed rules, run Pine-vs-Python signal parity and repaint checks, and produce a paper-only indicator spec (not a live order bot).

### Completion checklist

- [ ] No observed result was synthesized or copied from the paper.
- [ ] Correct ET/DST and market calendar for every eligible session.
- [ ] Feature timestamps precede order/fill timestamps.
- [ ] Baselines including always-long/always-short/flat included.
- [ ] Gross versus net P&L and per-side costs are transparent.
- [ ] 3:30→close *research endpoint* not misrepresented as executable 3:32→3:58.
- [ ] True chronological walk-forward and untouched holdout.
- [ ] Confidence intervals and independent-session counts disclosed.
- [ ] Dealer GEX assumptions, source and publication lags documented.
- [ ] No fictitious 0DTE option P&L.
- [ ] Every threshold and all unsuccessful strategy families represented in an immutable experiment ledger.
- [ ] No use of minute bars before their conservative publication time; 15:32 primary entry unless justified otherwise.
- [ ] Purging/embargo applied **only where outcome windows actually overlap**; IBS overnight labels/financing accounted for.
- [ ] DSR, PBO, or equivalent multiple-trial warnings computed with honest sample constraints; no spurious precision.
- [ ] Data-quality/lag and realistic bid/ask, adverse fill and cost-break-even stress tests.
- [ ] Direction accuracy **not** misrepresented as options profitability; any probability signal calibrated out of sample.
- [ ] Distinct cost, margin, ATR and overnight-risk logic for any IBS CFD benchmark.
- [ ] Robustness scorecard explicitly determines **reject / research-only / paper candidate**.
- [ ] If Pine produced, Python ↔ Pine parity and no-repaint tests pass with supportable data sources.
- [ ] Reproducible CLI, output artifacts, tests and straightforward next-step instructions.
- [ ] Architecture justified: Python 3.11+ core, Parquet/Polars/DuckDB, canonical event-driven execution; no unnecessary Rust/C++/paid dependencies.
- [ ] Fast screening (if used) reconciles with canonical event-driven trades/P&L on controlled fixtures.
- [ ] Order submission timestamps strictly precede eligible simulated fill events, including scheduled 15:58 exit.
- [ ] Tokyo JP225 before/after November 5, 2024 respects both changing cash close and new 15:25–15:30 pre-close auction.
- [ ] No actual vendor latency fields invented from historical OHLC; modelled availability labeled assumed.
- [ ] README contains the exact one-command replay sequence, target coverage, real-data status, and known blockers.

## 13. Open questions for a *future* iteration (do not block phase A)

- Obtain adequate historical gamma estimates with credible **dealer inventory signs**, not just open interest; or test multiple explicit sign conventions and label the uncertainty.
- Whether SPY/QQQ options hedging is done via ETF shares, futures or correlated baskets, affecting whether single-ETF GEX predicts ETF shares over 30 minutes.
- Whether a true paper-style cross-sectional equities long-short strategy is preferable to SPY/QQQ intraday direction signals.
- Whether leveraged ETF daily rebalance pressure can be estimated from prior AUM, constituent exposures and fund returns without publication-time leakage.
- Whether the end-of-day intraday signal can be executed with realistic option costs, especially for 0DTE contracts close to expiry.
- Data budgets, licensing and intraday execution feed selection. **No purchases, account changes or live brokerage actions without explicit authorization.**

---

**Research integrity note:** Good-looking historical Sharpe ratios are not sufficient. The result must survive correct historical information timing, vendor quality checks, transaction costs, multiple-hypothesis disclosure and genuine forward evaluation. Conclude **not supported** or **inconclusive** when warranted.


## 14. Research bibliography and implementation implications (verified 2026-10-09)

The following are methodology **references**, not proof that any strategy here works. Add access dates in final project logs; keep any conflicting evidence visible.

1. **Beckmeyer & Moerke (2021)**, *End-of-Day Momentum in the Cross-Section and Option Hedging*. Primary microstructure motivation, **single-stock cross-section**; not direct SPX/QQQ option validation. https://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2021-Leeds/papers/EFMA%202021_stage-2049_question-Full%20Paper_id-237.pdf
2. **Barbon, Beckmeyer, Buraschi & Moerke (2022)**, *Liquidity Provision to Leveraged ETFs and Equity Options Rebalancing Flows*. Gamma and LETF hedging pressure, economic mechanism and original setting. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3925725
3. **Bailey, Borwein, López de Prado & Zhu (2015)**, *The Probability of Backtest Overfitting*. Motivation for complete candidate ledger and optional CSCV/PBO. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253
4. **Bailey & López de Prado (2014)**, *The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality*. Trial accounting and nonnormal performance. https://doi.org/10.3905/jpm.2014.40.5.094
5. **White (2000)**, *A Reality Check for Data Snooping*. Family-level benchmark superiority testing rather than winner-only inference. https://doi.org/10.1111/1468-0262.00152
6. **CFA Institute (2026)**, *Backtesting & Simulation*. Rolling WFA, structural breaks, scenarios, sensitivity, survivorship and look-ahead bias. https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/backtesting-and-simulation
7. **López de Prado**, *Advances in Financial Machine Learning*, Chapter 7 (purging/embargo): needed for **overlapping future-label windows**, not arbitrary multi-day gaps on non-overlapping day trades. Also see an implementation discussion: https://python.financial/concepts/purged-cross-validation/
8. **Alpaca (2022)**, *Stock Minute Bars*. Minute bar timestamp denotes **bar start**, initial publication ~1 second after minute end with potential later correction; backtest latency assumptions must reflect availability. https://alpaca.markets/learn/stock-minute-bars
9. **NYSE**, *Auctions*. Different NYSE/Arca closing auction imbalance schedules, official auction vs continuous session. https://www.nyse.com/trade/auctions
10. **Nasdaq Trader**, *The Nasdaq Opening and Closing Crosses*. 15:50 dissemination of Nasdaq closing imbalance; separately time-gate any new features. https://www.nasdaqtrader.com/trader.aspx?id=openclose
11. **Cboe**, *Volatility Insights: Evaluating the Market Impact of SPX 0DTE Options*. Inference about market-maker inventory and possible futures cross-hedging, not direct equivalence to OI-derived GEX. https://www.cboe.com/insights/posts/volatility-insights-evaluating-the-market-impact-of-spx-0-dte-options/
12. **Scikit-learn**, *Probability calibration*. Reliability curves plus Brier/log-loss for a probability display; probability of direction != probability of profitable option trade. https://scikit-learn.org/stable/modules/calibration.html
13. **TradingView**, *Strategies* and *Repainting* documentation. Platform broker emulator assumptions, limit fills, slip and confirmed-bar testing; parity and forward validation required. https://www.tradingview.com/pine-script-docs/concepts/strategies/ and https://www.tradingview.com/pine-script-docs/concepts/repainting/
14. **TradingView**, *Other timeframes and data*. Only permitted `request.*()` market/economic/other feeds; verify GEX import feasibility before promising Pine display. https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/
15. **Polars**, *Lazy API*: appropriate for efficient as-of feature construction and pruning. https://docs.pola.rs/user-guide/concepts/lazy-api/
16. **DuckDB**, *Reading and Writing Parquet*: columnar scans and projection/filter pushdown without an external database. https://duckdb.org/docs/data/parquet
17. **VectorBT**, *Portfolio API*: signal timing must be shifted to prices **after** signal computation; open-source package is a screening option, not fill authority. https://vectorbt.dev/api/portfolio/base/
18. **NautilusTrader**, *Backtesting*: Rust-backed, event-driven option, not a mandatory dependency. https://nautilustrader.io/docs/latest/concepts/backtesting/
19. **QuantConnect LEAN**, *Engine and CLI*: Python/C# support; assess data and paid-tier CLI requirements before selection. https://www.quantconnect.com/docs/v2/lean-engine/getting-started and https://www.quantconnect.com/docs/v2/lean-cli/backtesting/deployment
20. **Japan Exchange Group**, *November 5, 2024 trading hours change*: 15:00→15:30 and new five-minute closing auction; critical to JP225 cash proxy historical rule. https://www.jpx.co.jp/english/corporate/news/monthly-headline/202411.html
21. **Databento**, *OPRA.PILLAR dataset*: US options consolidated top-of-book and definitions; licensing and NBBO granularity must be verified. https://databento.com/docs/knowledge-base/datasets/opra-pillar
22. **Kakushadze & Serur (2018)**, *151 Trading Strategies*, SSRN description (including ETF IBS mean reversion): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3247865. **Important provenance note:** Springer publisher currently labels the book **RETRACTED BOOK** (reason not verified): https://link.springer.com/book/10.1007/978-3-030-02792-6. The user-supplied CFD rules are not treated as book-verified.

## 15. Codex final-report format — answer these questions explicitly

For every candidate model (not only the winner):

1. **Exact falsifiable hypothesis** and how its entry/exit differs from the published research.
2. **What actual data exists?** Providers, dates, coverage, market feed, point-in-time availability proof, cost and license assumptions, excluded sessions and limitations.
3. **What was actually executed?** Date range, Git commit, config hash, CLI invocation, tests, strategy candidates/trial count, walk-forward folds and untouched holdout status.
4. **What is profitable after realistic costs?** Estimated daily/trade net return, uncertainties, drawdowns, tail risk, trade count, cost break-even point and practical trade size constraints.
5. **Does it hold out?** Year/regime/fold performance, alternative feed, latency sensitivity, outlier exclusions, tests against no-trade/passive and opposite-direction baselines, search/multiplicity bias.
6. **Would probabilities mean anything?** Formal target, reliability calibration, sample count in signal bins and OOS calibration error, or explicitly 'probabilities not validated'.
7. **Can we trade/visualize it as specified?** Required real-time feeds (especially GEX and exchange-auction feeds), broker/platform limitations, Python/Pine parity and non-repainting tests, IBS overnight capital requirements.
8. **Final verdict:** `NOT_SUPPORTED`, `INCONCLUSIVE_RESEARCH_ONLY`, or `CANDIDATE_FOR_PAPER_FORWARD_TESTING`. This is **never** a guarantee of profitable live trading. Include a short list of the next *evidence-earning* steps, not another unconstrained parameter search.

**Final rule:** publish complete losing as well as winning results. A successful research project may conclude that **there is no robust edge in accessible data**; in that case, do **not** retrofit a profitable-looking indicator.

## 16. Launch readiness preflight: known constraints, explicit stop conditions

**What is checked in this handoff:** conceptual fit to paper and user-defined IBS; research-vs-executable endpoint separation; market/data-clock leakage risks; session/auction change; credible contemporary language/framework documentation; unlicensed-data constraints; feasibility of Phase A without historical options feeds; no broker order permissions. **No real-data download or actual trading backtest is claimed in this document.**

**Before any outcome analysis Codex must log:** repo state, market-data credentials/entitlements **without secrets**, accessible feed and earliest/latest historical timestamp, corporate action policy, whether historical NBBO exists, successful calendar/date coverage, SHA256 manifest, predeclared holdout boundaries, trial budget and pinned dependencies. If data is absent, **stop outcome claims**, not engineering work.

**Block `PROMISING` or deployable indicator status if any of:** `DATA_SYNTHETIC_ONLY`, `UNKNOWN_DATA_AVAILABILITY`, `FILL_PROXY_ONLY` without representative quote validation, `HOLDOUT_REUSED`, `TRAIN_TEST_LEAKAGE`, `INCOMPLETE_TRIAL_LOG`, `UNSUPPORTED_LIVE_GEX_INPUT`, `ENGINE_PARITY_FAILED`, or `COST_SENSITIVITY_FAILED`. Clearly distinguish a **research signal visualization** (permitted but labeled unvalidated) from a validated trade alert (strictly gated).

**Evaluation budget / stopping policy:** First run M0/M1 on SPY with a finite preregistered parameter grid and unchanged OOS methodology; QQQ replication is the secondary check. Cap expansion until baseline performance, uncertainty and cost frontier are reported. Implement IBS as an **independent** benchmark once basic engine and overnight bookkeeper work; GEX, option P&L, leveraged-ETF flows, richer ML and TradingView are *data/evidence gated*. Do not interpret more features or faster computation as proof of economic robustness.

**Codex's final response must include:** command(s) actually run; PASS/FAIL counts for test suite; real historical coverage and any excluded sessions; strategy/hypothesis count; training/validation/OOS/holdout date boundaries; numbers only if genuinely computed; precise missing-data blockers; links/paths to reproducible project outputs; definitive one-line status `NOT_SUPPORTED`, `INCONCLUSIVE_RESEARCH_ONLY`, `CANDIDATE_FOR_PAPER_FORWARD_TESTING`, or `NO_REAL_HISTORICAL_BACKTEST` when data does not permit a valid outcome conclusion.

---
