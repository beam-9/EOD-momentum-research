# Sources and interpretation

Implementation reference access: 2026-10-09 America/Vancouver. These describe provider
semantics and the research design, not efficacy evidence. No financial recommendations follow.

- User-supplied authoritative specification: `experiments/HANDOFF_v3.md` (unaltered copy).
- [Alpaca stock minute bars](https://alpaca.markets/learn/stock-minute-bars): minute-start
  labeling, publication after minute end and possible later updates. A modeled 30-second
  delay is our sensitivity assumption, not observed historical receipt timing.
- [Alpaca market-data FAQ](https://docs.alpaca.markets/us/docs/market-data-faq): explicit feed
  selection and minute timestamp convention. IEX is not consolidated SIP evidence.
- [Alpaca historical SDK](https://alpaca.markets/sdks/python/api_reference/data/stock/historical.html):
  read-only historical bar client used here. No broker trading client is instantiated.
- [Alpha Vantage API documentation](https://www.alphavantage.co/documentation/): historical
  intraday access requires appropriate premium access. No subscription or credential was obtained.
- The source papers, JPX timing correction, and complete bibliography are preserved in the handoff.
  Paper returns were not copied into results, and neither ETF strategy is claimed as paper replication.

All numerical output here must derive from local input manifests. Tests use synthetic fixtures
with a separate test-only label. Lack of market data is a missing-evidence condition, not a zero return.
