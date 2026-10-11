from datetime import datetime, timezone

import polars as pl
import pytest

from eod_momentum.calendar import expected_minutes, latest_completed, sessions, tokyo_cash_times
from eod_momentum.common import ET, digest, stamp
from eod_momentum.data import audit, normalize
from eod_momentum.features import build_features, features_asof, signal


def day(bars, d='2024-03-08'):
    return bars.filter(pl.col('bar_start_et').dt.date().cast(pl.String) == d)


def raw(bars):
    return bars.select(['symbol', 'timestamp_utc', 'open', 'high', 'low', 'close', 'volume'])


def test_calendar_dst():
    rows = sessions('2024-03-08', '2024-03-11')
    assert [r['open'].hour for r in rows] == [14, 13]
    assert all(len(expected_minutes(r)) == 390 for r in rows)
    assert stamp('2024-03-11', '15:30').astimezone(ET).hour == 15


def test_holiday_early_close():
    assert not sessions('2024-07-04', '2024-07-04')
    assert sessions('2024-11-29', '2024-11-29')[0]['early']


def test_completed_only():
    assert latest_completed(datetime(2024, 3, 11, 19, tzinfo=timezone.utc)) == '2024-03-08'
    assert latest_completed(datetime(2024, 3, 11, 21, tzinfo=timezone.utc)) == '2024-03-11'


def test_tokyo_change():
    assert tokyo_cash_times('2024-11-01')['check'] == '14:55'
    assert tokyo_cash_times('2024-11-05')['close'] == '15:30'
    assert not tokyo_cash_times('2024-11-05')['continuous_fill_at_check']


def test_quality_missing_full_session(bars):
    q, valid = audit(bars, '2024-03-07', '2024-03-11', ['SPY', 'QQQ'])
    assert len(valid) == 2
    assert len([r for r in q if 'MISSING_SESSION' in r['reasons']]) == 4


def test_missing_minute(bars):
    bad = bars.filter(pl.col('timestamp_utc') != stamp('2024-03-08', '10:00'))
    q, valid = audit(bad, '2024-03-07', '2024-03-08', ['SPY'])
    assert ('SPY', '2024-03-08') not in valid
    assert 'MISSING_MINUTES' in q[-1]['reasons']


@pytest.mark.parametrize('fault', ['duplicate', 'reverse', 'zero', 'bad_high', 'nan', 'fractional_minute'])
def test_invalid_bars_fail(bars, fault):
    f = raw(day(bars))
    if fault == 'duplicate':
        f = pl.concat([f, f.head(1)])
    if fault == 'reverse':
        f = f.reverse()
    if fault == 'zero':
        f = f.with_columns(pl.lit(0).alias('close'))
    if fault == 'bad_high':
        f = f.with_columns(pl.lit(1).alias('high'))
    if fault == 'nan':
        f = f.with_columns(pl.lit(float('nan')).alias('close'))
    if fault == 'fractional_minute':
        f = f.with_columns(pl.col('timestamp_utc') + pl.duration(seconds=1))
    with pytest.raises(ValueError):
        normalize(f, source='TEST', feed='TEST', synthetic=True)


def test_ambiguous_timezone(bars):
    f = raw(bars).with_columns(pl.col('timestamp_utc').dt.replace_time_zone(None))
    with pytest.raises(ValueError, match='Ambiguous timezone'):
        normalize(f, source='TEST', feed='TEST')


def test_availability_assumed_not_observed(bars):
    assert bars['first_available_at_utc'].null_count() == len(bars)
    assert bars['assumed_available_at_utc'].null_count() == 0
    assert bars['availability_basis'][0] == 'ASSUMED_FINAL_BAR'


def test_before_bar_end_rejected(bars):
    f = raw(bars).with_columns(pl.col('timestamp_utc').alias('first_available_at_utc'))
    with pytest.raises(ValueError, match='before economic end'):
        normalize(f, source='TEST', feed='TEST')


def test_cutoff_alignment(bars):
    f = features_asof(day(bars), 100, '2024-03-08')
    p = day(bars).filter(pl.col('timestamp_utc') == stamp('2024-03-08', '15:29'))['close'].item()
    assert f['cutoff_price'] == p
    assert f['mark_at'] == stamp('2024-03-08', '15:30')


def test_future_poison_rejected(bars):
    f = day(bars).with_columns(pl.when(pl.col('timestamp_utc') == stamp('2024-03-08', '15:29'))
                              .then(stamp('2024-03-08', '15:32')).otherwise(
                                  pl.col('assumed_available_at_utc')).alias('assumed_available_at_utc'))
    with pytest.raises(ValueError, match='FUTURE_INFORMATION'):
        features_asof(f, 100, '2024-03-08')


def test_revised_final_price_unavailable(bars):
    f = day(bars).with_columns(pl.lit(stamp('2024-03-08', '16:30')).alias('revision_available_at_utc'))
    with pytest.raises(ValueError, match='FUTURE_INFORMATION'):
        features_asof(f, 100, '2024-03-08')


def test_prefix_invariance(bars):
    f = day(bars)
    earlier = f.filter(pl.col('timestamp_utc') < stamp('2024-03-08', '15:30'))
    expected = digest(features_asof(earlier, 100, '2024-03-08'))
    changed = f.with_columns(pl.when(pl.col('timestamp_utc') >= stamp('2024-03-08', '15:30'))
                            .then(pl.col('close') * 10).otherwise(pl.col('close')).alias('close'))
    assert digest(features_asof(changed, 100, '2024-03-08')) == expected
    assert digest(features_asof(f, 100, '2024-03-08')) == expected


def test_online_replay_signal_parity(bars):
    batch = features_asof(day(bars), 100, '2024-03-08')
    arrived = []
    for row in day(bars).to_dicts():
        if row['assumed_available_at_utc'] <= stamp('2024-03-08', '15:31'):
            arrived.append(row)
    online = features_asof(pl.DataFrame(arrived), 100, '2024-03-08')
    assert digest(batch) == digest(online)


def test_prior_features_and_action_exclusion(bars, cfg):
    _, valid = audit(bars, '2024-03-07', '2024-03-08', ['SPY'])
    cfg['symbols'] = ['SPY']
    fs, exclusions = build_features(valid, '2024-03-07', '2024-03-08', cfg)
    assert len(fs) == 1 and len(exclusions) == 1
    none, ex = build_features(valid, '2024-03-07', '2024-03-08', cfg, {('SPY', '2024-03-08')})
    assert not none and len(ex) == 2


@pytest.mark.parametrize('model,r,theta,q', [('flat', 0.1, 0, 0), ('long', -0.1, 0, 1),
    ('short', 0.1, 0, -1), ('momentum', 0.01, 0, 1), ('reversal', 0.01, 0, -1),
    ('momentum', 0.001, 0.0025, 0), ('momentum', 0, 0, 0), ('momentum', -0.01, 0.005, -1)])
def test_signals(model, r, theta, q):
    assert signal({'r_pre': r}, model, theta) == q


def test_malicious_future_price_feature_rejected():
    with pytest.raises(ValueError, match='Unsupported feature'):
        signal({'r_pre': 0.01, 'future_price': 200}, 'momentum')
