"""Data-gated option/GEX utilities, never spot-to-option P&L substitution."""
import math

from .engine import validate_quote


OPTION_FIELDS = ['underlying', 'occ_symbol', 'root', 'timestamp_utc', 'available_at_utc',
                 'expiry_date', 'option_type', 'strike', 'multiplier', 'exercise_style',
                 'settlement_type', 'bid', 'ask', 'bid_size', 'ask_size', 'source']


def gex(contracts, spot, r_pre, liquidity_dollars, sign_model):
    if spot <= 0 or liquidity_dollars <= 0:
        raise ValueError('Invalid spot/liquidity units')
    if sign_model not in ['all_dealer_short', 'call_long_put_short', 'magnitude']:
        raise ValueError('Unknown inventory-sign hypothesis')
    total = 0
    for c in contracts:
        if not all(math.isfinite(c[k]) and c[k] >= 0 for k in ['gamma', 'open_interest', 'multiplier']):
            raise ValueError('Invalid gamma/OI/multiplier')
        sign = -1 if sign_model == 'all_dealer_short' else (
            1 if sign_model == 'magnitude' or c['option_type'] == 'call' else -1)
        total += sign * c['gamma'] * c['open_interest'] * c['multiplier'] * spot ** 2 * 0.01
    hedge = -(r_pre / 0.01) * total
    return {'dollar_gex_per_1pct': total, 'estimated_hedge_dollars': hedge,
            'normalized_pressure': hedge / liquidity_dollars,
            'inventory_status': 'MODELLED_NOT_OBSERVED'}


def eligible_chain(contracts, *, decision_at, prior_session_date):
    result = []
    for c in contracts:
        if c['timestamp_utc'] > decision_at or c['available_at_utc'] > decision_at:
            raise ValueError('FUTURE_OPTION_CHAIN')
        if 'open_interest' in c:
            from datetime import date
            try:
                oi_date = date.fromisoformat(str(c.get('oi_asof_date')))
            except (ValueError, TypeError):
                raise ValueError('OI_NOT_PREVIOUS_NIGHT: OI_DATE_MISSING_OR_INVALID') from None
            if oi_date > date.fromisoformat(str(prior_session_date)):
                raise ValueError('OI_NOT_PREVIOUS_NIGHT')
        if c.get('listed_at_utc', c['available_at_utc']) > decision_at:
            raise ValueError('CONTRACT_NOT_YET_LISTED')
        result.append(c)
    return result


def select_atm(contracts, spot, direction, expiry):
    kind = 'call' if direction > 0 else 'put'
    eligible = [c for c in contracts if c['option_type'] == kind and str(c['expiry_date']) == str(expiry)]
    if not eligible:
        raise ValueError('NO_LISTED_0DTE_CONTRACT')
    return min(eligible, key=lambda c: (abs(c['strike'] - spot), c['strike'], c['occ_symbol']))


def long_option_trade(contract, entry_quote, exit_quote, *, entry_decision, exit_decision,
                      entry_fill_at, exit_fill_at, contracts=1, fee_per_side=0.65):
    if not (entry_decision < entry_fill_at < exit_decision < exit_fill_at):
        raise ValueError('Invalid option order chronology')
    if (contract['multiplier'] <= 0 or contracts < 1 or fee_per_side < 0 or
            isinstance(contracts, bool) or int(contracts) != contracts):
        raise ValueError('Invalid contract units')
    ask = validate_quote(1, decision=entry_fill_at, **entry_quote, quantity=contracts)
    bid = validate_quote(-1, decision=exit_fill_at, **exit_quote, quantity=contracts)
    premium = ask * contract['multiplier'] * contracts
    fees = 2 * contracts * fee_per_side
    return {'premium_spent': premium, 'gross_pnl': (bid - ask) * contract['multiplier'] * contracts,
            'fees': fees, 'net_pnl': (bid - ask) * contract['multiplier'] * contracts - fees,
            'max_loss_paid_premium_plus_fees': premium + fees,
            'fill_status': 'SNAPSHOT_NBBO_PROXY_REQUIRES_ARRIVAL_VALIDATION'}
