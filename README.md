# GEX Confluence Indicator — Research & Signal Validation

> **Project status (2026-10-11):** Stage 00 pivot foundation implemented; Stage 01 data qualification BLOCKED. A local read-only engineering demo is available; statistical validation remains pending. **No gamma-based trading edge has yet been established; no live signal service or automated trading exists.** The previous end-of-day price-only strategy study produced unfavorable development results after assumed costs. See [Project status](reports/PROJECT_STATUS.md) and [archived Phase A reports](reports/stages/STAGE_03_PHASE_A_DEVELOPMENT_2026-10-10_LOCAL_ENV.md).


## GEX levels, gamma flip, and confluence — research hypotheses

This project will test, rather than presume, whether **positive estimated dealer gamma** corresponds to lower short-horizon volatility, **negative estimated gamma** corresponds to higher volatility, **gamma-flip roots** identify meaningful regime transitions, and **call/put walls** or low-gamma-density corridors offer statistically useful target/support/resistance information.

A gamma wall is **not** a guaranteed ceiling/floor or take-profit fill. A large strike is evaluated against other large strikes, round-number and distance-matched controls. A flip is method-dependent (a fully re-priced portfolio zero-gamma root differs from a per-strike sign change). Sparse heatmap rows might mean **missing contracts rather than a gamma vacuum**. Public OI-based GEX does not reveal actual dealer inventories.

**Signal hypotheses:** a confirmed five-minute break/retest in a modeled negative-gamma regime with EMA 8/21/50 and pre-known volume-profile zones; a tested rejection/range setup during modeled positive gamma; a possible low-gamma corridor continuation only if chain coverage is complete; or **NO TRADE** when estimated regime, source data, or targets are uncertain. EMAs/HVN/POC/VAH/VAL are confluences **whose incremental predictive value must be proved**; levels are computed at or before the alert. Targets are **underlying price zones**, not option premium profit estimates.

See [the GEX research-direction handoff](docs/RESEARCH_DIRECTION_GEX.md) (installed v2 specification) for screenshot examples, primary Cboe and academic evidence, matched-control/falsification tests, data and portfolio sign caveats, and gated implementation stages. This README describes a proposal, **not a currently validated, tradeable signal**.


## Purpose

Build an evidence-based indicator that uses **estimated options dealer gamma exposure (GEX)**, **EMA 8/21/50**, and **high-volume nodes (HVN) / volume-profile zones** to identify possible bullish and bearish setups, define invalidation levels, and highlight plausible price target zones. The longer-term use case is manually evaluating **SPX/QQQ calls and puts**, including 0DTE contracts, but an underlying price signal is **not** an options-profit prediction.

The tool is intended to issue **CALL CANDIDATE**, **PUT CANDIDATE**, or **NO TRADE**, with explicit reasons and stale-data warnings. No guaranteed support/resistance, high-confidence badges without calibrated evidence, or live order placement.

## Research direction (new, not yet validated)

- **Gamma positioning:** compare estimated long/short dealer gamma regimes, 0DTE and broader expiry exposure, nearby gamma concentrations and model-specific gamma flips. Dealer inventory is not observable from open interest alone; all sign and flip definitions are labeled hypotheses.
- **Technical confluence:** confirmed 5-minute EMA 8/21/50 trend/reclaim context, with 1-minute context optionally used to inspect triggers.
- **Volume profile:** prior session POC, VAH/VAL, HVN/LVN and current *partial* session profile. Historical volume-by-price derived from 1-minute OHLCV is an approximation unless actual trade prints are supplied.
- **Trade planning:** explicit entry trigger, invalidation, underlying target zones, opportunity constraints, data-source timestamp and veto reasons.
- **Validation:** preregister a small set of hypotheses; show whether GEX adds incremental out-of-sample value beyond EMA or volume profile alone; model costs and event timing. Actual options P&L requires historical listed option NBBO with sizes/fees and expiry handling.

## Project architecture: implemented foundation and planned engines

**Python is the primary research and read-only signal engine**, using the existing Parquet/Polars/DuckDB data layer and verified historical execution infrastructure. A dependency-free loopback Python demo now displays explicit unavailable or TEST_ONLY fixture states. Gamma/EMA/profile calculations, signal generation and prospective monitoring remain planned, with modules for read-only option/GEX vendors, time-aware gamma estimates, five-minute EMA, causal volume profiles, alerts and experimental results. A future Pine Script v6 companion may overlay 8/21/50 and platform-accessible volume zones, plus *manually or legitimately available* external GEX levels.

**TradingView Pine Script does not generally call arbitrary external GEX REST/WebSocket APIs.** Native TradingView charts therefore cannot be assumed to display a truly live private GEX feed from Pine. TradingView webhooks send alerts outward, not gamma data inward. If seamless external GEX overlay is essential, use a separate Python chart/dashboard or investigate a properly licensed custom chart integration. Do not imply one is already deployed.

## Data roadmap

| Data | Current state / possible sources | Restriction |
|---|---|---|
| SPY/QQQ OHLCV | Existing private authenticated Alpaca SIP minute archive (2023–2026) | Raw vendor data is **not on GitHub** |
| Volume at price | Prefer historical underlying trade prints; start with visibly labeled minute-bar approximation | No backfilled current-session final HVNs |
| Historical GEX | Evaluate documented Quant Data GEX history/interval maps or compute independently from licensed Databento OPRA / Cboe DataShop chains | Verify as-of history, publication timing, sign models, licensing and cost |
| Current GEX | Evaluate a documented read-only GEX API and/or quote/OI based self-computed feed | Show delay, feed gaps, stale state, and model assumptions |
| Options trade returns | Later: actual SPXW/SPY/QQQ options NBBO, sizes, fees, expiry and settlement conventions | Underlying moves cannot substitute for option returns |

**Never** scrape undocumented proprietary endpoints or commit provider credentials, option tapes, restricted datasets or user trade journals. No API subscription/purchase without explicit approval. For vendor-capability research see the separate [GEX pivot handoff](docs/RESEARCH_DIRECTION_GEX.md) ; see the [actual feasibility audit](docs/GEX_DATA_FEASIBILITY.md) and [authenticated Alpaca findings](reports/research/ALPACA_GEX_ACCESS_FINDINGS_2026-10-11.md).

## Actual data findings and research records

- The renamed [GitHub repository](https://github.com/beam-9/GEX-indicator) was verified against baseline `32c843a`; local directory and legacy package names remain unchanged.
- Existing Alpaca credentials retrieved one genuine March 2024 option bar. Its feed is unverified and gamma/OI are absent; this is not historical GEX coverage. OPRA authentication returned **409: insufficient subscription**; no live channels or quotes were subscribed to.
- No primary GEX source is selected. Vendor capability documentation is distinct from tested account entitlement, point-in-time history, and storage/derived-work rights. No purchase was made.
- [New protocol DRAFT](experiments/gex_v1/PROTOCOL_DRAFT.md) and [trial inventory](experiments/gex_v1/registry.csv) are separate from the old frozen study. No new economic trials have executed. GEX D0 provenance remains BLOCKED; D1 is not yet evaluated.
- [Stage 00 report](reports/stages/GEX_STAGE_00_PIVOT_AND_HYGIENE.md), [Stage 01 report](reports/stages/GEX_STAGE_01_DATA_FEASIBILITY.md), [pivot decision](docs/PIVOT_DECISION_2026-10-11.md), [screenshot dictionary](docs/GEX_SCREENSHOT_FIELD_DICTIONARY.md).
- Earlier missing-document preflight notes are preserved under `reports/gex/`; their missing-v1 blocker is superseded by this installed v2 specification.

## First implementation milestones

1. **Pivot and preserve** — new research decision record and GEX protocol; keep original Phase A lock and test reports unmodified; update README and reproducible project status.
2. **Data feasibility** — compare historical vs live GEX providers with small authorized non-economic samples, timestamps, per-root coverage, and terms. Select primary data source or document BLOCKED.
3. **Causal feature engine** — validate gamma units/model sensitivity, 5m EMAs, and prior/partial volume profiles; show read-only dashboard with **DATA UNAVAILABLE** when feeds are missing.
4. **Robust backtesting** — strictly chronological GEX-only/EMA-only/HVN-only and small confluence comparisons; all candidates, costs and losing cases retained; sealed Phase A holdout remains untouched.
5. **Paper-forward advisory indicator** — stable data source and prospective logs before production claims.
6. **Separate real options execution study** — genuinely executable option bid/ask P&L only after signal evidence.

See [`reports/PROJECT_STATUS.md`](reports/PROJECT_STATUS.md) for actual stage completion. A planned milestone is not an accomplished backtest.

## Historical research: Phase A — end-of-day momentum (preserved archive)

The original `End-of-day momentum research` aimed to predict 15:32–15:58 ET SPY/QQQ returns with 15 preregistered price-only momentum/reversal/benchmark rules. On development-period authentic Alpaca SIP prices, **all 28 active rule-by-ETF combinations had negative mean returns at the modeled 3 bps/side execution cost**; G3 economic edge **FAILED**, while G1/G2/G4/G5 were inconclusive. 3 of 8 SPY folds and 5 of 8 QQQ folds ran due to the predeclared coverage policy. A separate erratum corrected a best-trade-removal diagnostic **without re-running original economic tests**.

- [Frozen Phase A research protocol](experiments/RESEARCH_PROTOCOL.md)
- [Phase A report](reports/stages/STAGE_03_PHASE_A_DEVELOPMENT_2026-10-10_LOCAL_ENV.md)
- [Evidence review](reports/stages/STAGE_04_EVIDENCE_REVIEW_2026-10-10_LOCAL_ENV.md)
- [Stage 05 architecture review](reports/stages/STAGE_05_ARCHITECTURE_AND_PUBLICATION_2026-10-10.md)
- [Erratum 001](experiments/ERRATUM_001_DROP_BEST_TRADES.md)
- [Archived results](results/20261011T044241208535Z/RESEARCH_REPORT.md)

**Research-integrity requirement:** The earlier **2026-04-10 onward sealed holdout remains sealed and unavailable for casual tuning**. This new GEX direction requires its **own** preregistration and explicitly defined datasets/holdouts; do not reuse the older holdout or overwrite the previous protocol because the focus changed. Prior price-only results neither validate nor refute a full gamma-conditioned hypothesis.

## Repository setup / developer safety

Python 3.12 is used for the existing pinned `requirements.lock` environment; preserve legacy commands for the original CLI. From the **actual local project root** (do not assume it was renamed on disk):

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python scripts/verify.py --checks-only
.venv/bin/python scripts/check_publication.py --staged --history
```

Detailed existing instructions remain in [repository publication rules](docs/PUBLICATION.md). Run the read-only local demo (from this project root, no credentials or market data read):

```bash
PYTHONPATH=src .venv/bin/python -m gex_indicator.ui --port 8765
# Optional engineering fixture; every displayed value is synthetic:
PYTHONPATH=src .venv/bin/python -m gex_indicator.ui --port 8766 --test-fixture
```

Open `http://127.0.0.1:8765` (or port 8766). Default output is DATA_UNAVAILABLE / NO TRADE. Fixture mode is TEST_ONLY / NO LIVE GEX; it does not calculate gamma or infer signals. Stop with Ctrl-C. No provider adapter or live signal command is implemented. Never publish `.env`, private keys, licensed market data, authenticated vendor payloads, or raw personal trading information. Enable hooks locally: `git config core.hooksPath .githooks`. Historical source/version tags must remain intact.

## Reporting contract

Each implementation stage must publish `reports/stages/GEX_STAGE_XX_*.md` (PASS/PARTIAL/BLOCKED/FAIL), update `reports/PROJECT_STATUS.md`, and record specific code/data hashes, available-at timestamps, executed tests, results including failures, uncertainty, stale-feed episodes and exact next action. **No real data means no historical GEX backtest**, regardless of how polished the indicator looks.

## Research and data references

- [Cboe — option market-maker gamma hedging](https://www.cboe.com/insights/posts/volatility-insights-evaluating-the-market-impact-of-spx-0-dte-options/)
- [Databento OPRA option data](https://databento.com/docs/examples/options/equity-options-introduction/using-parent-symbology-to-fetch-an-option-chain)
- [Cboe DataShop interval quote product](https://datashop.cboe.com/option-quote-intervals)
- [Quant Data GEX API](https://help.quantdata.us/en/articles/15807345-gamma-exposure-gex-api-python-quickstart-dealer-positioning-guide)
- [TradingView volume-profile definitions](https://www.tradingview.com/support/solutions/43000502040-volume-profile-indicators-basic-concepts/)
- [TradingView Pine request and footprint docs](https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/)

**Research use only.** No investment-performance claim, real-time GEX authorization, charting-library entitlement, or options execution is implied by this repository.
