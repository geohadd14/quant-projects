"""Black-Scholes closed form, only as the reference the tree converges to.

The full treatment with all five Greeks is project 03. This file exists so the
convergence plot has a horizontal line to walk into, and so the tree can be
checked against something that was derived a completely different way: the tree
discretises the stock, Black-Scholes solves a PDE in continuous time. Two
different derivations landing on the same number is the point.

The normal CDF is written with math.erf rather than pulling in scipy. It is one
line, and the repo stays on numpy plus matplotlib.
"""

import math


def norm_cdf(x):
    """Standard normal CDF, N(x). P(Z <= x) for Z ~ Normal(0, 1)."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def d1_d2(S0, K, T, r, sigma, q=0.0):
    """The two arguments the formula is built from.

    d1 = [ln(S0/K) + (r - q + sigma^2 / 2) * T] / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)

    N(d2) is the risk-neutral probability the option finishes in the money.
    N(d1) is that same probability reweighted by how much stock you end up
    holding, which is why it turns out to be the call's delta.
    """
    if T <= 0 or sigma <= 0:
        raise ValueError("T and sigma must be positive")
    vol_sqrt_t = sigma * math.sqrt(T)
    d1 = (math.log(S0 / K) + (r - q + 0.5 * sigma * sigma) * T) / vol_sqrt_t
    return d1, d1 - vol_sqrt_t


def call_price(S0, K, T, r, sigma, q=0.0):
    """European call. Hull ch 15."""
    d1, d2 = d1_d2(S0, K, T, r, sigma, q)
    return S0 * math.exp(-q * T) * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)


def put_price(S0, K, T, r, sigma, q=0.0):
    """European put. Same formula with the signs flipped."""
    d1, d2 = d1_d2(S0, K, T, r, sigma, q)
    return K * math.exp(-r * T) * norm_cdf(-d2) - S0 * math.exp(-q * T) * norm_cdf(-d1)
