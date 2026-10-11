# Alpaca GEX-source access findings

Observed 2026-10-11 America/Vancouver with the existing local credentials. No new account, paid subscription, channel subscription, trade or holdout observation was created. Only source access/schema and authentication were investigated. Credential values are absent from this report and remain local.

| Probe | Exact request | Observed result | What it establishes |
|---|---|---|---|
| Initial option bars | GET /v1beta1/options/bars, SPY240308C00510000, 2024-03-08T15:00:00Z–15:01:00Z,1Min,limit1,feed=opra | HTTP400 | Request rejected; not proof of authentication failure or OPRA entitlement denial |
| Corrected documented option bars | Same parameters without feed | HTTP200; one bar at2024-03-08T15:00:00Z; next-page token present | This single historical contract/minute is accessible; no whole-chain or full-history coverage claim |
| OPRA live endpoint, authentication only | wss://stream.data.alpaca.markets/v1beta1/opra; connect, send auth, disconnect; no subscribe action | Connected; authentication returned error409 | This credential pair lacks access to the requested live OPRA feed under the current subscription package |

The historical bars reference has no feed argument, and the installed alpaca-py0.44.0 OptionBarsRequest has no feed field. The corrected request's actual feed remains **UNVERIFIED**, rather than silently treated as OPRA. The official reference lists bars parameters and pagination behavior. [Historical bars](https://docs.alpaca.markets/us/reference/optionbars).

Returned bar field names were `c,h,l,n,o,t,v,vw`. No historical gamma, Greeks or open interest field was returned. One bar with further pagination is an access/schema sample, not a complete development dataset. The raw response was retained locally at data/raw/alpaca/gex_documented_bar_probe_2026-10-11.json, SHA256f6a583e4106dc8792c8cab30e79a099e5966e9192a1c14a8cacd8cfcac89a407; it is excluded from Git. Prices were not analyzed or printed.

Alpaca's official WebSocket error table defines409 as “insufficient subscription.” That is an entitlement rejection, distinct from error402 for invalid authentication credentials. The test sent zero market-data subscription messages and requested no market prices; it proves neither live coverage nor end-to-end latency. [WebSocket errors](https://docs.alpaca.markets/us/docs/streaming-market-data).

Local immutable evidence: reports/evidence/gex_stage00_01_2026-10-11/alpaca_options_access.json, alpaca_options_bars_documented_request.json and alpaca_opra_auth_only.json, alongside the exact probe code. These contain sanitized diagnostics only. The first probe was corrected after consulting the official endpoint and installed SDK; previous evidence was not overwritten.

**Decision:** existing access is insufficient for a verified live OPRA-based GEX indicator, and the successful historical bar sample does not supply historical gamma/OI. Do not buy/activate a plan automatically. The owner can supply already licensed historical chains/GEX snapshots, confirm an existing authorized alternative source, or separately approve a provider/entitlement decision later. None of these actions was taken here. A generic account authentication success or equity SIP permission would not repair these distinct gaps.
