# TradingView and read-only GEX delivery feasibility

Public-documentation review, 2026-10-11 America/Vancouver. No Pine script, account configuration or live indicator was created. The requested new handoff/proposed README were unavailable, so these are constraints and proposed choices, not an approved implementation specification.

Pine's documented `request.*` functions access supported TradingView datasets; they do not document an arbitrary HTTP/WebSocket client for a private GEX endpoint. A Python backend is not automatically a `request.security` symbol. Treat unrestricted Python-to-Pine intraday ingestion as unsupported by the documented interface unless a legitimate TradingView-integrated data feed is established. Pine Seeds supports user-maintained **EOD** data, and new repositories are currently unavailable; existing seed feeds do not establish a new intraday GEX channel. [Official data requests](https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/).

TradingView webhooks send HTTP POST alerts **from TradingView to an external app**. They do not return a time series into Pine. A webhook-to-Python design therefore cannot by itself refresh Pine gamma levels. No webhook, alert or external message was created. [Official webhook documentation](https://www.tradingview.com/support/solutions/43000529348-how-to-configure-webhook-alerts/).

The current Pine documentation supports `request.footprint`; it is limited to one unique call and Premium/Ultimate users. Entitlement, coverage and profile parity still need verification. Do not claim Pine cannot access any footprint data based on older documentation. [Official limitations](https://www.tradingview.com/pine-script-docs/writing/limitations/), [2026 release notes](https://www.tradingview.com/pine-script-docs/release-notes/).

TradingView's volume profiles use lower-timeframe data, with calculation selection varying by indicator. Their high-volume nodes depend on session/range and row sizing. Python OHLCV bars cannot identify every trade's exact price. Allocating whole minute volume to a close or uniformly across a bar is an approximation, not verified trade-by-price volume. A future implementation must explicitly label its method and test volume conservation and prefix/as-of behavior. Exact agreement with a platform profile cannot be presumed. [Official volume-profile concepts](https://www.tradingview.com/support/solutions/43000502040-volume-profile-indicators-basic-concepts/), [Session profile](https://www.tradingview.com/support/solutions/43000703072-session-volume-profile/).

## Legitimate delivery choices requiring a later decision

| Choice | What it can support | Unresolved conditions |
|---|---|---|
| Python-owned read-only chart/dashboard | Licensed live GEX plus locally calculated indicators, levels, timestamps and stale-data state | Source rights, refresh policy, historical parity, output schema and operational verification |
| Manual Pine level inputs | User-entered GEX levels with explicit source/as-of labels; Pine-local EMA and permitted chart data | Manual refresh, historical version loss, no automatic vendor ingestion; never claim continuously live |
| TradingView-supported vendor/instrument feed | Pine reads a legitimate platform dataset if the provider actually offers it | Confirm actual symbol/fields, licensing and historical availability; no such route verified here |
| Existing Pine Seeds | Supported EOD feed already available to the account | New repository creation unavailable; unsuitable as assumed intraday bridge |

**Proposed preference:** build source-independent Python research first and preserve a read-only output interface. Decide presentation after data rights and handoff requirements are confirmed. No strategy, target reliability, non-repainting parity or deployment gate passes merely because a dashboard can display numbers.
