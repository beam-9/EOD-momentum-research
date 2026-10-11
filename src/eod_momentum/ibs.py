"""Independent ETF IBS proxy bookkeeper. No broker/CFD replication claims."""
from dataclasses import dataclass

import numpy as np


def ibs(last, high, low):
    if high < low or not low <= last <= high:
        raise ValueError('Invalid observed range')
    return (last - low) / (high - low) if high > low else None


def prior_atr(daily, period=20):
    """Caller supplies only previously completed daily sessions."""
    if len(daily) < period + 1:
        raise ValueError('ATR_REQUIRES_PRIOR_COMPLETED_HISTORY')
    tr = [max(d['high'] - d['low'], abs(d['high'] - p['close']), abs(d['low'] - p['close']))
          for p, d in zip(daily, daily[1:])]
    return float(np.mean(tr[-period:]))


def atr_size(atr_points, risk_currency=1000, point_value=1, lot_increment=1):
    if min(atr_points, risk_currency, point_value, lot_increment) <= 0:
        raise ValueError('Invalid sizing units')
    return np.floor(risk_currency / (atr_points * point_value) / lot_increment) * lot_increment


@dataclass
class Book:
    cash: float = 100000
    shares: float = 0
    last_mark: float | None = None
    equity: float = 100000
    financing_paid: float = 0
    worst_gap_pnl: float = 0
    min_equity: float = 100000
    liquidated: bool = False

    def mark(self, price, *, elapsed_calendar_days=1, annual_financing=0, point_value=1,
             maintenance_fraction=0, overnight_open=None):
        if price <= 0 or elapsed_calendar_days < 0 or annual_financing < 0:
            raise ValueError('Invalid mark/financing')
        if overnight_open is not None and self.last_mark is not None:
            self.worst_gap_pnl = min(self.worst_gap_pnl,
                                     self.shares * point_value * (overnight_open - self.last_mark))
        charge = abs(self.shares) * price * point_value * annual_financing * elapsed_calendar_days / 365
        self.cash -= charge
        self.financing_paid += charge
        self.equity = self.cash + self.shares * price * point_value
        self.min_equity = min(self.min_equity, self.equity)
        if self.shares and self.equity < abs(self.shares) * price * point_value * maintenance_fraction:
            self.cash += self.shares * price * point_value
            self.shares = 0
            self.liquidated = True
        self.last_mark = price
        return self.equity

    def fill(self, quantity, price, *, decision_at, filled_at, fees=0, point_value=1):
        if filled_at <= decision_at:
            raise ValueError('IBS fill must be after actual decision')
        if price <= 0 or fees < 0 or self.shares + quantity < 0:
            raise ValueError('Invalid long-only IBS order')
        self.cash -= quantity * price * point_value + fees
        self.shares += quantity
        return self.mark(price, elapsed_calendar_days=0, point_value=point_value)


def run_proxy(checks, *, threshold, risk_currency=1000, capital=100000, bps_side=3,
              annual_financing=0, maintenance_fraction=0):
    """Chronological precomputed as-of checks; open positions explicitly remain marked at end.

    checks require date, decision_at, filled_at, open, mark, fill_price, ibs, prior_atr.
    Actual CFD spread, lot, swap and margin schedules are intentionally not inferred.
    """
    from datetime import date
    book = Book(cash=capital, equity=capital, min_equity=capital)
    daily, trades = [], []
    previous = None
    for c in checks:
        d = date.fromisoformat(c['date'])
        if previous is not None and d <= previous:
            raise ValueError('IBS checks must be chronological')
        days = (d - previous).days if previous else 0
        book.mark(c['mark'], elapsed_calendar_days=days, annual_financing=annual_financing,
                  overnight_open=c['open'], maintenance_fraction=maintenance_fraction)
        quantity = 0
        if not book.liquidated and c['ibs'] is not None:
            if not book.shares and c['ibs'] < threshold:
                size = atr_size(c['prior_atr'], risk_currency, lot_increment=1)
                quantity = min(size, np.floor(book.cash / (c['fill_price'] * (1 + bps_side / 10000))))
            elif book.shares and c['ibs'] > 0.5:
                quantity = -book.shares
        if quantity:
            fee = abs(quantity) * c['fill_price'] * bps_side / 10000
            book.fill(quantity, c['fill_price'], decision_at=c['decision_at'], filled_at=c['filled_at'], fees=fee)
            book.mark(c['mark'], elapsed_calendar_days=0)
            trades.append({**c, 'quantity': quantity, 'fees': fee})
        daily.append({'date': c['date'], 'equity': book.equity, 'shares': book.shares,
                      'financing_paid': book.financing_paid, 'liquidated': book.liquidated})
        previous = d
    return {'daily': daily, 'trades': trades, 'terminal_open_shares': book.shares,
            'terminal_equity': book.equity, 'worst_gap_pnl': book.worst_gap_pnl,
            'classification': 'ETF_PROXY_ONLY;DAILY_MARKS_MISS_INTRADAY_MARGIN_BREACHES'}
