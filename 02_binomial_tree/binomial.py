"""Binomial option pricer (Cox-Ross-Rubinstein).

Hull 11th ed, ch 13. You write the bodies; the docstrings carry the derivation
so you are never coding a formula you have not seen come from somewhere.

Conventions across this repo:
- S0    : spot price today
- K     : strike
- T     : time to expiry in years
- r     : continuously compounded risk-free rate (0.05 = 5%)
- sigma : annualised volatility (0.2 = 20%)
- N     : number of steps in the tree
- q     : continuous dividend yield (0.0 = no dividends)
- kind  : "call" or "put"

BEFORE YOU WRITE ANY CODE, do this on paper:
    S0 = 100, one step, u = 1.25, d = 0.8, r = 0, K = 100, call.
    Build the replicating portfolio: how many shares plus how much cash
    reproduces the option payoff in both states? What does that portfolio
    cost today? That cost IS the option price - no probabilities needed.
    Then check that the same number falls out of the risk-neutral formula.
Until those two agree in your handwriting, the code below is just typing.
"""

import numpy as np


# --- helpers -----------------------------------------------------------------
# Shared by both pricers so the European and American paths cannot drift apart.

def _payoff(S, K, kind):
    """Intrinsic value at stock price S. Works on a scalar or an array."""
    if kind == "call":
        return np.maximum(S - K, 0.0)
    if kind == "put":
        return np.maximum(K - S, 0.0)
    raise ValueError(f"kind must be 'call' or 'put', got {kind!r}")


def _tree_setup(T, r, sigma, N, q):
    """Return (u, d, p, discount_factor_for_one_step)."""
    if N < 1:
        raise ValueError("N must be at least 1")
    if T <= 0:
        raise ValueError("T must be positive")
    dt = T / N
    u, d = crr_parameters(sigma, dt)
    p = risk_neutral_prob(r, q, dt, u, d)
    return u, d, p, float(np.exp(-r * dt))


def crr_parameters(sigma, dt):
    """Return (u, d): the up and down multipliers for one step of length dt.

    Cox-Ross-Rubinstein pick u and d so the tree's log-returns have the same
    variance as the continuous model over each step:

        u = exp(sigma * sqrt(dt))
        d = 1 / u

    The tree recombines for ANY u and d, because up-then-down and down-then-up
    both land on S0 * u * d -- multiplication commutes. That is what gives N+1
    terminal nodes after N steps instead of 2^N, and it is the whole reason
    this is computationally sane.

    What d = 1/u adds is symmetry, not recombination: u * d = 1, so up-then-down
    returns exactly to S0 and the grid of log-prices stays centred on log(S0).

    Hull ch 13, eq. (13.15)-(13.16).
    """
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    if dt <= 0:
        raise ValueError("dt must be positive")
    u = np.exp(sigma * np.sqrt(dt))
    return u, 1.0 / u


def risk_neutral_prob(r, q, dt, u, d):
    """Return p: the risk-neutral probability of an up move.

    NOT the real-world probability, and not a forecast. It is the number that
    makes the stock earn the risk-free rate in expectation:

        E[S_next] = S0 * exp((r - q) * dt)
        p*u*S0 + (1-p)*d*S0 = S0 * exp((r - q) * dt)

    Cancel S0 and solve for p:

        p = (exp((r - q) * dt) - d) / (u - d)

    The point of risk-neutral valuation: once you price by discounting the
    expectation under p, you never need to know anyone's risk appetite or the
    stock's real drift. Both parties agree on the price even if they disagree
    completely about where the stock is going.

    Note p must land strictly between 0 and 1. If it does not, then either
    d >= exp((r-q)dt) or u <= exp((r-q)dt), and there is a riskless arbitrage
    in your inputs. Raise ValueError in that case rather than returning a
    nonsense probability - a silent bad p produces a plausible wrong price,
    which is the worst kind of bug.

    Hull ch 13, eq. (13.5).
    """
    if u <= d:
        raise ValueError(f"need u > d, got u={u} d={d}")
    growth = np.exp((r - q) * dt)
    p = (growth - d) / (u - d)
    # p outside (0, 1) means the riskless growth factor sits outside the range
    # the stock can reach in one step, so one side of the trade is free money.
    # Refuse, rather than return a number that prices without complaining.
    if not 0.0 < p < 1.0:
        raise ValueError(
            f"arbitrage in inputs: p={p:.6f} is not in (0, 1). "
            f"Need d < exp((r-q)dt) < u, got d={d:.6f} "
            f"exp={growth:.6f} u={u:.6f}"
        )
    return float(p)


def terminal_prices(S0, u, d, N):
    """Return the N+1 possible stock prices at expiry, lowest first.

    After N steps with j up moves and (N - j) down moves:

        S = S0 * u**j * d**(N - j)

    Build this as a numpy array, not a Python loop appending to a list - the
    whole tree should stay vectorised so N = 5000 is still fast.
    """
    j = np.arange(N + 1)           # number of up moves, 0 to N
    return S0 * u**j * d**(N - j)  # j ascending gives price ascending


def european_price(S0, K, T, r, sigma, N, kind="call", q=0.0):
    """Price a European option on an N-step CRR tree.

    The algorithm:
      1. dt = T / N, then u, d from crr_parameters and p from risk_neutral_prob.
      2. Compute the option payoff at every terminal node.
      3. Step BACKWARDS through the tree. At each node the value is the
         discounted risk-neutral expectation of its two children:

             value = exp(-r * dt) * (p * value_up + (1 - p) * value_down)

      4. After N backward steps you are left with one number: today's price.

    Vectorisation hint: hold the current level as a 1-D array `v` of length
    (steps + 1). One backward step turns length n+1 into length n, and is
    exactly `exp(-r*dt) * (p * v[1:] + (1-p) * v[:-1])`. Understand why the
    slices line up that way before you use it - v[1:] is the up-child and
    v[:-1] is the down-child of each node at the level below.
    """
    u, d, p, disc = _tree_setup(T, r, sigma, N, q)
    v = _payoff(terminal_prices(S0, u, d, N), K, kind)
    # Roll the whole level back one step at a time. v[1:] is the up-child of
    # each node below, v[:-1] the down-child, so this single line is the
    # discounted risk-neutral expectation applied to every node at once.
    for _ in range(N):
        v = disc * (p * v[1:] + (1.0 - p) * v[:-1])
    return float(v[0])


def american_price(S0, K, T, r, sigma, N, kind="put", q=0.0):
    """Price an American option on an N-step CRR tree.

    Identical to european_price except for ONE line in the backward loop. At
    every node you now compare:

        continuation value  = discounted expectation of the two children
        exercise value      = intrinsic value at that node's stock price

    and take the larger. That comparison is early exercise. It is why an
    American option cannot be worth less than its European twin, and why there
    is no closed form for the American put.

    You will need the stock price at each node during the backward pass, not
    just at expiry - so either recompute the level, or carry it alongside `v`.
    Recomputing is clearer; do that first and optimise later, if ever.

    Sanity check to hold in your head as you write it: for a non-dividend
    stock (q = 0), the American CALL price must come out exactly equal to the
    European call. Early exercise throws away time value and the insurance
    against the stock falling below K, so it is never optimal. If your code
    prices the American call higher, the bug is in the comparison, not in the
    theory. Hull ch 11.5 has the argument.
    """
    u, d, p, disc = _tree_setup(T, r, sigma, N, q)
    v = _payoff(terminal_prices(S0, u, d, N), K, kind)
    # Identical to the European loop plus one comparison: at every node take
    # the better of holding on (continuation) and exercising now (intrinsic).
    # That single max is what early exercise means, and it is why the American
    # price can never fall below the European one.
    for n in range(N - 1, -1, -1):
        continuation = disc * (p * v[1:] + (1.0 - p) * v[:-1])
        intrinsic = _payoff(terminal_prices(S0, u, d, n), K, kind)
        v = np.maximum(continuation, intrinsic)
    return float(v[0])
