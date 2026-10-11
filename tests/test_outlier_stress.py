"""Synthetic diagnostic regressions, never historical performance evidence."""
from copy import deepcopy

import pytest

from eod_momentum.research import drop_best_trades


def row(day, net, q):
    return {'date': day, 'net': net, 'gross': net + 0.0006 if q else 0.0,
            'q': q, 'fees': 0.0, 'slippage': 0.0006 if q else 0.0,
            'exposure_minutes': 26.0 if q else 0.0}


def test_removes_best_executed_loss_instead_of_flat_day():
    rows = [row('2024-01-02', 0.0, 0), row('2024-01-03', -0.001, 1),
            row('2024-01-04', -0.002, -1)]
    before = deepcopy(rows)
    result = drop_best_trades(rows, 1)
    assert len(result) == len(rows)
    assert result[0] == rows[0]
    assert result[1]['q'] == 0
    assert all(result[1][key] == 0 for key in ['net', 'gross', 'fees', 'slippage', 'exposure_minutes'])
    assert result[2] == rows[2]
    assert rows == before


def test_remove_five_caps_at_executed_count_and_preserves_calendar():
    rows = [row('2024-01-02', 0.0, 0), row('2024-01-03', 0.001, 1),
            row('2024-01-04', -0.001, -1)]
    result = drop_best_trades(rows, 5)
    assert [r['date'] for r in result] == [r['date'] for r in rows]
    assert all(r['q'] == r['net'] == r['exposure_minutes'] == 0 for r in result)
    assert drop_best_trades(rows, 0) == rows


def test_equal_returns_use_input_order_and_flat_book_is_unchanged():
    rows = [row('2024-01-02', 0.001, 1), row('2024-01-03', 0.001, -1)]
    assert [r['q'] for r in drop_best_trades(rows, 1)] == [0, -1]
    assert drop_best_trades([row('2024-01-02', 0.0, 0)], 5) == [row('2024-01-02', 0.0, 0)]
    with pytest.raises(ValueError, match='nonnegative'):
        drop_best_trades(rows, -1)
