"""Hand-calculated synthetic IBS/GEX/options contracts; never historical research."""
from datetime import datetime, timedelta, timezone

import pytest

from eod_momentum.ibs import Book, atr_size, ibs, prior_atr, run_proxy
from eod_momentum.options import eligible_chain, gex, long_option_trade, select_atm


T = datetime(2024, 3, 8, 20, 31, tzinfo=timezone.utc)


def test_ibs_range_and_zero_range():
    assert ibs(102, 110, 100) == pytest.approx(0.2)
    assert ibs(100, 100, 100) is None
    with pytest.raises(ValueError):
        ibs(99, 110, 100)


def test_atr_includes_gaps_and_size_uses_point_value_and_lot_increment():
    daily = [{'high': 101, 'low': 99, 'close': 100},
             {'high': 112, 'low': 108, 'close': 110},
             {'high': 111, 'low': 107, 'close': 108}]
    assert prior_atr(daily, period=2) == pytest.approx(8)
    assert atr_size(8, risk_currency=1000, point_value=10, lot_increment=5) == 10
    with pytest.raises(ValueError, match='ATR_REQUIRES'):
        prior_atr(daily[:2], period=2)
    with pytest.raises(ValueError):
        atr_size(0)


def test_ibs_open_loss_financing_calendar_gap_and_terminal_mark():
    book = Book()
    book.fill(100, 100, decision_at=T, filled_at=T + timedelta(seconds=1), fees=2)
    # Friday -> Monday: three calendar days financing, including weekends.
    equity = book.mark(90, elapsed_calendar_days=3, annual_financing=0.365, overnight_open=80)
    assert book.financing_paid == pytest.approx(27)
    assert book.worst_gap_pnl == pytest.approx(-2000)
    assert equity == pytest.approx(98971)
    assert book.shares == 100  # Open loss remains in equity.
    assert book.min_equity == pytest.approx(98971)


def test_ibs_margin_liquidation_preserves_loss():
    book = Book(cash=0, equity=100, min_equity=100)
    book.fill(10, 100, decision_at=T, filled_at=T + timedelta(seconds=1))
    assert book.mark(90, maintenance_fraction=0.25) == pytest.approx(-100)
    assert book.liquidated
    assert book.shares == 0
    assert book.cash == pytest.approx(-100)
    assert book.equity == pytest.approx(-100)


@pytest.mark.parametrize('offset', [-1, 0])
def test_ibs_requires_strictly_later_fill(offset):
    with pytest.raises(ValueError, match='after actual decision'):
        Book().fill(1, 100, decision_at=T, filled_at=T + timedelta(seconds=offset))


def check(day, mark, value, atr=10):
    time = datetime.fromisoformat(day + 'T20:31:00+00:00')
    return {'date': day, 'decision_at': time, 'filled_at': time + timedelta(minutes=1),
            'open': mark, 'mark': mark, 'fill_price': mark, 'ibs': value, 'prior_atr': atr}


def test_proxy_keeps_losing_open_position_and_rejects_date_reordering():
    observations = [check('2024-03-08', 100, 0.1), check('2024-03-11', 80, 0.2)]
    result = run_proxy(observations, threshold=0.2, risk_currency=100, bps_side=0)
    assert result['terminal_open_shares'] == 10
    assert result['terminal_equity'] == pytest.approx(99800)
    assert result['worst_gap_pnl'] == pytest.approx(-200)
    assert len(result['trades']) == 1
    with pytest.raises(ValueError, match='chronological'):
        run_proxy(observations[::-1], threshold=0.2)


def test_proxy_exit_friction_and_financing_are_distinct():
    result = run_proxy([check('2024-03-08', 100, 0.1), check('2024-03-11', 110, 0.8)],
                       threshold=0.2, risk_currency=100, bps_side=10, annual_financing=0.365)
    assert result['terminal_open_shares'] == 0
    assert result['daily'][-1]['financing_paid'] == pytest.approx(3.3)
    assert result['terminal_equity'] == pytest.approx(100000 + 100 - 1 - 1.1 - 3.3)


@pytest.mark.parametrize('model,total', [('all_dealer_short', -300),
                                        ('call_long_put_short', 100), ('magnitude', 300)])
def test_gex_sign_units_and_normalization(model, total):
    contracts = [{'option_type': 'call', 'gamma': 0.02, 'open_interest': 1, 'multiplier': 100},
                 {'option_type': 'put', 'gamma': 0.01, 'open_interest': 1, 'multiplier': 100}]
    result = gex(contracts, spot=100, r_pre=0.02, liquidity_dollars=10000, sign_model=model)
    assert result['dollar_gex_per_1pct'] == pytest.approx(total)
    assert result['estimated_hedge_dollars'] == pytest.approx(-2 * total)
    assert result['normalized_pressure'] == pytest.approx(-2 * total / 10000)
    assert result['inventory_status'] == 'MODELLED_NOT_OBSERVED'


def chain(**overrides):
    return {'timestamp_utc': T, 'available_at_utc': T, 'listed_at_utc': T - timedelta(days=10),
            'open_interest': 30, 'oi_asof_date': '2024-03-07', **overrides}


@pytest.mark.parametrize('field', ['timestamp_utc', 'available_at_utc', 'listed_at_utc'])
def test_future_chain_information_rejected(field):
    with pytest.raises(ValueError):
        eligible_chain([chain(**{field: T + timedelta(seconds=1)})], decision_at=T,
                       prior_session_date='2024-03-07')


@pytest.mark.parametrize('oi_date', ['2024-03-08', '2024-03-09', None])
def test_future_or_unknown_oi_rejected(oi_date):
    contract = chain()
    if oi_date is None:
        del contract['oi_asof_date']
    else:
        contract['oi_asof_date'] = oi_date
    with pytest.raises(ValueError, match='OI_NOT_PREVIOUS_NIGHT'):
        eligible_chain([contract], decision_at=T, prior_session_date='2024-03-07')


def test_previous_night_oi_chain_is_eligible():
    contracts = [chain()]
    assert eligible_chain(contracts, decision_at=T, prior_session_date='2024-03-07') == contracts


def test_atm_selection_expiry_type_and_deterministic_ties():
    contracts = [{'option_type': kind, 'expiry_date': expiry, 'strike': strike, 'occ_symbol': symbol}
                 for kind, expiry, strike, symbol in [('call', '2024-03-08', 99, 'B'),
                                                      ('call', '2024-03-08', 99, 'A'),
                                                      ('call', '2024-03-08', 101, 'C'),
                                                      ('put', '2024-03-08', 100, 'P'),
                                                      ('call', '2024-03-15', 100, 'F')]]
    assert select_atm(contracts, 100, 1, '2024-03-08')['occ_symbol'] == 'A'
    assert select_atm(contracts[::-1], 100, 1, '2024-03-08')['occ_symbol'] == 'A'
    assert select_atm(contracts, 100, -1, '2024-03-08')['occ_symbol'] == 'P'
    with pytest.raises(ValueError, match='NO_LISTED'):
        select_atm(contracts, 100, 1, '2024-03-09')


def option_trade(**overrides):
    args = {'contract': {'multiplier': 100},
            'entry_quote': dict(timestamp=T + timedelta(seconds=1), bid=1.95, ask=2.05,
                                bid_size=5, ask_size=5),
            'exit_quote': dict(timestamp=T + timedelta(minutes=27, seconds=1), bid=2.95, ask=3.05,
                               bid_size=5, ask_size=5),
            'entry_decision': T, 'entry_fill_at': T + timedelta(seconds=1),
            'exit_decision': T + timedelta(minutes=27),
            'exit_fill_at': T + timedelta(minutes=27, seconds=1), 'contracts': 2}
    return long_option_trade(**{**args, **overrides})


def test_option_pnl_uses_entry_ask_exit_bid_actual_premium_and_multiplier():
    result = option_trade()
    assert result['premium_spent'] == pytest.approx(410)
    assert result['gross_pnl'] == pytest.approx(180)
    assert result['fees'] == pytest.approx(2.6)
    assert result['net_pnl'] == pytest.approx(177.4)
    assert result['max_loss_paid_premium_plus_fees'] == pytest.approx(412.6)
    assert 'REQUIRES_ARRIVAL_VALIDATION' in result['fill_status']


def test_option_total_premium_loss_is_retained():
    quote = dict(timestamp=T + timedelta(minutes=27, seconds=1), bid=0.01, ask=0.011,
                 bid_size=5, ask_size=5)
    result = option_trade(exit_quote=quote)
    assert result['net_pnl'] == pytest.approx(-410.6)


def test_option_rejects_same_time_order_fill_and_insufficient_depth():
    with pytest.raises(ValueError, match='chronology'):
        option_trade(entry_fill_at=T)
    with pytest.raises(ValueError, match='INSUFFICIENT_DEPTH'):
        option_trade(contracts=6)
    with pytest.raises(ValueError, match='STALE_OR_FUTURE'):
        option_trade(exit_quote=dict(timestamp=T, bid=2.95, ask=3.05, bid_size=5, ask_size=5))


def test_option_contract_quantity_must_be_integral():
    with pytest.raises(ValueError, match='contract|units'):
        option_trade(contracts=1.5)


@pytest.mark.parametrize('oi_date', [None, '', 'not-a-date', '2024-19-45'])
def test_invalid_oi_date_fails_with_clear_data_contract_error(oi_date):
    with pytest.raises(ValueError, match='OI_'):
        eligible_chain([chain(oi_asof_date=oi_date)], decision_at=T, prior_session_date='2024-03-07')
