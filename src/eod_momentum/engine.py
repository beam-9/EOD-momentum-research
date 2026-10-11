"""Authoritative event-clock engine; signed constant-notional return ledger."""
from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from datetime import timedelta

import polars as pl

from .calendar import sessions
from .common import digest, stamp


@dataclass(order=True)
class Event:
    time: object
    priority: int
    kind: str = field(compare=False)
    payload: dict = field(default_factory=dict, compare=False)


def costs(q, slippage_bps_side, commission_bps_side=0.0):
    if slippage_bps_side < 0 or commission_bps_side < 0:
        raise ValueError('Negative friction')
    return (2 * slippage_bps_side * 1e-4 * abs(q), 2 * commission_bps_side * 1e-4 * abs(q))


def simulate(feature, bars, q, *, entry='15:32', exit='15:58', slippage=3.0, commission=0.0,
             arrival_seconds=1.0, trace=False):
    if q not in [-1, 0, 1]:
        raise ValueError('Invalid position')
    day, symbol = feature['date'], feature['symbol']
    session = sessions(day, day)
    if not session or session[0]['early']:
        raise ValueError('Unsupported calendar session or early close')
    if 'symbol' in bars.columns and (bars['symbol'] != symbol).any():
        raise ValueError('Mixed or mismatched instrument price events')
    dec, avail = feature['decision_at'], feature['feature_available_at']
    enter, leave = stamp(day, entry), stamp(day, exit)
    if not session[0]['open'] <= dec < session[0]['close']:
        raise ValueError('Decision outside session')
    if avail > dec:
        raise ValueError('Feature unavailable at decision')
    if not (dec < enter < leave < stamp(day, '16:00')):
        raise ValueError('Invalid session execution window')
    if arrival_seconds < 0:
        raise ValueError('Negative latency')
    # Price events are the first trade of a minute, only revealed when event clock reaches it.
    prices = {r['timestamp_utc']: r['open'] for r in bars.to_dicts()}
    submit = dec + timedelta(microseconds=1)
    eligible = submit + timedelta(seconds=arrival_seconds)
    exit_submit = leave - timedelta(seconds=arrival_seconds + 1)
    exit_eligible = exit_submit + timedelta(seconds=arrival_seconds)
    if exit_submit <= enter:
        raise ValueError('Invalid exit order timing')
    events = [Event(avail, 0, 'INFORMATION'), Event(dec, 1, 'DECISION'),
              Event(submit, 2, 'SUBMIT_ENTRY'), Event(eligible, 3, 'ACK_ENTRY'),
              Event(enter, 4, 'ENTRY_TRADE'), Event(exit_submit, 5, 'SUBMIT_EXIT'),
              Event(leave, 6, 'EXIT_TRADE')]
    heapq.heapify(events)
    log, position, entry_price, exit_price, reject = [], 0, None, None, None
    for_order = False
    while events:
        ev = heapq.heappop(events)
        payload = {}
        if ev.kind == 'SUBMIT_ENTRY':
            for_order = bool(q)
        elif ev.kind == 'ENTRY_TRADE' and for_order:
            if eligible >= ev.time:
                reject = 'ARRIVAL_NOT_STRICTLY_BEFORE_FILL'
            elif ev.time not in prices:
                reject = 'MISSING_ENTRY_EVENT'
            else:
                entry_price = prices[ev.time]
                position = q
                payload = {'fill_price': entry_price, 'size': q, 'eligible_at': eligible,
                           'decision_time': dec, 'submitted_at': submit}
        elif ev.kind == 'EXIT_TRADE' and position:
            if exit_eligible >= ev.time:
                raise ValueError('EXIT_ORDER_NOT_ELIGIBLE')
            if ev.time not in prices:
                # Missing flatten price invalidates session; never quietly discard an open loss.
                raise ValueError('MISSING_SCHEDULED_FLATTEN: cannot value terminal position')
            exit_price = prices[ev.time]
            position = 0
            payload = {'fill_price': exit_price, 'size': -q, 'submitted_at': exit_submit,
                       'eligible_at': exit_eligible}
        if trace:
            log.append({'event_id': digest([symbol, day, ev.kind, ev.time])[:20],
                        'event_time_utc': ev.time, 'information_available_at_utc': avail,
                        'event_kind': ev.kind, 'symbol': symbol,
                        'payload_source': 'ASSUMED_BAR_OPEN_PROXY', **payload})
    executed = entry_price is not None and exit_price is not None
    slip, fees = costs(q if executed else 0, slippage, commission)
    gross = q * (exit_price / entry_price - 1) if executed else 0.0
    return {'symbol': symbol, 'date': day, 'q': q if executed else 0, 'signal': q,
            'decision_at': dec, 'feature_available_at': avail, 'submitted_at': submit,
            'eligible_at': eligible, 'filled_at': enter if executed else None,
            'exit_submitted_at': exit_submit, 'exit_eligible_at': exit_eligible,
            'exit_at': leave if executed else None,
            'entry_price': entry_price, 'exit_price': exit_price, 'gross': gross,
            'slippage': slip, 'fees': fees, 'net': gross - slip - fees,
            'size': abs(q) if executed else 0, 'reject_reason': reject,
            'fill_model': 'FILL_PROXY_ONLY', 'slippage_model': 'ADDITIVE_RETURN_BPS_PER_SIDE',
            'exposure_minutes': (leave - enter).total_seconds() / 60 if executed else 0,
            'label_start_at': enter, 'label_end_at': leave, 'events': log}


def screening_reference(feature, bars, q, entry='15:32', exit='15:58', slippage=3, commission=0):
    """Independent array formula; screening only. Timing enforced separately by canonical engine."""
    marks = bars.with_columns(pl.col('bar_start_et').dt.strftime('%H:%M').alias('hm'))
    a = marks.filter(pl.col('hm') == entry)['open'].item()
    b = marks.filter(pl.col('hm') == exit)['open'].item()
    return q * (b / a - 1) - abs(q) * 2 * (slippage + commission) / 10000


def validate_quote(q, *, decision, timestamp, bid, ask, bid_size, ask_size,
                   quantity=1, max_age_seconds=30, max_spread_fraction=0.2):
    if not (timestamp <= decision and (decision - timestamp).total_seconds() < max_age_seconds):
        raise ValueError('STALE_OR_FUTURE_NBBO')
    if not (0 < bid < ask and (ask - bid) / ((ask + bid) / 2) <= max_spread_fraction):
        raise ValueError('INVALID_OR_WIDE_NBBO')
    if quantity <= 0 or min(bid_size, ask_size) < quantity:
        raise ValueError('INSUFFICIENT_DEPTH')
    return ask if q == 1 else bid
