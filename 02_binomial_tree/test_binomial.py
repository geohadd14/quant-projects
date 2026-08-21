"""Tests for binomial.py - run `pytest` in this folder until green.

Work the hand-computable ones out on paper BEFORE writing code. The order
below is the order to implement in: get the first three green, then the tree,
then the American cases.
"""

import math

import numpy as np
import pytest

from binomial import (
    american_price,
    crr_parameters,
    european_price,
    risk_neutral_prob,
    terminal_prices,
)


# --------------------------------------------------------------- parameters --

def test_crr_up_and_down_are_reciprocal():
    """d = 1/u is what makes the tree recombine."""
    u, d = crr_parameters(sigma=0.2, dt=0.01)
    assert u * d == pytest.approx(1.0)


def test_crr_known_value():
    # sigma chosen so that u comes out at exactly 1.25 over a one-year step
    u, d = crr_parameters(sigma=math.log(1.25), dt=1.0)
    assert u == pytest.approx(1.25)
    assert d == pytest.approx(0.8)


def test_higher_vol_gives_a_wider_tree():
    u_calm, _ = crr_parameters(sigma=0.10, dt=1 / 252)
    u_wild, _ = crr_parameters(sigma=0.40, dt=1 / 252)
    assert u_wild > u_calm


# ------------------------------------------------------ risk-neutral measure --

def test_risk_neutral_prob_hand_computed():
    # r = 0, u = 1.25, d = 0.8  ->  p = (1 - 0.8) / (1.25 - 0.8) = 0.4444...
    p = risk_neutral_prob(r=0.0, q=0.0, dt=1.0, u=1.25, d=0.8)
    assert p == pytest.approx(0.2 / 0.45)


def test_risk_neutral_prob_is_a_probability():
    p = risk_neutral_prob(r=0.05, q=0.0, dt=1 / 252, u=1.02, d=1 / 1.02)
    assert 0.0 < p < 1.0


def test_arbitrage_inputs_are_rejected():
    """If the risk-free rate beats even the up move, the inputs are arbitrageable."""
    with pytest.raises(ValueError):
        risk_neutral_prob(r=0.50, q=0.0, dt=1.0, u=1.05, d=0.95)


# ------------------------------------------------------------ terminal nodes --

def test_terminal_prices_recombine():
    S = terminal_prices(S0=100.0, u=1.25, d=0.8, N=2)
    # two downs, one of each, two ups -> the middle node is back at S0
    np.testing.assert_allclose(S, [64.0, 100.0, 156.25])


def test_terminal_prices_count():
    assert len(terminal_prices(S0=100.0, u=1.1, d=1 / 1.1, N=50)) == 51


# ------------------------------------------------------------------- pricing --

def test_one_step_call_hand_computed():
    """S0=100, K=100, u=1.25, d=0.8, r=0.

    Payoffs: up -> 125, worth 25.  down -> 80, worth 0.
    p = 4/9, so price = (4/9) * 25 = 11.111...
    """
    price = european_price(S0=100.0, K=100.0, T=1.0, r=0.0,
                           sigma=math.log(1.25), N=1, kind="call")
    assert price == pytest.approx((4 / 9) * 25.0)


def test_put_call_parity_holds():
    """c - p = S0 - K*exp(-rT). The cleanest check that the tree is sane."""
    args = dict(S0=100.0, K=95.0, T=1.0, r=0.05, sigma=0.2, N=500)
    c = european_price(**args, kind="call")
    p = european_price(**args, kind="put")
    assert c - p == pytest.approx(100.0 - 95.0 * math.exp(-0.05 * 1.0), abs=1e-6)


def test_converges_to_black_scholes():
    """S=100, K=100, T=1, r=5%, sigma=20% -> Black-Scholes call = 10.4506.

    You will derive that number yourself in Project 2. For now it is the
    target the tree has to walk towards as N grows.
    """
    coarse = european_price(100.0, 100.0, 1.0, 0.05, 0.2, N=1, kind="call")
    fine = european_price(100.0, 100.0, 1.0, 0.05, 0.2, N=2000, kind="call")
    assert abs(fine - 10.4506) < abs(coarse - 10.4506)
    assert fine == pytest.approx(10.4506, abs=0.01)


def test_call_price_increases_with_volatility():
    """More vol, more optionality. If this fails, p or the payoff is wrong."""
    args = dict(S0=100.0, K=100.0, T=1.0, r=0.05, N=500, kind="call")
    assert (european_price(**args, sigma=0.30)
            > european_price(**args, sigma=0.15))


def test_call_price_increases_with_maturity():
    args = dict(S0=100.0, K=100.0, r=0.05, sigma=0.2, N=500, kind="call")
    assert european_price(**args, T=2.0) > european_price(**args, T=0.5)


# ------------------------------------------------------- American / exercise --

def test_american_put_beats_european_put():
    args = dict(S0=90.0, K=100.0, T=1.0, r=0.05, sigma=0.2, N=500)
    assert american_price(**args, kind="put") > european_price(**args, kind="put")


def test_american_call_equals_european_without_dividends():
    """The one every candidate should know and most get wrong.

    Exercising early throws away time value AND the protection against the
    stock falling below K. So for q = 0 it is never optimal, and the two
    prices must be identical.
    """
    args = dict(S0=100.0, K=95.0, T=1.0, r=0.05, sigma=0.25, N=500, q=0.0)
    assert american_price(**args, kind="call") == pytest.approx(
        european_price(**args, kind="call"), abs=1e-8
    )


def test_dividends_make_early_exercise_worth_something():
    """With a big enough dividend yield, early exercise on a call CAN pay."""
    args = dict(S0=100.0, K=95.0, T=1.0, r=0.02, sigma=0.25, N=500, q=0.12)
    assert american_price(**args, kind="call") > european_price(**args, kind="call")


def test_deep_itm_american_put_is_worth_intrinsic():
    """Far enough in the money, you exercise now and the price is just K - S."""
    price = american_price(S0=1.0, K=100.0, T=1.0, r=0.05, sigma=0.2,
                           N=500, kind="put")
    assert price == pytest.approx(99.0, abs=1e-6)
