from datetime import timedelta
from functools import lru_cache

import exchange_calendars as xcals
import pandas as pd

from .common import ET, utcnow


@lru_cache(maxsize=1)
def exchange():
    return xcals.get_calendar('XNYS', start='2000-01-01', end='2035-12-31')


def sessions(start, end):
    """Inclusive calendar dates, market session open/close in UTC."""
    cal = exchange()
    out = []
    for label in cal.sessions_in_range(str(start), str(end)):
        op = cal.session_open(label).to_pydatetime()
        cl = cal.session_close(label).to_pydatetime()
        out.append({'date': str(label.date()), 'open': op, 'close': cl,
                    'early': cl.astimezone(ET).hour != 16})
    return out


def latest_completed(now=None):
    now = now or utcnow()
    if now.tzinfo is None:
        raise ValueError('Clock must be timezone-aware')
    day = now.astimezone(ET).date()
    eligible = [s for s in sessions(day - timedelta(days=14), day) if s['close'] < now]
    return eligible[-1]['date']


def expected_minutes(session):
    return list(pd.date_range(session['open'], session['close'], freq='min', inclusive='left')
                .to_pydatetime())


def tokyo_cash_times(day):
    """Timing helper only; not a Tokyo holiday or CFD trading calendar."""
    if str(day) < '2024-11-05':
        return {'close': '15:00', 'check': '14:55', 'continuous_fill_at_check': True}
    return {'close': '15:30', 'check': '15:25', 'continuous_fill_at_check': False}
