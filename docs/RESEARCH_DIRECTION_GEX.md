# GEX Confluence Indicator — Codex Research and Implementation Handoff (v2 — evidence-screened level and confluence models)

**Prepared:** 2026-10-11  
**Repository:** `https://github.com/beam-9/GEX-indicator` (the former `beam-9/EOD-momentum-research` currently redirects; verify `git remote -v` before writing).  
**Status:** NEW research direction / PROPOSED, **not validated**. **Revision v2:** interpretation of provided GEX screenshots; rigorous testing of gamma flip, gamma walls, per-expiry heatmaps, low-GEX corridors, and EMA/HVN confluence against matched controls. No newly verified trading edge.  
**User objective:** A genuinely useful **gamma-exposure (GEX) confluence indicator** to guide possible SPX/QQQ call/put entries, invalidation, and nearby plausible targets by combining gamma positioning, EMA 8/21/50, and high-volume nodes (HVNs). First prove data provenance, causal calculations, reproducibility, and incremental predictive value. The specific level/entry/exit hypotheses and their falsification controls are in **Section 3**. Later evaluate executable options P&L and paper-forward reliability. **Never promise profitability.**

## 0. Instruction to Codex: start here

Continue in the EXISTING repository. This is a **new, separately registered research program**, not an amendment to the frozen 2026 Phase A strategy experiment.

1. Inspect current branch/working tree/recent commits, README, `reports/PROJECT_STATUS.md`, `docs/PUBLICATION.md`, historical handoffs, `experiments/RESEARCH_PROTOCOL.md`, `experiments/protocol_lock.json`, `experiments/ERRATUM_001_DROP_BEST_TRADES.md`, and prior results. Do not overwrite locked or historical artifacts. Preserve the **2026-04-10 onward holdout**; no signal/outcome testing on that interval under the old holdout authorization. **This pivot does not automatically reset or authorize reuse of the previous sealed holdout.**
2. Write a pivot decision record and a **new v1 research protocol and registry** (`experiments/gex_v1/`). Include signed data availability timestamps, source assumptions, trial inventory, holdout boundaries, and change control. Mark protocol as `DRAFT` until user/data choices can be verified; freeze *before* any new GEX signal outcome inspection. Keep old research labeled historical.
3. Update the root README to describe the pivot accurately. Use the supplied `GEX_Indicator_README_Proposed_v2.md` as a starting point, merge with any newer repo changes, verify links/commands, and preserve an archival section. Install a finalized copy of **this handoff** as `docs/RESEARCH_DIRECTION_GEX.md` (or adjust the README link to the actual new location); update `docs/PUBLICATION.md` and `reports/PROJECT_STATUS.md` to reflect the **current repository remote** if still pointing to the old name, without changing historical archived evidence. **Do not replace the repository’s history or misrepresent Phase A results.**
4. Implement vendor capability audit first, starting with mock/local fixture adapters and narrow authenticated samples where access already exists. **Do not buy data, create subscriptions, request broker permissions, scrape undocumented/private endpoints, bypass licensing, publish raw vendor data, or send real orders.** If no historical GEX vendor is accessible, use labeled synthetic fixtures strictly for engineering tests, and historical underlying bars for an independently labeled EMA/HVN study only. Never call it a genuine GEX backtest.
5. Implement point-in-time GEX, gamma-level, EMA, volume-profile, confluence, alert, target, and invalidation engines in modular Python. Construct an **external Python dashboard/signal engine** as the primary GEX-enabled artifact. Optionally provide a **Pine v6 companion** for native EMAs/HVNs/manual externally supplied GEX levels; never pretend Pine directly calls an arbitrary vendor REST API. No automated order execution.
6. Conduct chronological historical tests on *eligible*, point-in-time sources only. **Require the level-matched falsification battery in Section 3** (wall vs equally prominent non-wall strikes; flip roots vs alternative levels; low-GEX corridor vs distance/volatility-matched non-corridors; full confluence vs each component). Report each component's incremental predictive value, price-only benchmarks, costs, significance, regime stability and selection bias. A trade signal is not a profitable options strategy until options bid/ask execution is separately tested.
7. At the end of EACH stage, produce `reports/stages/GEX_STAGE_XX_<NAME>.md`, update `reports/PROJECT_STATUS.md`, and include exact run IDs, commands, hashes, missing evidence, failing candidates, user decisions, and next action. A blocked stage still requires a report.
8. Do not run old Phase A economic experiments, reevaluate its old holdout, or use the latest observed outcome to quietly tune the new protocol. Stop if data/rights/timestamps are insufficient and produce a concrete blocker report.

**Recommended rollout:** GEX Stage 00 (audit, screenshot semantics, protocol) -> Stage 01 (data feasibility with actual provider samples) -> Stage 02 (causal metrics and HVN/EMA engine) -> Stage 03 (GEX-confluence historical validation) -> Stage 04 (paper-forward dashboard and alerts) -> Stage 05 (separate options execution validation). README changes and safe publication are part of Stage 00.

## 1. Starting point, preserved findings, and strategy pivot

From repository `reports/PROJECT_STATUS.md` / Stage 03 / Stage 05 as reviewed 2026-10-11:
- Existing Python 3.12.14 / Parquet / Polars / DuckDB project; 195 tests reportedly passing at Stage 05, **not newly executed for this handoff**.
- Authentic Alpaca SIP raw SPY/QQQ minute history: 1,608,254 bars, 2023-01-03 through 2026-10-09, retained privately, not in GitHub.
- Phase A's actual development OOS: SPY 180 sessions, QQQ 297 sessions; 3/5 of eight folds executed respectively. All 28 active rule × instrument combinations negative **mean net session returns at assumed 3 bps/side**. G3 FAIL; G1/G2/G4/G5 INCONCLUSIVE. Minute-open fills and delayed availability remain assumptions. The old result **does not test true historical dealer GEX**.
- Phase A records, `review/initial-import`, erratum, manifest hashes, and its unused 2026-04-10 holdout must remain immutable.
- Old IBS code is an independent benchmark, **not** a validated GEX filter.

**New hypothesis:** Estimated options hedging context, if measured reliably, may add information about conditional price behavior near important strikes; EMA and volume profile may help identify *where and when* to act. These are hypotheses, not guaranteed causal or predictive relationships. This can produce a **NO TRADE** verdict, and negative findings are acceptable.

## 2. The indicator we are building (user-visible specification)

Supported analysis underlyings initially **SPY and QQQ** with their own option chains, optionally **SPX/SPXW** where index data is licensed. **Do not derive an SPX index GEX level by blindly dividing by 10 to obtain SPY**. Show the exact instrument of every level and, if necessary, an explicitly dated basis/ratio mapping based on simultaneous spot quotes with estimation error. Do not mix SPX index points, SPY dollars, QQQ dollars, or ES futures points in a single unlabeled level set.

User interface should display:
- Current price, RTH session/date/timezone, selected ticker, last market-data receipt and **last valid GEX observation timestamp**; **DATA STALE / DELAYED / ESTIMATED / UNAVAILABLE** indicators.
- GEX estimated **dealer gamma sign and magnitude** with sign convention and confidence caveat; 0DTE-only and all-expiry views separately; nearby positive/negative concentrated gamma strikes, top call/put gamma clusters, reproducibly defined gamma-flip root(s), distances in ticks/ATR/bps. If a provider supplies differently defined 'walls' or 'flip', label the provider definition instead of rewriting it.
- EMA 8, 21, 50 on explicitly configured **5-minute confirmed regular-session bars** as initial default; show 1-minute for execution inspection only. Calculate history/warmup exactly, no partially formed-bar repaint in confirmed signals.
- Prior completed session POC, VAH/VAL, significant HVN/LVN zones; optionally current **partial** intraday profile as of timestamp, visibly distinguished from final session profile; optional VWAP reference, price structure and volatility/session risk context.
- **CANDIDATE CALL / CANDIDATE PUT / NO TRADE**, setup archetype, trigger, reason codes, invalidation level, first/second **underlying** target zones with basis, distance, estimated reward-to-risk **before** options costs, and exact data freshness. These are *underlying price* targets, never guaranteed option price targets.
- Reason for rejection and which filters disqualified a candidate. Avoid misleading precise success-probabilities until externally calibrated on sufficient OOS evidence.
- Alerts are advisory/manual, with deduplication, throttle, expiry, cancel-on-stale, and optional 'entry confirmed' event. No broker API/trade execution.

### A. Candidate directional playbooks (pre-register; not trading rules yet; see Section 3 for precise hypotheses and controls)

**Playbook G-NEG (hypothesized short-gamma / expansion):** estimated dealer gamma negative, spot approaching a statistically important gamma cluster or break/retest level, EMA8/21/50 context supports breakout, and prior HVN boundary / LVN context does not make the nearest target too close. Long-call *candidate* on confirmed bullish break plus acceptable target-room; long-put *candidate* on bearish break. Invalidation at failed reclaim/break zone or nearby structure. **Do not infer direction from negative GEX alone.**

**Playbook G-POS (hypothesized long-gamma / range):** estimated dealer gamma positive and material, price rejects a preregistered extreme (wall, VAH/VAL, prior HVN edge) with EMA context compatible with reversal; target prior POC/HVN/interior. **Do not mechanically fade every wall.**

**Playbook G-FLIP/UNCERTAIN:** price near model-dependent gamma flip, conflicting gamma-sign models, volatile macro-release window, non-fresh chain, thin market, no target room, or clustered levels causing a low reward/risk -> **NO TRADE** by default until such a regime has separate empirical support.

**Optional trend-continuation comparator:** 8>21>50 EMA (or reverse), sustained closes beyond a prior profile zone; test as **benchmark independent of GEX** to quantify actual GEX incremental value. EMA crossover alone is not proof of an edge.

**Targets/risks (candidate generation):** nearest forward GEX cluster, prior HVN/POC/VAH/VAL, session high/low, ATR-based reachability; targets are *zones with widths*, not magical exact prices. Target must lie beyond expected underlying slippage, and target-before-stop statistics must be computed causally. Define one unique, fixed target ordering, clustering and collision/tie policy. Distinguish binary probability of touching from probability of being filled before the stop, and from long-option profit probability. Use a maximum setup time-to-live. Preliminary risk limit caps max cost of purchased option premium; avoid 0DTE holding through cutoff/settlement except under independently validated rules. Not financial advice; no auto-trading.

## 3. Evidence-screened hypotheses from the supplied gamma maps and heatmaps (2026-10-11)

**Scope and evidence hierarchy.** These are the user's *proposed* interpretation of two screenshots, not observations of a repeatable edge. Ground the mechanism in Cboe's exchange research, peer-reviewed market-microstructure studies, and TradingView's volume-profile documentation. Treat independent 2026 SSRN working papers as **interesting counterevidence / measurement audits, not settled peer-reviewed conclusions**. Gamma explains **potential hedging-flow response conditional on dealer inventory and actual hedging**, not the market's direction. The aim is a falsifiable indicator, not a collection of attractive lines.

### 3.1 What the two reference screenshots actually show (and what they cannot establish)

- **Screenshot A (SPY aggregate GEX panel)** explicitly shows a displayed SPY spot of **$780.50**, modeled **Net GEX +$7.8B** (call side +$25.1B, put side −$17.3B, 'total' $42.4B), **Call Wall $785**, **Put Wall $755**, and **Zero Gamma $776.27**. Under **this provider's** model, SPY is above its displayed zero-gamma level and 0.58% below its displayed call wall. These are **point-in-time illustrative observations in the image**, not verified current live values, forecasts, or a measured dealer position. The screenshot's 0DTE expiry share reads 0.0%; do not assume that share remains zero once a new trading session begins. Verify snapshot time and timezone before drawing conclusions.
- The strike histogram in A shows signed/modeled contributions by strike and a spot line. **Green/red are not proof dealers own the positions in the corresponding sign.** 'Call wall', 'put wall', and 'zero gamma' must be stored as *provider-defined level types* with source, formula and time; never silently substitute a different formula.
- **Screenshot A's lower strike-by-expiration heatmap** appears to show *dollar GEX-like values* for individual expiry/strike cells (e.g., positive concentrations near $780/$785). Use the cell's actual legend, units and model metadata. The same strike can receive very different exposure across 0DTE, weekly and monthly expiries; flattening across expiries can hide these differences.
- **Screenshot B** is a separate strike-by-expiration matrix with conspicuous counts, including a highlighted **129,473 at strike 785 for Oct 16**. Its legend/units, model, receipt time, and even data vendor are **not established by the image**. It might show position/OI, activity, or a different metric; **do not assume 129,473 is gamma dollars or actual market-maker contracts**. Do not merge A and B into one signal without a verified same-asset/same-time/same-units/same-inventory-model crosswalk. Record `metric_kind`, `metric_unit`, `contract_type`, `expiry`, `as_of`, and `model_id` for every cell.
- Document screenshot-level interpretation as `docs/GEX_SCREENSHOT_FIELD_DICTIONARY.md` containing field, meaning, provenance needed, uncertainty and prohibited inference. These images are UX references, **not admissible historical training samples**.

### 3.2 Evidence-backed *mechanisms*, with explicit qualifications

| Research proposition | Strength and qualification | What the indicator can do |
|---|---|---|
| **Estimated dealer long gamma may dampen moves** (sell rallies, buy dips) | Cboe's research and the academic literature support the *conditional hedging mechanism*, not guaranteed sideways prices. Market direction, actual inventory, hedging frequency and liquidity also matter. | Show **estimated dampening regime**, optionally suggest testing fade/rejection setups; **never label "certain chop"**. |
| **Estimated dealer short gamma may amplify moves** (buy rallies, sell declines) | Same conditional mechanism. Cboe finds average index-market-maker impact is generally modest relative to total market variation, and net positioning can be offset across products. | Show **estimated expansion-risk regime**, test break/retest with direction derived from observed price, not gamma sign. |
| **Sign and magnitude relative to available liquidity matter** | Peer-reviewed/working research studies gamma imbalance **interacting with liquidity**. Notional dollar GEX alone is not comparable between assets/periods. | Test `hedge_flow_estimate / corresponding market liquidity`, realized/forecast volume, spread and distance-to-spot. Label estimation assumptions. |
| **Gamma concentrations can relate to strike clustering/pinning** | Ni, Pearson & Poteshman (JFE, 2005) document *expiration-date stock* clustering. This does **not** establish that any SPY intraday call wall is a unique support/resistance barrier. A preregistered 2026 SPY working paper finds largest walls statistically indistinguishable from other high-GEX strikes on several level-local outcomes; replication needed. | Display walls as **candidate testable zones**; benchmark their quality against **other large strikes and matched controls**. |
| **Gamma flip could indicate regime change** | 'Flip' can mean portfolio net gamma re-priced across hypothetical spot values, or a simplistic crossing between adjacent signed strike bars. The two are **not equivalent**; one portfolio can have multiple/no roots, and intraday IV/OI assumptions move them. Recent independent measurement research documents instability. | Use **named, versioned flip methodology**, roots and stability band; no automatic trade on a single crossover. |
| **Low-GEX area could permit extension** | **Plausible conjecture, not established**: limited gamma concentration between present price and next cluster could imply less gamma-hedging friction. But absence of plotted bars may reflect missing contracts, chart clipping, expiry filter or normalization; ordinary liquidity and directional order flow still dominate. | Test a **low-gamma-density corridor** and available target room **against matched placebo corridors**. Never promise a 'gamma vacuum' move. |
| **EMA stack + retest + HVN adds confluence** | EMAs are trend summaries; HVNs/POC are *past traded-volume concentrations*, not prospective buy/sell orders. TradingView explicitly calls volume profile reactive and explains that a volume spike is not a guaranteed reversal. Combining these signals may add no new information. | Use prior/partial-as-of volume nodes and confirmed EMA bars as candidate confirmation, and **measure incremental lift net of lower signal count and costs**. |

**Primary research sources**: Cboe/Amaya et al., *0DTE Index Options and Market Volatility: How Large is Their Impact?* (2025); Cboe Xu (2025) actual SPX 0DTE market-maker flow; *Option gamma and stock returns* (Journal of Empirical Finance, 2023); *Gamma Fragility* (Barbon & Buraschi, research paper); Ni et al., *Stock price clustering on option expiration dates* (JFE 2005); TradingView volume profile basic concepts; Cboe DataShop OI FAQ. Working-paper challenges: Popovici, *Do Gamma-Exposure Walls Exhibit Strike-Local Effects?* (SSRN 2026, not peer reviewed); Chilingarian, *The Sign of Dealer Gamma... Two Definitions of the Gamma Flip* (SSRN 2026, not peer reviewed). Full URLs in revised references Section 11.

### 3.3 The gamma flip: implement two distinct methods, never conflate

- **Portfolio repricing zero-gamma root:** for a fixed *point-in-time* set of contracts, OI, IV surface and dealer sign convention, compute signed net **dollar** gamma on a predefined range of hypothetical spot values using a specified sticky-strike/sticky-delta assumption. Numerically find zero crossings with declared bracketing/interpolation and root-selection policy. Expose zero, one or multiple roots honestly. The *nearest root* may be a display convenience, **not always the regime delimiter**.
- **Per-strike bar sign crossing:** a zero crossing between neighboring positive/negative **strike totals** in the displayed histogram is a different statistic; do not call it the portfolio flip. Record `PER_STRIKE_CROSSING` separately with possible multiple crossings.
- Persist `spot_range`, `spot_step`, `IV_repricing_assumption`, `dealer_sign_model`, `OI_publication_as_of`, `expiry_scope`, `gamma_currency_unit`, `quote_mark`, `timestamp`, `root_count`, `root_stability` and snapshot hash. Add regression cases for multiple roots, no root, near-zero numerical instability, sign inversion, stale/partial chains, and 0DTE gamma singularities near expiry.
- Test distance to flip as a **continuous variable**, and separately test cross/hold/retest events with persistent-bar conditions; prefer a **no-trade/uncertain regime** within the measurement/price-tick uncertainty band. Do not hardcode 'above flip means calls' or 'below flip means puts'.

### 3.4 Per-expiration heatmap and true positioning uncertainty

- For each **strike × expiration** cell track reported `open_interest`, `volume`, `call_gamma`, `put_gamma`, `gross_abs_gamma`, `signed_gamma_proxy`, `as_of` and `source`. **Only show columns actually supplied**; do not transmute raw counts into GEX dollars without valid contract greeks/units/multipliers.
- Preserve **0DTE-only, ≤7 DTE, weekly, monthly and all-expiries** aggregates as separate views. Report concentration share of near-expiry gamma, gamma contribution near spot vs remote wings, top-K strikes **by the exact metric**, and time-to-expiry; never multiply 0DTE gamma by yesterday's volume as if it were current dealer inventory.
- **Open interest is published after prior-session clearing and is generally static through the trading day** (Cboe DataShop FAQ). Contract trading volume is activity, not signed dealer inventory; it cannot independently establish dealers long or short. A vendor claiming live-position changes must document its transaction classification and updating algorithm. Persist **effective publication times**, not merely the trading date.
- Require sensitivity across (i) provider-native dealer-signed positioning when documented, (ii) conventional call-positive/put-negative **OI proxy**, (iii) alternate sign models, (iv) DTE scopes and (v) plausible spot/IV repricing. If sign changes under reasonable conventions, use **GEX_SIGN_UNCERTAIN** and suppress sign-dependent automated candidate alerts.

### 3.5 Candidate playbook decision order and measurable conditions

**Use this precedence: data/expiry validity → instrument mapping → macro/session veto → regime estimate → location relative to tested zones → independently confirmed price trigger → EMA/profile qualification → reachable targets/stop → option liquidity (if relevant) → NO TRADE/ALERT.** A GEX map is *context*, not a trigger.

- **L1: Negative-gamma continuation candidate.** Strong, meaningful **model-estimated short gamma**; 5m completed bar closes **beyond a predefined level/zone** (call/put wall, flip band or prior profile edge) and price subsequently holds or retests it within a prespecified time-to-live. Direction is chosen by a verified bullish/bearish price move, not GEX alone. Record EMA8/21/50 ordering, slope and distance; do not demand that all three are stacked in every regime without ablation. Require *pre-entry* defined first target outside the retest/invalidated zone and price/volume context. Distinguish breakout-vs-failed-break paths.
- **L2: Positive-gamma mean-reversion candidate.** Material estimated long gamma, approach to a **candidate** wall or confirmed prior VAH/VAL/HVN boundary, *actual rejection* defined by completed bars and no significant confirmed trend acceleration against it. Examine EMA compression or opposing stack as features rather than universal mandatory vetoes. Potential T1 previous POC/HVN interior, T2 additional pre-known level; stop beyond the rejection zone. Do not assume the largest gamma strike is intrinsically stronger than other levels.
- **L3: Low-density 'gamma corridor' continuation candidate** (highest skepticism). Define **same-snapshot** signed and absolute gamma per **price interval**, normalized by options completeness/spot/nearby strike grid and optionally expected hedge demand/underlying liquidity. Declare thresholds from training only. Detect a corridor only with contract coverage proven; *missing bars / distant OTM / chart clipped are NOT low gamma*. After a price/volume-confirmed break and retest, estimate conditional path speed and target-before-stop through corridor toward next **independently pre-known** zone. Test whether it improves L1 rather than adds an unjustified extra setup.
- **L4: Flip-transition candidate** (initially **monitor-only**, not a call/put alert). Confirm *portfolio* flip methodology, sign stability across snapshots, price crosses and holds beyond defined uncertainty/hysteresis zone for prespecified confirmed bars, plus price/EMA context. Compare to a placebo level and to no-flip trend entries before promoting.
- **L5: Conflict / low-information → NO TRADE.** Zero/near-zero gamma, contradictory sign models, very large wall/target overlap, no room before opposing GEX/HVN zones, stale snapshot, insufficient quote/OI publication evidence, IV shocks, high spread, macro uncertainty, unsupported SPX↔SPY/QQQ scaling or upcoming expiry cutoff. Do not reverse a candidate simply because GEX crossed a model-dependent flip.

**Structural retest definition (to pre-register, not optimize ad hoc):** reference level known at or before decision; breakout requires a fully closed 5m bar beyond a zone + predeclared buffer; retest uses only following bars within a fixed lookahead **from the trigger** for recognition; confirmation must arrive before order submission, with invalidation based on level/structure defined then. Compare 'no retest', 'break + retest', and 'rejected break' as separate prespecified models if data permit. One-minute bars may refine fills only if the 5m signal existed before the 1m order. Enforce daylight-saving changes, halts, gaps and force-flats. No use of future candle highs/lows to backdate an entry.

**EMA definition:** EMA8/21/50 on **confirmed 5-minute regular-session bars**, with choice of overnight reset versus warmup from the prior session explicitly locked; features include ordering, slopes, separation / ATR, changes in alignment, not just a Boolean. Condition on distance to nearest gamma/profile zone; otherwise many variables simply encode the same trend. Never pretend EMAs forecast direction on their own.

**Volume-profile definition:** use prior *completed* session HVN/POC/VAH/VAL for unambiguous static levels; for current-session values use only tape/aggregates observed and published **before** the trigger. HVN is a volume peak (possibly a zone), not the same as a gamma wall. LVN is a volume trough, which may or may not accelerate traversal. In a large-HVN zone treat target proximity as risk of stalling; test breakdown/reclaim before using it as a target. Store bin size, quote/trade feed, local maxima prominence, profile lifetime and alternate `BAR_PROXY`/`TRADE_PRINTS` provenance.

### 3.6 Exits and target selection: distinguish three separate endpoints

1. **Target attraction:** probability that a tagged GEX/HVN/POC zone is touched within **5/15/30/60 minutes** after a *causal* signal; distance- and volatility-adjusted. This is not success probability of a trade.
2. **Trade-executable path:** probability that the **pre-known T1** is touched before the **pre-known invalidation/stop**, with a conservative tie rule when both fall within the same bar. Price-bin levels are zones with buffers, not guaranteed prints or fills. Report median time-to-T1, MAE/MFE, rate of stagnation, and target-horizon expiry.
3. **Long-option profitability:** requires valid option chain/contract mapping, strike, ask entry, bid exit, size/depth, fees, IV/theta effects, exact 0DTE cutoff and risk limits; directionally correct underlying signals **can still lose money**. Do not show a 70% 'options win probability' from price-only target-touch statistics.

Before any backtest lock a deterministic **target ranking**: first *independently known* opposing obstacle along travel path with adequate distance/size and minimum R multiple, then next distinct zone; merge overlapping GEX + volume nodes into one **confluence cluster** with source identities, not two fictitious targets. If closest level offers insufficient room, label NO_TRADE rather than skip it to claim an attractive distant T1. A gamma concentration may be a **barrier** rather than a magnet; test both touch and rejection with direction-agnostic controls. If no eligible target exists, label UNDEFINED_TARGET and abstain. Predefine partial-profit vs full-exit variations as separate trials, not discretionary hindsight choices.

### 3.7 Strict matched-control and ablation experiment suite (mandatory)

Pre-register a small finite family; explicitly distinguish **regime prediction**, **level predictiveness**, **signal execution**, and **options P&L**.

| Claim under test | Outcome | Critical falsification/control |
|---|---|---|
| Positive vs negative **estimated net gamma** predicts volatility regime | Next 5/15/30m realized abs/squared returns and trend/chop measures | Prior volatility, implied vol/VIX, realized range, intraday time, expiry effects, macro event dummies, liquidity, season/year, lagged returns. Assess sign-model and expiry-scope robustness. |
| The **#1 wall** is significant S/R or magnetic T1 | Touch/reject/break/dwell rate, conditioned on starting distance and accessible trading time | #2–#5 large GEX strikes; nearest round-number strikes; prior session S/R; level-shuffled controls with matched strike spacing, moneyness, distance/ATR and time-of-day. Use **level-local** tests, not only market-wide gamma association. |
| **Gamma flip** creates a useful change in market behaviour | Return/volatility persistence on crossing, retest outcomes, post-cross reversal | Equal-distance random/round-number crossover controls, per-strike crossing versus portfolio root, alternative IV/sign conventions; root hysteresis/no-root regime. |
| **Low-GEX corridor** predicts faster/larger travel | Forward range/velocity to next zone, time-to-target, adverse excursion | Equal-width/distance/volatility/volume/strike-grid-matched high-gamma or randomly located price corridors, plus LVN-only model. Test missing-chain rejection. |
| **EMA stack** and retest add value beyond GEX | Conditional entry direction, target-first expectancy, signal count and false positives | Compare GEX-only, EMA-only, profile-only, GEX+EMA, GEX+profile, EMA+profile, full trio; hold all entry/exits and data/timing assumptions equal when comparing. |
| **Expiry concentration** improves level performance | Difference in hit/bounce/break rate by 0DTE/weekly/monthly weighting | DTE-matched concentration placebo; include prior OI publication timing, contract completeness and moneyness effects. |

**Selection/acceptance constraints:** predeclare exactly one primary outcome (e.g., net expectancy of a small, bounded, tradable candidate family after pessimistic costs) *and* secondary outcomes; track every tried threshold/feature/clock horizon, control false discovery with resampling/Holm or other precommitted multiplicity methods, report confidence intervals and sample sizes; use day-blocked chronological WFA, synchronized-SPY/QQQ dependence, realistic historical bid/ask/latency and a newly frozen/authorized holdout separate from the untouched prior Phase A interval. No decision from one highlighted wall or favorable day. If matched controls tie the wall, **reject special-wall claims even if the indicator can still label a regime**. If combined confluence loses to simpler components out-of-sample, simplify/remove it. If no truly point-in-time GEX history exists, only prospective shadow collection is allowed for GEX economics; do not splice screenshot-derived daily levels into backtests.

### 3.8 Additional interface and stage deliverables for Codex

Implement the following in addition to Sections 2 and 5–9:

- A **pre-trade scenario map** (not a prediction): `Regime = LONG_GAMMA / SHORT_GAMMA / UNCERTAIN`; above/below **provider-named zero gamma**; nearest significant levels and *verified expiry sources*; EMA stack and distance; last confirmed HVN/POC/VAH/VAL; nearby congestion; next gamma-density corridor; expected move/volatility context; observation age; reason codes; eligibility for L1–L5.
- Every visual zone should carry hover metadata: **what exactly was measured, instrument, provider, publication time, algorithm, confidence/uncertainty, expiry scope, zone width, comparison rank**. Rendering color alone must never imply 'dealer-owned signed inventory'.
- Introduce `level_id`, `snapshot_id`, `available_at`, `expiry_set`, `wall_rank`, `root_method`, `sign_model`, `volume_metric`, `zone_confluence_count`, `corridor_coverage_valid`, and `component_ablation_id` to research/alert schemas. Require strict no-duplication and invalidation if levels update after alert issuance; live snapshots are immutable.
- Add **unit tests of screenshot A field arithmetic** (+25.1B + −17.3B = +7.8B; 25.1+17.3=42.4B), but do **not** use screenshot B's unlabeled 129,473 as GEX dollars. Add cross-vendor strike/expiry join validation, delayed OI publication poisoning, flipped sign convention, multiple portfolio roots, nearest-wall selection vs hindsight, corridor missing-grid rejection, pre-trade target ordering, target/stop same-bar tie, and confirmed EMA + 1m-fill chronology.
- Stage 00: incorporate this addendum in `docs/RESEARCH_DIRECTION_GEX.md` and adapt README so walls/flips/corridors are listed as **hypotheses to test**, not promised predictive levels. Stage 01: identify provider’s *exact* cell and wall definitions (send user a sample request/checklist if vendor documentation is insufficient). Stage 02: ship causal engines and synthetic scenarios labeled `TEST_ONLY`. Stage 03: execute matched-level falsification + ablations before any claim. Stage 04: capture real-time snapshots as issued, frozen signals and alert cancellations. Stage 05: use real options NBBO, not synthetic P&L.

## 4. Research evidence and **data-provider decision matrix** (2026-10-11 checked)

### 4.1 What data is actually required?

**Minimum for *real* historical GEX signal backtest** at each decision time:
- As-of option series with underlying/root, expiry/session type, strike, call/put, multiplier, quote (or IV), model gamma, prevailing spot, availability/receipt timestamps and version; previous **published** OI and effective publication timestamp; intraday option volume/flow if used; contract rolls/settlement/exercise and corrections.
- Defined dealer-position/sign assumption, aggregation/units, 0DTE vs non-0DTE partition, and point-in-time snapshot reconstruction. The same methodology must be available historically and live; static backfilled chain snapshots do **not** prove a live-known signal.
- Genuine underlying trade/quote/1-min bars for EMA and volume profile; historical NBBO and sizes for options-executable validation, not only last trades or theoretical midpoints.

**Start with only SPY and QQQ (or SPXW once contract definitions are proven), selected dates, 09:30–16:00 ET**; calculate expected cost before requesting a full options universe. Use bounded, cached, hashed, read-only samples.

### 4.2 Specific verified candidates (capabilities from official docs; user entitlement and historic scope not verified)

| Provider | Historical use | Live use | Scope / caveats | Initial decision |
|---|---|---|---|---|
| **Existing Alpaca SIP** | Already collected SPY/QQQ minute OHLCV; investigate historical trade prints / quotes under existing credentials | Market-data streams subject to existing entitlements | **Does not itself supply dealer GEX**; 1-min OHLCV permits only a **profile proxy**, not exact volume-at-price | **REUSE now** for prices, EMA, initial HVN proxy |
| **Quant Data (quantdata.us) GEX API** | Official guide claims **365+ day** lookback and intraday **interval-map** by strike/minute; `sessionDate` | Per-strike exposure API and intraday maps advertised | Confirm exact returned sign/units, timestamps, entitlements, history back to desired start, rate limits, latency, 0DTE, rights and quote-based methodology; historical 365+ days may be too short for 2023 start | **First targeted GEX API feasibility trial** if lawful access, no subscription without approval |
| **Databento OPRA.PILLAR** | Option definitions, historical trades/NBBO, **start-of-day OI statistics**, historical SPXW 0DTE examples; compute Greeks / GEX ourselves if necessary | Consolidated options feed with licensing, connection and API terms | Requires engineering Greeks, dividends/rates, sign models; large data and OPRA costs; confirm SPXW 0DTE contract & data dates | **Strong raw-data reproducibility candidate**, obtain quote/sample estimate |
| **Cboe DataShop Option Quote Intervals** | 1-min option NBBO+size, optional Greeks and OI; SPX and ETF datasets | Interval files, not necessarily suitable for low-latency decision feeds; 15-min delayed intraday product | Investigate historical coverage, delivery, publication and pricing; snapshot greeks != observed dealer inventory | **Strong historical backtest candidate**, obtain small-sample quote |
| **Massive (formerly Polygon)** | Options tick quotes/trades, contracts, aggregates; snapshots with gamma/OI/IV; verify historic *chain snapshot* availability | REST/WebSocket chains and quotes by subscribed tier | **Today's snapshot endpoint is not automatically a point-in-time snapshot archive**; reconstruct only from legitimate historical quotes/OI, check full index SPX contract treatment | **Potential live/provider combination** after tests |
| **Intrinio** | EOD options chains/Greeks/OI and certain historical quotes; longer bulk history possible | Options real-time/delayed products sold separately | **EOD snapshot cannot supply intraday GEX evolution**; good previous-day contextual levels if publication time verified | **Lower-cost coarse historical baseline** subject to provider terms |
| **SpotGamma** | Proprietary model dashboards and EquityHub CSV export (official support confirms export) | Useful human chart/context, not a documented public API | **Official support says no public API yet.** Do not scrape dashboard, browser tokens, reverse-engineered endpoints or assume export automation rights. | **Manual comparison only**, not an API backbone |
| **GEXStream / other API-first vendors** | Advertised limited lookback (e.g. 30 days hourly GEXStream); investigate detailed scope | Authenticated read-only snapshots | Third-party historical coverage, computation and retention rights must be contractually verified | **Optional short shadow comparison**, not primary WFA without older history |

Important: A vendor's 'GEX by strike' may represent **call/put gross exposure**, a signed inventory heuristic, or an intraday flow estimate. These are **different statistical objects**. A 'gamma flip' may be a per-strike crossing or a root obtained by repricing portfolio gamma over spot; they need not match. Record exact provider convention, scaling and expiry inclusions. Quant Data offerings with similar names/domains can have **different products**; verify URLs and account rights individually. Free or paid status may change. No price/licensing promise is made.

### 4.3 Vendor due-diligence checklist (make comparative `docs/GEX_DATA_FEASIBILITY.md`)

For each candidate collect and timestamp:
1. Source product/version; eligible SPY/QQQ/SPXW root, OPRA license; market data redistribution / storage/retention / derived-work rights; **personal vs commercial** permissions.
2. Oldest *verified retrievable* historical session, expiry completeness including now-expired contracts, frequency (EOD, 1m, 1s), OI publication lag, snapshot generation/receipt latency, revisions/corrections, timestamp timezone.
3. Fields, sign-model and units, put/call conventions, gamma normalization, 0DTE partition, strike clustering/flip algorithm, opening vs live-volume treatment; both raw chains and provider precomputed levels if available.
4. Endpoint auth method, streaming vs polling, rate limits, average and 95/99th-percentile latency, outage behavior, per-month cost for sample and full sample, storage cost, API error modes.
5. Test at least **three predeclared historical dates** spanning regime variety, plus one limited current session when market is open; record parsed schemas, missing rows, per-symbol coverage, response hashes, and *as-of* consistency **without testing profitability** during vendor selection.
6. Before new research, choose **one primary source/model**, a secondary sanity-check if available, a historical train/test window, benchmark set, and explicit no-data behavior; freeze the decision in `experiments/gex_v1/PROTOCOL.md`.

### 4.4 Historical GEX reconstruction and point-in-time safeguards

For self-calculated gamma, a commonly used **dollar delta change for a 1% move** at contract level is:

`gex_1pct_usd = signed_contracts * gamma_per_underlying_dollar * contract_multiplier * spot_price**2 * 0.01`

where `signed_contracts` is the **hypothesized dealer inventory**, *not* merely unsigned OI. If using OI, `signed_contracts = sign_model(contract) * as_of_published_OI(contract)` is only a proxy; document models for (a) all call-long/put-short dealers, (b) reversed, and (c) measured/proxy flow if identifiable. Gamma is nonnegative for ordinary long vanilla options, regardless of call/put; model dealer **position** determines the hedging sign. Do not claim that OI reveals dealer side or that 0DTE newly opened positions are represented instantly in published OI.

Daily OI is published **before** the session and is not a continuous realtime positions ledger. Distinguish daily OI + *live repriced Greeks*, versus updated modeled exposure using intraday flow. Preserve effective publication timestamp, last quote, model inputs, options multiplier/corporate actions, rates/dividends, IV fitting and gamma degeneracy near expiration. Reject stale/crossed quotes and impossible spot/expiry combinations. Parameterize expiration filters, spot shocks for net-gamma curve, and root isolation; compute crossing multiplicity and confidence range across sign models. Test units, model consistency and sensitivity; use independent library/closed-form benchmarks.

**Strict causal rule:** an observation is available at `max(event_timestamp, effective_publication_timestamp, receipt_timestamp)` if all are present; with missing historical receipts, label assumption and test delayed scenarios. No backfilling later snapshots or final-day gamma levels into morning signals. Save *versioned* daily premarket levels vs intraday refreshed levels.

## 5. Price/volume data: EMA and high-volume nodes

**Existing historical prices**: retain current Alpaca SIP private minute series. Do not re-download without need. Include separate market-trade event dataset if the current entitlement allows because exact trade prints permit more credible price-by-volume. Never claim OHLCV volume equals volume executed at each price.

**EMA features**: 8, 21, 50 calculated on confirmed 5-min regular-session bars (SPY, QQQ initially), causal warm-up explicitly specified (continuous previous sessions vs reset at RTH open, pre-register one), no higher-timeframe future leakage, plots 1-min optional context. Benchmark EMA slope, stack and reclaim/lose 21; avoid testing huge arbitrary combos.

**Volume-profile definitions**:
- Compute a **prior-completed-session immutable profile**; current partial session profile is allowed only using executed observations up to decision time; *never* retroactively paint final current-day POC/HVN on earlier bars.
- Fixed price bins in absolute tick units or ATR-scaled bins precommitted by instrument; volume per bin from trade prints (preferred), or explicitly **bar-allocation proxy** from 1-min OHLCV; implement ≥2 proxy methods (close-bin and uniformly over bar range) as *sensitivity tests*, never call either exact print-by-price volume.
- From a profile generate POC, 70% volume-area VAH/VAL, smoothed peaks (HVNs), troughs (LVNs), node strength, prominence, zone width, merge distance, minimum volume and node-age. All parameters preregistered before economic search.
- Restrict in-session timestamp/volume and tape corrections; verify trade conditions, consolidated vs venue feed, odd-lot/trade exclusions if using prints. SPX is an index, not a traded security with directly comparable share volume. For SPX setups, explicitly choose SPY or ES volume proxy and label **different instrument basis**.
- Integrate **TradingView `request.footprint()`** as an optional Pine feature for Premium/Ultimate eligible accounts. It offers footprint-row POC/VAH/VAL and HVN possibilities, but cannot be treated as the same as our external tape-derived HVN definition without parity tests. TV built-in VP often uses lower-timeframe bars and differ from trade prints. Provide fallback non-footprint level plotting and `na`/not-supported state.

## 6. Data and software architecture

Do **not** rewrite the Phase A engine or start in Pine. Reuse proven Python modules, segregate with a new `src/eod_momentum/gex/` or (prefer after local review) `src/gex_indicator/` package without breaking historic import paths. Keep existing Parquet / Polars / DuckDB and deterministic event simulator, add vendor adapters. Decide rename/module path only after verifying test and packaging implications. No Rust migration required.

```text
provider input (licensed OPRA/aggregated GEX; Alpaca price/trades)
  -> immutable raw cache + as-of & provenance + quality/latency checks
  -> options chain reconstruction and model-labeled GEX levels
  -> EMA(8/21/50) + POC/VAH/VAL/HVN/LVN (causal)
  -> feature registry + setup engine + vetoes + target/stop generator
  -> (i) chronological research / cost-aware validation
     (ii) read-only live shadow monitor + alerts + simple dashboard
     (iii) conditional Pine v6 companion / manual approved levels
  -> paper-forward evaluation -> separate real option NBBO evaluation
```

Recommended modules/interfaces:
- `providers/{base,alpaca,quantdata,databento,cboe,massive,local}.py` read-only; optional dependencies not required for offline fixtures.
- `schemas.py` typed model objects `MarketObservation`, `OptionContract`, `OptionSnapshot`, `GEXSnapshot`, `ProfileZone`, `SignalCandidate`, `TargetZone`, `RiskPlan` with `event_ts`, `published_ts`, `received_ts`, `available_at_ts`, `source_id`, `model_id`, `data_quality`, `convention`, `unit`, `code_digest`.
- `gamma.py`, `gamma_levels.py`, `volume_profile.py`, `ema.py`, `signals.py`, `targets.py`, `risk.py`, `validation.py`, `replay.py`, `live_monitor.py`, `ui.py` and tests (adapt to existing architecture).
- `data/raw/` and `data/processed/` private; `data/manifests/` sanitized provenance; no auth tokens or licensed data in Git. Add provider fail-closed `STALE`, `DELAYED`, `MISSING`, `LICENSE_BLOCKED` statuses. Local append-only trial ledger and artifact hashes. Rate-limit/backoff, snapshot conflict controls, stream-reconnect/outage handling and monotonic receipt timestamps.
- Python dashboard: Streamlit/Plotly or lightweight FastAPI+frontend according to existing infrastructure. Read-only and usable locally. Show gamma exposure *estimated*, price, levels, 5m EMA overlay, profile zones, timestamp and states; 1m zoom only for trigger inspection, do not spam alerts.
- Optional Pine v6 companion: EMAs, native price-only filters, optional POC/HVN if available, display **manual or permitted TV-native feed** of GEX levels with `as_of` date and a conspicuous expiration/freshness state. **Pine Script cannot generally fetch arbitrary private REST/WebSocket GEX data**, and TradingView webhooks are **outbound** alert notifications, not inbound data into Pine. Never silently synthesize GEX inside Pine from SPY price bars. Consider a custom web chart using TradingView Advanced Charts Datafeed API only after checking license/access; otherwise use Plotly.

## 7. Test plan, baselines, acceptance, and anti-overfitting

### 7.1 Unit/engineering gates before strategy outcome tests

- Source API response fixtures (sanitized), full schema/contract roots, OI as-of tests, event/receipt poison tests, expiry rollover, 0DTE near close, stale-feed and reconnect, fragmented/corrected quotes, gamma sign convention sensitivity, SPY/SPX mapping, GEX scaling invariants.
- EMA parity with independent NumPy/pandas or TA reference; 5m bar close/warmup and holidays/early close/DST tests; 1m vs 5m confirmation.
- Volume profile with hand-checkable trade prints, weighted 70% VA, multiple HVN local maxima, threshold/cluster tie cases, **no future current-day volume**; Python vs Pine parity within declared data-source tolerance.
- Targets/stop zones never forward-observed. Preserve versioned zone definitions, no target chosen because it turned out to be reached. Overlapping simultaneous signals have explicit priority; define multi-asset correlation treatment. Order simulations include submission after decision, realistic fill assumptions and outcome censoring.
- Re-run existing repository verification and publication guard; old historical artifacts and hashes remain untouched.

### 7.2 Registered, staged *experimental hierarchy* (avoid combinatorial overfit)

Pre-register a **small finite** initial inventory, e.g.:
- **B0** no-trade/long/short or preregistered prior price-only benchmarks (do not claim prior Phase A validation transfers).
- **B1** EMA8/21/50 trend/reclaim only, no GEX or HVN.
- **B2** prior POC/HVN/VAH/VAL price-context only, no GEX.
- **B3** GEX magnitude/regime/level geometry only (fixed entry trigger independent of future data). **Do not presume walls outperform matched non-wall strikes; see Section 3.7.**
- **B4** GEX + EMA.
- **B5** GEX + HVN.
- **B6** GEX + EMA + HVN **only if preregistered and preceding components have enough OOS evidence**.

Precommit exact thresholds and zones based on *training-only* historical features; not arbitrary 8/21/50 proximity, hindsight-defined breakout, or best-of-500 filters. Gamma regimes may require minimum signal magnitudes scaled by recent liquidity/volume (gamma sign alone is not sufficient); reserve 'unknown' regime. EMA confluence should be an optional filter tested for **incremental lift** and changes in frequency, not assume more filters = more profit.

Use separate chronological train/validation/OOS test folds with train-only parameter fitting and truly out-of-sample GEX as-of snapshots. Disallow future data via purging/embargo where outcome windows overlap; holdouts *must* be specific to **the new preregistered experiment** and not silently reuse the earlier sealed period. Forward collection is especially valuable if historical GEX point-in-time is unavailable. Do not promote an OOS finding without enough trades/dates and cost realism; show confidence intervals, uncertainty and base rates.

Metrics **separate these three tasks**:
1. *Level quality*: distance error and time-to-touch / reject / breakout probabilities, conditioned on level type and age, against matched control price levels; predefine acceptance/risk ranges and evaluation horizon.
2. *Underlying candidate rule*: target-first vs invalidation-first, conditional expectancy, opportunity rate, false positives, trade/no-trade coverage, slippage/stale-data stress and regime stability.
3. *Actual options trade*: historical contract availability, option ask entry/bid exit with NBBO sizes, fees, theta/IV changes, spread, expiry cutoff and early liquidation; only run with genuine eligible option market data. A correct underlying directional move may still lose option premium.

Cost frontier and latency > cherry-picked Sharpe; show every failed test. Block bootstrap by session, clustered/SPY-QQQ dependent samples, multiple-test accounting (DSR/PBO only if defensible), parameter perturbation, real macro-event windows, session-time ablations, first/last 30 min, high/low volatility, strong/weak GEX, shocks, short options market exposure, and missing observations. Avoid putting paper-trading performance or expected returns on UI before prospective calibration. Explicit **NO EDGE / INCONCLUSIVE / PROMISING FOR PAPER FORWARD** verdicts; never overstate certainty.

### 7.3 Stage gates (must pass in order)

- **D0 Data provenance**: legitimate historic AND live-compatible source; contract-level fields and timestamps; no unsupported sign claims.
- **D1 Causal feature parity**: no future leakage, 5m EMAs, volume-profile and GEX calculation golden fixtures pass.
- **D2 Incremental signal edge**: combined GEX feature beats price/EMA/HVN baselines on strictly held-out development at realistic scenario costs/uncertainty; report if absent.
- **D3 Signal usability**: targets/invalidations computed pre-entry, signal frequency, stale/outage handling and model uncertainty robust.
- **D4 Paper-forward**: read-only uninterrupted market sessions with captured at-signal values and alerts; no retrospective level changes, measure coverage/false alerts.
- **D5 Options trade evidence**: genuinely tradable options NBBO data, reasonable strikes/expiries/entry sizes, loss limits and positive net edge; not required for informative non-trading indicator but required for claims about profitable calls/puts.

If missing D0/D1, build only engineering demos with conspicuous **SIMULATED / NO LIVE GEX** labels. Do not skip gate because dashboard looks persuasive.

## 8. Trading options: guardrails and quality of targets

- Define option choice *separately* from underlying signal: SPXW vs SPY/QQQ options, correct contract root, expiry, settlement, multiplier, quote age, minimum option bid/ask size, spread-to-premium ratio, IV, theta/gamma, fees, and market session cutoffs. Never carry 0DTE past user-defined exit/cutoff by default; no short naked options. No automation.
- Show **underlying price zone target**, not a guessed option premium target. If option price is modeled, display model range with IV/theta uncertainty and update it only from authorized quotes.
- No candidate if a valid target is closer than the stop, profile bins are unreliable, estimated gamma sign convention is conflicted, data is delayed > threshold, or option spread is unusually wide. This is a testable risk gate, not optimized after seeing outcomes.
- Review market events, opening/closing auctions and settlement mechanics by instrument. SPX and SPXW options have distinct conventions, and 0DTE trading stops are not uniform with non-expiring index options.

## 9. Proposed implementation stages and deliverables

| Stage | Work | Mandatory evidence / stop criterion |
|---|---|---|
| **00: Pivot & repo hygiene** | Snapshot branch/commit; document pivot, update README and publication docs, install this handoff as `docs/RESEARCH_DIRECTION_GEX.md`, preserve archive and stale absolute paths, run publication hooks; draft new protocol | `docs/PIVOT_DECISION_2026-10-11.md`, README update, new DRAFT protocol, stage report; existing 195-test baseline *rechecked*, not assumed |
| **01: GEX data feasibility** | Vendor matrix, confirm already accessible services, small authorized as-of historical/live samples and underlying data; inspect cost/licensing | `docs/GEX_DATA_FEASIBILITY.md`, anonymized schema+sample hashes, timestamps, vendor selection or precise BLOCKED decision; **no historical P&L yet** |
| **02: Causal confluences** | GEX model/flip/strike zones, EMA(5m), trade-print/1m-proxy volume profile, normalized symbol mapping, feed freshness; read-only dashboard mock | Tests/golden fixtures, parity reports, labeled synthetic mode; dry-run displays no statistical signals when unavailable |
| **03: Registered historical research** | Only if D0 passes; pre-frozen candidate inventory, causal replay, WFA/cost/latency; incremental feature tests | Full reproducible results, rejected variants, sensitivity curves and D0–D3 scorecard; *no* old holdout consumption |
| **04: Prospective shadow indicator** | Read-only current market monitor, append-only tick/snapshot and signal log, manual advisory alerts, outage recovery and shadow review | Prospective session reports and timing audit; non-repainting proof, no broker orders |
| **05: Options executable P&L** | Historical real listed options NBBO with size, dates, rules, fees and settlement; option contract chooser in separate module | Contract-level trade log, conservative costs, option-specific WFA and risk proof. Not a prerequisite for an **information-only** dashboard, but required for claims of trading profitability |

**Stage reporting contract:** every stage report states latest commit SHA, task status PASS/PARTIAL/BLOCKED/FAIL, list of files changed, exact tests run + pass counts, data source/coverage/timestamps/cost/rights, archived SHA provenance, figures, limitations, candidate results positive *and negative*, robustness-gate status, holdout untouched confirmation, next single action and files for reviewer. Update `reports/PROJECT_STATUS.md` with **new GEX status and unchanged Phase A historical status**. Stage files should be self-contained. Do not simply say 'complete' without source files or output evidence.

## 10. Suggested first Codex execution (without presuming vendor credentials)

1. Inspect the renamed GitHub remote and working tree, read documents, verify legacy test suite without economic replay, and preserve current state.
2. Make new `experiments/gex_v1/PROTOCOL_DRAFT.md` and decision record explicitly **not frozen** until data availability is established.
3. Update root README (merge with supplied `GEX_Indicator_README_Proposed_v2.md`) but archive Phase A prior results, old commands, source-provenance risks and sealed holdout.
4. Build `docs/GEX_DATA_FEASIBILITY.md`, with provider matrix, live/historic capability probes as separate tasks, **no API procurement**. Use existing credentials only if present in local environment and explicitly authorized for read-only usage; never print keys.
5. Provide a minimal local **read-only** UI prototype using fixtures or `DATA_UNAVAILABLE` states: EMA/profile plotting can be based on Alpaca historical data, but GEX bars/levels must be labeled synthetic unless authentic samples are acquired.
6. Generate Stage 00 and 01 reports (blocked is valid), updated `reports/PROJECT_STATUS.md`, tests, and specific user decisions (vendor spend and data license). Stop before evaluating economic outcomes.

## 11. References and evidence hierarchy (revised for screenshot-level hypotheses)

External provider claims are **capabilities advertised by the linked publisher**, not confirmed entitlements, live availability, data quality, or profitability. Check again before purchase:

1. [Cboe, What Is Gamma Hedging?](https://www.cboe.com/insights/posts/volatility-insights-evaluating-the-market-impact-of-spx-0-dte-options/) — long/short dealer-gamma hedging intuition.
2. [Databento: OPRA options definitions and 0DTE SPXW](https://databento.com/docs/examples/options/zero-dte-options); [open interest published before RTH](https://databento.com/docs/examples/options/equity-open-interest); [OPRA contract/quote data](https://databento.com/docs/examples/options/equity-options-introduction/using-parent-symbology-to-fetch-an-option-chain).
3. [Cboe DataShop, Option Quote Intervals](https://datashop.cboe.com/option-quote-intervals) — 1-minute NBBO, optional Greeks/OI, delivery limitations.
4. [Massive options REST overview](https://massive.com/docs/rest/options) and [index coverage](https://massive.com/options) — snapshots vs historical tick quotes.
5. [Intrinio historical EOD options](https://intrinio.com/options/eod-historical-options) — historical EOD Greeks/OI not an intraday replay by itself.
6. [Quant Data US GEX API](https://help.quantdata.us/en/articles/15807345-gamma-exposure-gex-api-python-quickstart-dealer-positioning-guide) — per-strike exposure, interval map, advertised 365+ day lookback.
7. [SpotGamma official API/export answer](https://support.spotgamma.com/hc/en-us/articles/50266085426195-Does-SpotGamma-have-an-API-Can-I-export-data) — current export, **no public API**.
8. [TradingView: VP definitions and HVNs](https://www.tradingview.com/support/solutions/43000502040-volume-profile-indicators-basic-concepts/) and [Pine `request.footprint()`](https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/) — proprietary chart/footprint methodology and eligibility limits.
9. [TradingView Pine request limitations](https://www.tradingview.com/pine-script-docs/writing/limitations/); [outbound webhooks](https://www.tradingview.com/support/solutions/43000529348-how-to-configure-webhook-alerts/); [Advanced Charts Datafeed API](https://www.tradingview.com/charting-library-docs/latest/connecting_data/datafeed-api/).
10. [SpotGamma data source](https://support.spotgamma.com/hc/en-us/articles/50266146223123-Where-does-SpotGamma-s-data-come-from) — proprietary option positioning derived from OPRA and exchange feeds.



**Primary / authoritative independent evidence added in v2:**

11. [Cboe/Amaya, Garcia-Ares, Pearson, Vasquez (2025), *0DTE Index Options and Market Volatility: How Large is Their Impact?*](https://cdn.cboe.com/resources/education/research_publications/gammasqueezes.pdf). Uses proprietary actual participant-position estimates; long-gamma dampening / short-gamma amplification is conditional and often not large relative to other market forces.
12. [Cboe (2025), *0DTEs Decoded: Positioning, Trends, and Market Impact*](https://www.cboe.com/insights/posts/0-dt-es-decoded-positioning-trends-and-market-impact) — real dealer-flow estimates and net hedging relative to SPX liquidity, not evidence that all 0DTE volume has the same effect.
13. [*Option gamma and stock returns*, Journal of Empirical Finance 74 (2023)](https://doi.org/10.1016/j.jempfin.2023.101442) — signed exposure and hedging pressure associated with price/volatility; stock-level results are **not** validated index-wall T1 entries.
14. [Ni, Pearson & Poteshman (2005), *Stock price clustering on option expiration dates*, Journal of Financial Economics](https://doi.org/10.1016/j.jfineco.2004.08.005) — particular expiration-date stock clustering; not blanket confirmation of modern SPY intraday 'wall' strength.
15. [Barbon & Buraschi, *Gamma Fragility*, SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3725454) — gamma imbalance times underlying illiquidity predicts conditional momentum/reversal in stocks; a working-paper source.
16. [Cboe DataShop FAQs](https://datashop.cboe.com/faqs) — start-of-day prior-night OCC OI static until following morning; options multipliers/non-standard roots.
17. [TradingView, *Volume Profile Indicators: Basic Concepts*](https://www.tradingview.com/support/solutions/43000502040-volume-profile-indicators-basic-concepts/) — POC/VAH/VAL/HVN/LVN definitions, bar-based approximation, profile is reactive not a forecast.
18. [CME Group, *What is Volume?*](https://www.cmegroup.com/education/courses/introduction-to-futures/what-is-volume) — high volume does not reveal positioning direction or guarantee reversals.
19. [TradingView Pine `request.footprint()` official documentation](https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/) — bar footprint features, `na` handling, Premium/Ultimate plan eligibility, source/timeframe limitations.

**Recent working papers / counterevidence (NOT peer-reviewed findings, must verify/replicate):**

20. [Popovici (2026), *Do Gamma-Exposure Walls Exhibit Strike-Local Effects? A Pre-Registered, Control-Matched Test of Strike-Local Dealer-Gamma Effects in SPY*](https://ssrn.com/abstract=7082418) — preregistered test reports that #1 wall has no significant advantage versus ranks 2–5; motivates mandatory matched-wall controls, **not conclusive universal falsification**.
21. [Chilingarian (rev. Oct 2026), *The Sign of Dealer Gamma: An Inventory Convention, a Scale, and Two Definitions of the Gamma Flip*](https://ssrn.com/abstract=7131778) — challenges the assumption that per-strike sign crossings and repriced portfolio roots are interchangeable; motivates root stability and sign-model testing.

**Evidence hierarchy for decisions:** actual vendor documentation for data semantics; Cboe participant-data studies and peer-reviewed papers for potential mechanism; independently validated development and prospective results for *this* indicator's success; SSRN/new vendor commentary as exploratory questions, never as permission to assert profitability. Provider dashboard color, green/red heatmap, snapshot magnitude and stock-analogy are not themselves empirical evidence.

**Provenance:** The original repository Phase A facts above are based on its versioned README, `reports/PROJECT_STATUS.md`, and historical research reports reviewed 2026-10-11; do not treat those prior performance reports as evidence that the NEW GEX model succeeds or fails. Nothing in this document authorizes running or consuming the old sealed holdout.
