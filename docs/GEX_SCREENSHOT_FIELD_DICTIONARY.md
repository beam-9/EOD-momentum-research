# GEX screenshot reference field dictionary — 2026-10-11

**Source limitation:** actual screenshot image files were not supplied to this documentation task. The values below are transcribed from Section 3.1 of the user's v2 handoff, not independently read from pixels, authenticated market observations or current prices. They are UX/schema examples only, **never admissible historical training or outcome samples**. Screenshot identity, vendor, capture time/timezone, data as-of, rights and algorithms require verification before any source use. No current strategy, alert or market inference is drawn from these examples.

| Handoff-transcribed field | Meaning permitted for documentation | Provenance/uncertainty required | Prohibited inference |
|---|---|---|---|
| A instrument SPY, displayed spot $780.50 | Provider-displayed instrument/spot in illustrative snapshot | Instrument ID, spot feed, event/publication/receipt time, currency | Current live price, SPX equivalent, executable fill |
| A call +$25.1B, put −$17.3B, net +$7.8B | Reported model-signed gamma quantities; arithmetic 25.1 − 17.3 = 7.8 | Exact dollar-gamma convention/scale, contracts/multipliers, expiry scope, sign/inventory model | Actual dealer inventory or inevitable price direction |
| A “total” $42.4B | Displayed gross-like aggregate; arithmetic 25.1 + 17.3 = 42.4 | Confirm provider meaning of “total,” units and aggregation | Treat gross absolute value as net signed exposure |
| A Call Wall $785 / Put Wall $755 | Provider-defined candidate level types | Formula, rank/metric, chain completeness, expiry/filter, snapshot hash | Guaranteed resistance/support, target fill or largest-wall superiority |
| A Zero Gamma $776.27 | Provider-named level, methodology unverified | Portfolio repricing root versus other method; IV/sign assumptions, stability/root count | Automatically equate with neighboring strike-bar crossing, above=calls/below=puts |
| A 0DTE share 0.0% | Displayed filtered snapshot share | Exact expiry date, local clock, denominator/filter/rounding | Same share next session; no near-expiry positioning |
| A strike histogram colors and spot line | Visual model/strike contributions | Color legend, units, sign convention, full strike grid | Green/red proves dealer ownership or hedge direction |
| A strike × expiration heatmap | Handoff describes GEX-like dollar cells, not independently verified | Each cell's `metric_kind`, `metric_unit`, call/put `contract_type`, strike, expiry, `as_of`, `model_id`, publication/receipt | Mix expiry scopes or infer missing cell means zero gamma |
| B highlighted 129,473 at strike 785 for Oct 16 | Unlabeled count from separate handoff-described matrix | Vendor, asset, year, legend/unit, contract type, model and times unknown | GEX dollars, actual market-maker contracts or signed inventory |
| A/B crosswalk | No merge currently permitted | Verified same asset/time/units/contracts/expiry and inventory-model crosswalk | Join by strike number alone or use screenshots as a historical level series |

The handoff describes A as above its displayed zero-gamma level and approximately 0.58% below its call wall. These are example arithmetic relationships only, not a regime classification or forecast. Future synthetic engineering tests may verify A's arithmetic and reject B's untyped count; those tests do not authenticate the screenshot or validate predictive value.

Each future visual zone must show instrument/provider, what was measured, observation/publication/receipt times, algorithm/model/sign convention, unit, expiry set, width, comparison rank, confidence/uncertainty and staleness. Preserve provider definitions separately from independently reconstructed walls/roots. See the draft protocol for matched-wall, flip, corridor, expiry and confluence falsification controls.
