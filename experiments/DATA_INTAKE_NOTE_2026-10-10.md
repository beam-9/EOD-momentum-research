# Data input binding — 2026-10-10 America/Vancouver

Written before any real outcome analysis. Original config/default.yaml, RESEARCH_PROTOCOL.md, registry.csv and protocol_lock.json remain unchanged. config/intake_2026-10-10.yaml changes exactly one field: corporate_actions_path binds authenticated historical Alpaca actions. Cash dividends map by ex_date, never payment/process date. Existing exclusion of action dates and their dependent next-session prior-close feature is preserved. No strategy, threshold, timing, cost, universe, fold, seed or selection rule changes.

The existing checker will honestly label the augmented configuration EXPLORATORY_PROTOCOL_CHANGED because its digest includes the input path. It must not be called an exact frozen-config confirmation or used to consume the holdout. It is a documented input-binding variance that executes the original registered rules with the original prescribed action exclusions, not a retuned strategy. Retain all losing/inactive variants.

Auction access succeeded on a probe. Official-close history may be used for separate source/endpoint validation only; the frozen previous final-minute close and research endpoint remain explicitly labeled proxies unless separate outputs identify the official endpoint. No substitution changes signal definitions. Historical auction event times are not broker receipt times. Minute-open fills and additive friction remain FILL_PROXY_ONLY.

Missing action publication/version timestamps and independent action exhaustiveness limit G1. A successful historical bar/auction request does not verify NBBO, executable size, actual latency or live fills. All research stays development-only before 2026-04-10. No holdout freeze/evaluate is authorized.
