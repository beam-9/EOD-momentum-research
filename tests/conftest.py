"""All generators in this directory are SYNTHETIC TEST ONLY."""
from datetime import timedelta

import numpy as np
import polars as pl
import pytest

from eod_momentum.calendar import expected_minutes, sessions
from eod_momentum.common import config
from eod_momentum.data import normalize


def synthetic(start='2024-03-07', end='2024-03-08', symbols=('SPY',)):
    rng = np.random.default_rng(71)
    rows = []
    for symbol in symbols:
        price = 100.0
        for session in sessions(start, end):
            for t in expected_minutes(session):
                close = price * (1 + rng.normal(0, 0.0001))
                rows.append({'symbol': symbol, 'timestamp_utc': t, 'open': price,
                             'high': max(price, close) + 0.01, 'low': min(price, close) - 0.01,
                             'close': close, 'volume': 10000})
                price = close
    return normalize(pl.DataFrame(rows), source='SYNTHETIC_TEST_ONLY', feed='TEST', synthetic=True)


@pytest.fixture(scope='session')
def bars():
    return synthetic()


@pytest.fixture
def cfg():
    return config()


@pytest.fixture
def feature(bars):
    from eod_momentum.common import stamp
    return {'symbol': 'SPY', 'date': '2024-03-08', 'r_pre': 0.01,
            'decision_at': stamp('2024-03-08', '15:31'),
            'feature_available_at': stamp('2024-03-08', '15:30') + timedelta(seconds=30)}
