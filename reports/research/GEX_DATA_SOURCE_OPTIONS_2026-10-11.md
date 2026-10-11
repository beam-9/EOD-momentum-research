# GEX historical and live data options

Research date: **2026-10-11 America/Vancouver**. Status: **PUBLIC_DOCUMENTATION_REVIEW_ONLY**. This report verifies vendor documentation, not this account's options entitlements, response quality, licensed storage rights, or historical coverage. No credentials, authenticated endpoints, purchases, subscriptions, trades, or sealed-holdout observations were used. No vendor below is approved for production or historical inference by this review. The GEX handoff was not available to this researcher when this note was written; this is a source inventory, not Stage 01 acceptance.

## What must be established before a source qualifies

The acceptance requirements below are research design recommendations, rather than claims that a vendor currently satisfies them. Obtain contract-level quotes or explicitly defined precomputed levels, economic/event timestamps, provider publication times, our receipt times, provenance and model versions. For raw chains require open-interest economic dates and availability times, expiry/settlement definitions, underlying marks, gamma units, contract multipliers and adjustment/deliverable records. Preserve missing values and original responses. A date label is not proof that data existed at an intraday decision time.

Treat OI-weighted gamma as an exposure model, not directly observed dealer inventory. A call-positive/put-negative sign convention is a hypothesis; neither OI nor a quote identifies who holds the other side. OPRA trades do not publish aggressor side, according to [Databento's OPRA guide](https://databento.com/docs/examples/options/equity-options-introduction/using-parent-symbology-to-fetch-an-option-chain). Inferring aggressor direction also does not establish opening/closing status or dealer ownership. Do not equate volume with OI, observed inventory, or newly established exposure.

For a proposed dollar-gamma-per-1%-underlying-move convention, the dimensional formula is `sign × gamma × OI × contract_multiplier × spot² × 0.01`, conditional on gamma being change in delta per dollar of underlying. This is a proposed unit definition, not a formula verified against any vendor response here. Preserve unsigned call/put contributions as well as any signed aggregation, and never combine a vendor's proprietary signed GEX with locally signed GEX without a reconciliation.

## Source options and documented capabilities

### Alpaca: existing provider, limited historical GEX foundation

Historical option data is documented from **February 2024**. The installed `alpaca-py` 0.44.0 implementation exposes historical bars/trades, but no `OptionQuotesRequest` or `get_option_quotes`; historical quotes were not established as an accessible capability. `opra` is the consolidated options BBO feed and requires subscription entitlement. `indicative` quotes are modified derivatives, while its trades are delayed 15 minutes; it is not an authentic OPRA quote substitute. [Historical options](https://docs.alpaca.markets/us/docs/historical-option-data), [SDK historical interface](https://alpaca.markets/sdks/python/api_reference/data/option/historical.html).

The historical-bars reference does **not** document a `feed` parameter. For endpoints supporting explicit feed selection, request it and reject silent fallback; otherwise mark the returned feed **UNVERIFIED**, rather than infer OPRA entitlement from HTTP 200. A bars request rejected for an unsupported `feed` parameter is not an entitlement denial. [Historical bars reference](https://docs.alpaca.markets/us/reference/optionbars). Account-specific probes belong in a separate evidence addendum, not this documentation inventory.

The chain endpoint `GET /v1beta1/options/snapshots/{underlying_symbol}` provides **latest** trades, quotes and Greeks, paginated up to 1,000 snapshots per response. `updated_since` filters latest quote/trade updates; it is not an historical as-of-Greeks query. The public documentation reviewed does not establish a historical Greeks archive or historical point-in-time OI series. [Chain reference](https://docs.alpaca.markets/us/reference/optionchain).

Contract metadata examples expose `open_interest`, `open_interest_date`, `size`, strike, expiration and style. The presence of an OI date does not establish its original publication or revision time, historical depth, or intraday freshness. [Options metadata documentation](https://docs.alpaca.markets/us/docs/options-trading). Greeks use Black–Scholes with convergence-related missing IV possible; this is a computed analytic, not an exchange-measured field. [Market Data FAQ](https://docs.alpaca.markets/us/docs/market-data-faq).

Live options use `wss://stream.data.alpaca.markets/v1beta1/{feed}`, MsgPack only, with documented trade/quote channels; wildcard quote subscriptions are disallowed and unauthorized feeds error at authentication. A streaming-Greeks/OI channel is not established by this page. [Live options](https://docs.alpaca.markets/us/v1.4.2/docs/real-time-option-data).

**Decision:** suitable candidate for an explicitly indicative demonstration or, if existing OPRA entitlement is actually verified, forward read-only quote collection plus timestamped chain snapshots. It cannot alone establish the required historical GEX dataset from the documentation reviewed. Existing successful equity SIP access does not prove options OPRA access. No current account permission was tested here.

### Cboe DataShop Option Quotes: strongest documented historical snapshot candidate

The product documents **January 2012–present**, one-minute or custom interval snapshots with NBBO, sizes, OHLC and volume, plus optional IV/Greeks and OI. Intraday file delivery is delayed **15 minutes**; daily files arrive overnight/next morning. Equity/ETF underlying bid/ask are included; index underlying licensing is separate. Early-close daily interval files can retain 16:00/16:15 delivery labels despite 13:00/13:15 closing quotes. A **June 22, 2026** quote-size capture methodology change must be recorded. Historical download and subscription are commercial routes; no purchase was made. [Product specification](https://datashop.cboe.com/option-quote-intervals).

Cboe's product explanation calls its optional OI **start-of-day OI**. The exact original publication/receipt and revision policy must still be established before point-in-time joins. [Optional OI semantics](https://datashop.cboe.com/data-product-replacement-option-intervals-combines-nbbo-bbo-quotes-calcs-into-one-product).

**Decision:** request a legally shareable sample/specification or use an already licensed user-supplied export before considering a bounded SPY/QQQ historical purchase. Public product availability does not grant this project access. Exact contract inclusion, expiration cutoffs, calculation version, gamma units, delivery clock, correction policy and storage/redistribution rights remain acceptance questions.

### Cboe Hanweck: legitimate licensed real-time analytics candidate

Hanweck supplies real-time IV and Greeks on equity, ETF, index and futures options. Its described model uses a binomial tree with discrete dividends, corporate-action reference data, intraday decay and borrow inputs. This is a different model family from Alpaca Black–Scholes and cannot be assumed numerically interchangeable. Public marketing does not establish this account's access, detailed timestamps, OI history, cadence guarantees, or permitted redistribution. [Hanweck analytics](https://www.cboe.com/services/analytics/hanweck/implied_volatility/).

**Decision:** institutional live-feed candidate if explicitly approved later. No vendor contact, licensing request or subscription was initiated.

### Databento OPRA.PILLAR: reproducible raw-feed route, not turnkey GEX

The feed documents exchange and consolidated BBO/trades, event and capture timestamps, daily statistics, adjusted symbology and historical/live differences. `ts_event` is OPRA consolidator processing time; `ts_recv` is Databento capture arrival, not our application's receipt. Before **2023-03-28**, data is subsampled: finest BBO is one minute, capture times are replaced with event times and flagged `F_BAD_TS_RECV`, and statistics are aggregated OI only. Expiration definitions are date-granularity UTC midnight, not actual settlement/last-trading clocks. Raw symbols must be retained because live/historical instrument IDs differ. Exact first available date and symbol/schema gaps require metadata verification. [OPRA specifications](https://databento.com/docs/venues-and-datasets/opra-pillar).

**OI is not absent:** the statistics schema includes outstanding-contract counts and event/capture timestamps; coverage is dataset-specific. General schema fields do not prove Greeks are available for OPRA, and no currently operational calculated-Greeks endpoint was verified. Local Greeks would require registered modeling, synchronized inputs and validation. [Statistics schema](https://databento.com/docs/schemas-and-data-formats/statistics).

Historical API metadata can establish availability and conditions; retrieval requires provider authentication. [Historical reference](https://databento.com/docs/api-reference-historical). **Decision:** strong raw reconstruction candidate if licensed inputs are supplied, with substantial modeling/storage work. Do not run chargeable requests or assume free credits. Earliest dates, cost, current entitlements, retention and derivative redistribution rights are **UNKNOWN** for this project.

### ThetaData: historical Greeks and OI through local Terminal

Published options tiers list Value minute history from **2020-01-01**, Standard tick history from **2016-01-01**, Pro from **2012-06-01**. Historical first-order Greeks require Standard/Pro; full `greeks/all` requires Pro. Free access is EOD-only; the page inconsistently describes one year/20 requests per minute in prose versus 2023-06-01/30 in its table. Do not silently pick either free-history/rate limit claim. [Subscriptions](https://thetadata.net/docs/Articles/Getting-Started/Subscriptions.html).

`/v3/option/history/greeks/all` requires the local v3 Theta Terminal, uses option/underlying midpoint calculations, supports intervals and limits multi-day requests to one month. [Historical Greeks](https://docs.thetadata.us/operations/option_history_greeks_all.html). OI is normally reported around **06:30 ET**, once daily, representing the previous trading day's close; absence of a new message is possible. [Historical OI](https://thetadata.net/docs/operations/option_history_open_interest.html).

Standard Greeks are Black–Scholes; binomial endpoints allow early exercise. Dividend parameters and versions matter: default dividend omissions must not be inherited silently. NDX underlying history before **2026-05-11** is not supported for these calculations. [Model documentation](https://thetadata.net/docs/Articles/Data-And-Requests/Option-Greeks.html).

**Decision:** credible bounded sample route if a user already holds compatible access and supplies Terminal/export. No Terminal/account was configured here. Exact live Greek refresh, timestamp zones/receipt semantics, multiplier treatment, publication revisions and license scope remain unverified.

### ORATS: historical/live modeled chain analytics

Historical EOD API advertises history back to **2007**. [Historical API](https://orats.com/docs/historical-data-api). Live one-minute chain history is documented from **August 2020** through one minute ago, with up to twenty trading days per range request. [Live intraday API](https://orats.com/docs/live-intraday-api). An archive-specific README instead begins its delivered one-minute archive **October 1, 2020**; delivery format and API history must be confirmed separately. [Archive README](https://orats.com/readme-1min.pdf).

**Decision:** credible modeled-history alternative, subject to credentials/license and explicit field audit (gamma, OI date/availability, quote/snapshot/update clocks, expiry settlement, multiplier, corrections). No source was purchased or queried. Different model inputs and delivery products cannot be merged by date alone.

### Precomputed GEX vendors

**SpotGamma:** official support explicitly says **a public API is not yet available**. EquityHub exports current stock-level data; product tier determines model availability. Current export is not a historical machine-readable archive guarantee. Do not reverse engineer internal endpoints or assume a third-party API wrapper is authorized. [Official API/export statement](https://support.spotgamma.com/hc/en-us/articles/50266085426195-Does-SpotGamma-have-an-API-Can-I-export-data).

**Trading Volatility:** v2 documents authenticated historical daily series, strike curves, expiry decompositions and levels. Full access requires subscription; the public demo is not evidence of licensed production coverage. [API v2](https://stocks.tradingvolatility.net/api/v2/docs). Its dashboard defines dollar GEX per 1% move, includes options below 94 DTE, and records a **May 15, 2025 model change**. Therefore historical values need model versions, not an assumed constant methodology. [Calculation notes](https://stocks.tradingvolatility.net/gexDashboard). Commercial API redistribution and personal-use restrictions differ. [Licensing descriptions](https://stocks.tradingvolatility.net/subscribe). Earliest exact historical day, intraday archive cadence, publication lag and retention were not established here.

**TradingFlow:** official material describes live/historical flow and GEX context, but this review found no public, versioned historical GEX API contract establishing machine-readable history, original availability clocks, units, retention or export license. Treat these capabilities as **UNKNOWN**, not verified or unavailable. [Official documentation](https://tradingflow.com/docs/), [GEX introduction](https://doc.tradingflow.com/product-docs/concepts/gamma-exposure-gex/intro-to-gamma-exposure).

### OCC: useful independent OI/reference evidence, incomplete GEX input

OCC documents a dated CSV daily-OI download route and a redesigned reporting site. This may provide a legitimate public audit source, but exact past-date retention, availability-clock history, contract granularity and automated-use rights need verification. This investigation did not download files. OCC OI alone supplies neither contemporaneous gamma nor underlying quotes and cannot establish historical GEX. [Daily OI](https://www.theocc.com/market-data/market-data-reports/other-market-data-info/batch-processing/daily-open-interest), [site changes](https://www.theocc.com/specialpages/whats-changed).

## Recommendation and approval decisions

1. **No-spend foundation now:** retain offline tests and timestamped input contracts; compute EMA and any explicitly labeled bar-volume-profile approximation independently of GEX. Missing authentic gamma inputs must leave confluence unavailable, rather than create proxy dealer levels or fabricated histories. Historical minute OHLCV does not establish true volume-at-price. Source inventory is complete enough for provider selection, not empirical acceptance.
2. **Read-only capability check next, if authorized within the final handoff:** a tiny explicit Alpaca OPRA query with existing credentials can establish actual entitlement. Keep any indicative fallback entirely separate. A live/latest chain observation cannot repair historical GEX gaps. New vendors require credentials supplied by the user or existing lawful files; this research made no such calls.
3. **Historical route requiring a decision:** choose Cboe Option Quotes with Greeks+OI, ThetaData, ORATS, or Databento raw reconstruction only after sample verification, development-period dates, model assumptions, timestamp semantics and licensing are approved. Exact budget requires an official bounded quote; no estimated costs or purchase recommendation is treated as approval.
4. **Live route requiring a decision:** choose verified Alpaca OPRA plus snapshot collection, a licensed ThetaData/ORATS/Hanweck source, or an explicitly licensed precomputed GEX provider. Confirm read-only storage/display/derivative rights, permitted persistence and commercial redistribution before deployment. No automatic renewal or subscription is authorized.

**Current blocker:** no authentic, point-in-time historical GEX-ready options dataset or verified live options entitlement was established by this public-documentation review. No strategy effectiveness, entry/target reliability or profitability conclusion can follow from these sources alone. Do not reopen or repurpose the sealed EOD holdout for provider evaluation.
