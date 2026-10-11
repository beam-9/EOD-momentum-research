# Frozen research protocol — v1, 2026-10-09 (before outcome analysis)
Authoritative source: HANDOFF_v3.md. Primary SPY; QQQ is a dependent secondary replication.
Target 2023-01-03 through most recent completed XNYS session; full RTH minutes only.
Holdout starts 2026-04-10, ends after last completed session; sealed by default. Never shift it
based on outcomes. All final-bar availability is ASSUMED unless actual receipts are imported.
Raw transaction prices; action dates excluded when an authenticated action file exists; missing
action history blocks G1. Previous 15:59 close is a proxy, never called official auction close.
Economic feature: previous RTH close to 15:29 minute close; decision 15:31; scheduled submission
strictly before 15:32 entry and 15:58 exit. No stops, constant one-unit notional, flat overnight.
Costs are additive return bps per side, 0/1/3/5 slippage plus configured commission; no-interest/
no-borrow simplified baseline. Minute opens are FILL_PROXY_ONLY. NBBO subset validation required.
Finite families: flat/long/short, momentum and reversal x five thresholds (13 deterministic rules).
Add two validation-selected threshold procedures (one per M1 family) for 15 evaluated rules.
Null: 100 fixed-seed random-direction controls, all seeds reported as one diagnostic distribution.
Train 12 calendar months, inner validation 3, outer test 3, step 3. No overlapping outer tests.
Deterministic rules require no fitting. Threshold chosen solely by mean net validation session
return at 3 bps/side; ties use smallest threshold. No scaler/probability model in baseline.
Single final family+threshold chosen from development WFA only, after data/code/config hashes
are frozen. `holdout freeze` writes an immutable selection; `holdout evaluate` is one-time.
Primary metric mean OOS return per eligible date at 3 bps/side including no-trade zeros.
Circular moving-block bootstrap, block 5 dates, 2,000 replicates, seed 2049; joint-symbol portfolio
resampled by date, equal capital split. 95% intervals and bootstrap Sharpe intervals.
Prespecified stresses: +1/+2 minute arrival, 15:36/15:37 delayed arrival, exits 15:45/55/59,
2x/3x 3-bp friction, drop best 1/5 trades; all diagnostic, never optimization knobs.
Report all models including failed/no-trade variants. No fabricated price/options/CFD results.
Data exclusions: holidays, incomplete/invalid RTH, early closes, incomplete prior session,
actions when known, ambiguous timestamps, future/nonpositive prices and delayed required marks.
No arbitrary embargo for nonoverlapping intraday labels. Overlapping IBS labels purged separately.
G1 data and quote timing; G2 leakage/trials/untouched holdout; G3 positive conservative net mean
with CI excluding zero and benchmark lift; G4 fold/outlier/latency stability; G5 platform/quote
feasibility. Every gate must PASS. Any unknown means research-only. Minimum evidence guide:
200 independent OOS dates / 100 trades; no automatic inference of power from those numbers.
DSR/PBO default NOT_ESTIMABLE: dependent variants, no validated effective independent trial count.
No probability badge, Pine, options/GEX P&L or CFD replication without appropriate evidence.
Phase D is an independent ETF proxy only; no empirical CFD or margin claims without actual specs.
