"""Tests for payoffs.py - run `pytest` in this folder until everything is green.

Every number here is hand-checkable: work each one out on paper first,
THEN write the code. If a test surprises you, that's the learning moment.
"""

import numpy as np
import pytest

from payoffs import (
    call_payoff,
    put_payoff,
    long_pnl,
    short_pnl,
    straddle_pnl,
    bull_call_spread_pnl,
)


def test_call_payoff_itm_atm_otm():
    S = np.array([80.0, 100.0, 120.0])
    # K=100: worthless at 80 (why exercise a right to buy at 100 when spot is 80?),
    # worthless at 100, worth 20 at 120
    np.testing.assert_allclose(call_payoff(S, 100.0), [0.0, 0.0, 20.0])


def test_put_payoff_mirror_of_call():
    S = np.array([80.0, 100.0, 120.0])
    np.testing.assert_allclose(put_payoff(S, 100.0), [20.0, 0.0, 0.0])


def test_long_and_short_are_zero_sum():
    S = np.linspace(50, 150, 101)
    payoff = call_payoff(S, 100.0)
    total = long_pnl(payoff, 5.0) + short_pnl(payoff, 5.0)
    np.testing.assert_allclose(total, np.zeros_like(S))


def test_long_call_breakeven():
    # Paid 5 for a K=100 call -> breakeven at S=105, not at S=100.
    assert long_pnl(call_payoff(np.array([105.0]), 100.0), 5.0)[0] == pytest.approx(0.0)


def test_straddle_worst_case_is_at_the_strike():
    # Bought call (4) + put (3) at K=100. At S=K both expire worthless:
    # you lose exactly the total premium, 7. Anywhere else you lose less or win.
    S = np.array([100.0])
    assert straddle_pnl(S, 100.0, 4.0, 3.0)[0] == pytest.approx(-7.0)

    S_wide = np.linspace(50, 150, 201)
    pnl = straddle_pnl(S_wide, 100.0, 4.0, 3.0)
    assert pnl.min() == pytest.approx(-7.0)


def test_bull_call_spread_caps_both_ways():
    # Buy K=100 call for 6, sell K=110 call for 2 -> net cost 4.
    # Max loss = net cost (below 100). Max gain = (110-100) - 4 = 6 (above 110).
    S = np.array([80.0, 100.0, 110.0, 150.0])
    pnl = bull_call_spread_pnl(S, 100.0, 110.0, 6.0, 2.0)
    np.testing.assert_allclose(pnl, [-4.0, -4.0, 6.0, 6.0])
