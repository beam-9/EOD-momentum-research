from datetime import timedelta

import polars as pl
import pytest

from eod_momentum.common import dump, stamp
from eod_momentum.engine import costs, screening_reference, simulate, validate_quote


def test_hand_calculated_three_minute_trace(feature, tmp_path):
    # Only execution trade events: 15:32, 15:33, 15:58. Information arrives before decision.
    f = pl.DataFrame({'symbol': ['SPY'] * 3,
                      'timestamp_utc': [stamp(feature['date'], x) for x in ['15:32', '15:33', '15:58']],
                      'open': [100., 100.5, 101.]})
    t = simulate(feature, f, 1, slippage=3, trace=True)
    assert t['gross'] == pytest.approx(0.01)
    assert t['slippage'] == pytest.approx(0.0006)
    assert t['net'] == pytest.approx(0.0094)
    assert t['submitted_at'] < t['eligible_at'] < t['filled_at']
    assert t['exit_submitted_at'] < t['exit_at']
    assert len(t['events']) == 7
    dump(tmp_path / 'trace.json', {'SYNTHETIC_TEST_ONLY': True, **t})


@pytest.mark.parametrize('q', [-1, 0, 1])
@pytest.mark.parametrize('slip', [0, 1, 3, 5])
def test_independent_engine_parity(bars, feature, q, slip):
    day = bars.filter(pl.col('timestamp_utc') >= stamp('2024-03-08', '09:30'))
    event = simulate(feature, day, q, slippage=slip, commission=0.1)
    ref = screening_reference(feature, day, q, slippage=slip, commission=0.1)
    assert event['net'] == pytest.approx(ref, abs=1e-12)
    assert event['gross'] - event['slippage'] - event['fees'] == event['net']


def test_costs_per_side():
    assert costs(1, 3, 0.1) == pytest.approx((0.0006, 0.00002))
    assert costs(0, 3) == (0, 0)
    with pytest.raises(ValueError):
        costs(1, -1)


def test_late_order_rejected(bars, feature):
    t = simulate(feature, bars, 1, arrival_seconds=60)
    assert t['q'] == 0 and t['net'] == 0
    assert t['reject_reason'] == 'ARRIVAL_NOT_STRICTLY_BEFORE_FILL'


def test_same_bar_entry_forbidden(bars, feature):
    with pytest.raises(ValueError, match='Invalid session'):
        simulate(feature, bars, 1, entry='15:31')


def test_missing_entry_reject(bars, feature):
    missing = bars.filter(pl.col('timestamp_utc') != stamp('2024-03-08', '15:32'))
    t = simulate(feature, missing, 1)
    assert t['q'] == 0 and t['reject_reason'] == 'MISSING_ENTRY_EVENT'


def test_missing_exit_not_hidden(bars, feature):
    missing = bars.filter(pl.col('timestamp_utc') != stamp('2024-03-08', '15:58'))
    with pytest.raises(ValueError, match='MISSING_SCHEDULED_FLATTEN'):
        simulate(feature, missing, 1)


def test_future_feature_rejected(bars, feature):
    feature['feature_available_at'] = feature['decision_at'] + timedelta(seconds=1)
    with pytest.raises(ValueError, match='unavailable'):
        simulate(feature, bars, 1)


def test_order_event_sorting(bars, feature):
    t = simulate(feature, bars, 1, trace=True)
    times = [e['event_time_utc'] for e in t['events']]
    assert times == sorted(times)
    assert len({e['event_id'] for e in t['events']}) == len(times)


@pytest.mark.parametrize('fault', ['future', 'stale', 'crossed', 'locked', 'wide', 'size'])
def test_nbbo_rejections(feature, fault):
    t = feature['decision_at']
    quote = dict(timestamp=t, bid=1.0, ask=1.05, bid_size=5, ask_size=5)
    if fault == 'future':
        quote['timestamp'] = t + timedelta(seconds=1)
    elif fault == 'stale':
        quote['timestamp'] = t - timedelta(seconds=30)
    elif fault == 'crossed':
        quote['bid'] = 2
    elif fault == 'locked':
        quote['bid'] = 1.05
    elif fault == 'wide':
        quote['ask'] = 3
    elif fault == 'size':
        quote['ask_size'] = 0
    with pytest.raises(ValueError):
        validate_quote(1, decision=t, **quote)


def test_holiday_fill_forbidden(bars, feature):
    feature['date'] = '2024-07-04'
    with pytest.raises(ValueError, match='calendar session'):
        simulate(feature, bars, 1)


def test_mixed_instrument_events_forbidden(bars, feature):
    mixed = pl.concat([bars, bars.with_columns(pl.lit('QQQ').alias('symbol'))])
    with pytest.raises(ValueError, match='instrument'):
        simulate(feature, mixed, 1)
