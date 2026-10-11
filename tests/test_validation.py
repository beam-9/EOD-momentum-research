"""Synthetic unit fixtures only; no market evidence or performance claims."""
import json
from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

from eod_momentum import ledger
from eod_momentum.statistics import block_bootstrap, multiplicity
from eod_momentum.walk_forward import folds, in_interval, purge


def test_folds_half_open_contiguous_oos_and_sealed_holdout():
    windows = folds('2020-01-01', '2023-01-01')
    assert len(windows) == 7
    for window in windows:
        assert window['train_end'] == window['validation_start']
        assert window['validation_end'] == window['test_start']
        assert window['train_start'] < window['train_end'] < window['validation_end'] < window['test_end']
        assert window['test_end'] <= '2023-01-01'
        assert in_interval(window['test_start'], window['test_start'], window['test_end'])
        assert not in_interval(window['test_end'], window['test_start'], window['test_end'])
    assert all(left['test_end'] == right['test_start'] for left, right in zip(windows, windows[1:]))


def test_incomplete_outer_window_is_not_used():
    assert folds('2020-01-01', '2021-06-30') == []
    assert len(folds('2020-01-01', '2021-07-01')) == 1


def test_purge_overlapping_multiday_labels_and_touching_boundary():
    start = datetime(2024, 1, 10, tzinfo=timezone.utc)
    end = start + timedelta(days=3)
    intervals = [(start - timedelta(days=2), start - timedelta(microseconds=1)),
                 (start - timedelta(days=2), start),
                 (start - timedelta(days=2), start + timedelta(days=1)),
                 (start, start + timedelta(days=1)),
                 (start + timedelta(days=1), end + timedelta(days=3)),
                 (end, end + timedelta(days=1))]
    samples = [{'id': i, 'label_start_at': a, 'label_end_at': b} for i, (a, b) in enumerate(intervals)]
    assert [s['id'] for s in purge(samples, start, end)] == [0, 5]
    assert len(samples) == 6  # Does not alter the original ledger.


def test_nonoverlapping_intraday_labels_do_not_require_arbitrary_embargo():
    samples = [{'label_start_at': '2024-01-08T15:32', 'label_end_at': '2024-01-08T15:58'},
               {'label_start_at': '2024-01-09T15:32', 'label_end_at': '2024-01-09T15:58'}]
    assert purge(samples, '2024-01-10T15:32', '2024-01-10T15:58') == samples


def test_bootstrap_preserves_cross_asset_dates_and_seed():
    common = np.linspace(-0.02, 0.02, 100)
    panel = np.column_stack([common, -common])
    result = block_bootstrap(panel, samples=200, block=5, seed=22)
    assert result == block_bootstrap(panel, samples=200, block=5, seed=22)
    assert result['n_dates'] == 100
    assert result['mean_ci95'] == [0.0, 0.0]
    assert result['sharpe_ci95'] is None


def test_bootstrap_duplicated_ticker_is_not_extra_independent_dates():
    values = np.sin(np.arange(80)) * 0.01 + 0.001
    scalar = block_bootstrap(values, samples=100, seed=8)
    duplicate = block_bootstrap(np.column_stack([values, values]), samples=100, seed=8)
    assert scalar == duplicate
    assert block_bootstrap(np.ones((10, 500)))['status'] == 'NOT_ESTIMABLE'


def test_bootstrap_matches_manual_circular_block_resampling():
    values = np.arange(60, dtype=float) / 10000
    seed, count, block = 7, 100, 4
    rng = np.random.default_rng(seed)
    means = []
    for _ in range(count):
        starts = rng.integers(0, len(values), size=15)
        idx = ((starts[:, None] + np.arange(block)) % len(values)).ravel()
        means.append(values[idx].mean())
    actual = block_bootstrap(values, samples=count, block=block, seed=seed)
    assert actual['mean_ci95'] == pytest.approx(np.quantile(means, [0.025, 0.975]))


def test_bootstrap_nonfinite_input_fails():
    with pytest.raises(ValueError, match='Nonfinite'):
        block_bootstrap([np.nan] + [0.0] * 30)


def test_multiplicity_does_not_manufacture_dsr_or_pbo():
    result = multiplicity(80, 12)
    assert result['DSR']['status'] == result['PBO']['status'] == 'NOT_ESTIMABLE'
    assert result['deterministic_variants'] == 12


def test_trial_ledger_appends_and_detects_payload_tampering(tmp_path):
    path = tmp_path / 'trials.jsonl'
    first = ledger.append(path, {'model': 'flat', 'threshold': 0})
    second = ledger.append(path, {'model': 'momentum', 'threshold': 0.01})
    assert first['previous_hash'] == 'GENESIS'
    assert second['previous_hash'] == first['hash']
    assert [first['trial_id'], second['trial_id']] == [1, 2]
    records = [json.loads(line) for line in path.read_text().splitlines()]
    records[0]['threshold'] = 100
    path.write_text(''.join(json.dumps(row) + '\n' for row in records))
    with pytest.raises(ValueError, match='TRIAL_LEDGER_TAMPERED'):
        ledger.append(path, {'model': 'reversal'})
    assert len(path.read_text().splitlines()) == 2


def test_trial_ledger_detects_chain_break(tmp_path):
    path = tmp_path / 'trials.jsonl'
    ledger.append(path, {'model': 'flat'})
    ledger.append(path, {'model': 'long'})
    rows = path.read_text().splitlines()
    path.write_text(rows[1] + '\n')
    with pytest.raises(ValueError, match='TRIAL_LEDGER_TAMPERED'):
        ledger.append(path, {'model': 'short'})


@pytest.mark.parametrize('reserved', ['trial_id', 'registered_at', 'previous_hash', 'hash'])
def test_trial_record_cannot_override_chain_metadata(tmp_path, reserved):
    path = tmp_path / 'trials.jsonl'
    with pytest.raises(ValueError, match='reserved|RESERVED|metadata'):
        ledger.append(path, {'model': 'flat', reserved: 'forged'})
    assert not path.exists() or path.read_text() == ''


@pytest.mark.parametrize('field', ['train_months', 'validation_months', 'test_months'])
@pytest.mark.parametrize('value', [0, -1])
def test_walk_forward_requires_positive_windows(field, value):
    # A short limit makes even the pre-fix implementation terminate; never test a hanging loop.
    with pytest.raises(ValueError):
        folds('2020-01-01', '2020-02-01', **{field: value})


@pytest.mark.parametrize('holdout', ['2020-01-01', '2019-12-31'])
def test_walk_forward_requires_start_before_holdout(holdout):
    with pytest.raises(ValueError):
        folds('2020-01-01', holdout)


def test_prior_close_revision_after_today_decision_excludes_feature(bars, cfg):
    import polars as pl
    from eod_momentum.common import stamp
    from eod_momentum.data import audit
    from eod_momentum.features import build_features

    poisoned = bars.with_columns(
        pl.when(pl.col('timestamp_utc') == stamp('2024-03-07', '15:59'))
        .then(stamp('2024-03-08', '15:32'))
        .otherwise(pl.col('revision_available_at_utc'))
        .alias('revision_available_at_utc'))
    _, valid = audit(poisoned, '2024-03-07', '2024-03-08', ['SPY'])
    cfg['symbols'] = ['SPY']
    features, exclusions = build_features(valid, '2024-03-07', '2024-03-08', cfg)
    assert not features
    assert {'symbol': 'SPY', 'date': '2024-03-08',
            'reason': 'PRIOR_CLOSE_NOT_AVAILABLE'} in exclusions
