# Independent Phase D ETF proxy protocol — preregistered before execution

SPY entry IBS < 0.20; QQQ entry IBS < 0.10. Exit an existing position only at a
later eligible daily check with IBS > 0.50. One long position per ETF, no stops or
targets. These ETF proxies do not reproduce US500/US100 CFD contracts or claims.
No optimization, probabilities, or Phase A strategy selection. No pooled ticker
observations. A negative result is retained.

At 15:55 America/New_York, include only economic bar intervals ending by the
check AND prices available by the check. With assumed 30-second publication,
the most recent minute starts at 15:53. Include the available prefix range only.
Submit after the check; fill at 15:56 minute-open proxy, separately stress 15:57
and 15:58 with decisions delayed to 15:56 and 15:57 respectively. The economic
cutoff remains 15:55; later receipts may reveal completed intervals by that cutoff,
never later economic bars. Latest eligible mark may be at most 60 seconds old
plus the explicitly simulated decision delay; older prefixes fail loudly. Scheduled fill must occur after submission plus one-second arrival.
Daily equity marks use the final regular-session minute close, explicitly not
an official auction close. Overnight gaps use next session open and prior close.
Daily close marks are accounting valuations, never pre-decision inputs.

Size from 20 true ranges of the prior 21 fully completed sessions, whose entire
input history must be available by decision: floor(1000 / ATR). Cap purchase by
available cash including adverse fill and commission; initial capital 100000 per
independent ETF. No leverage or reinvestment sizing beyond the fixed ATR risk
budget. Adverse prices apply configured per-side bps; commission is additional.
Financing accrues on prior-close open notional for actual elapsed calendar days,
ACT/365. Default zero financing is an assumption, not historical broker financing.
ATR risk budget is not a stop or maximum loss. End positions remain open and
marked; unrealized losses are never discarded or force-closed for convenience.

Default sample excludes the sealed Phase A holdout from holdout_start onward.
This is a fixed-rule chronological path, not a trained or optimized walk-forward
strategy. Daily MTM may be attributed to calendar outer test folds without
restarting positions; folds do not create independent overlapping trade labels.
No model trains on carried position states. Separate scenario books start flat.
Warmup requires 21 prior daily sessions. Missing/incomplete sessions while held
abort the simulation rather than erase exposure. Complete half-days are marked
and enter ATR history; there is no 15:55 decision on them. Known corporate actions
while held abort pending proper entitlement accounting; flat action dates reset
ATR warmup. Unknown action history blocks any validation claim.

Output separate daily equity, order/fill logs, realized/unrealized P&L, gaps,
fees, financing, exposure, underwater curves and date-block uncertainty when
estimable. Synthetic fixtures are tests only, never market findings. No data
means NO_REAL_HISTORICAL_BACKTEST with null performance and no profit charts.
No CFD, intraday margin, actual NBBO, live timing, Pine or deployability claims.
