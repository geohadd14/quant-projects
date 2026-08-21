"""Option payoff & P&L functions.

Conventions (used across all projects in this repo):
- S: numpy array of possible underlying prices at expiry (or a float)
- K: strike price
- premium: what was paid (long) or received (short) for the option
- "payoff" = value of the position at expiry, ignoring the premium
- "pnl"    = payoff minus what you paid (long) / premium minus payoff (short)

Hull 11th ed, ch 10 (mechanics) and ch 12 (strategies).
Every function below should work when S is a numpy array - use np.maximum,
not Python's max(), so it applies element-wise.
"""

import numpy as np


def call_payoff(S, K):
    """Payoff at expiry of a LONG call: right to BUY at K.

    Worth something only when S > K. Hull eq. (10.1): max(S - K, 0).
    """
    return np.maximum(S - K, 0)

def put_payoff(S, K):
    """Payoff at expiry of a LONG put: right to SELL at K."""
    return np.maximum(K - S, 0)

def long_pnl(payoff, premium):
    """P&L of a long position: you PAID the premium."""
    return payoff - premium

def short_pnl(payoff, premium):
    """P&L of a short position: you RECEIVED the premium.

    Sanity check before coding: for every S, long_pnl + short_pnl must equal 0
    (options are a zero-sum contract between the two parties).
    """
    return premium - payoff

def straddle_pnl(S, K, call_premium, put_premium):
    """LONG straddle: buy a call AND a put, same K, same expiry.

    The classic 'I think it will move big but I don't know which way' trade.
    Build it by REUSING the functions above - no re-deriving maxes here.
    """
    return long_pnl(call_payoff(S, K), call_premium) + long_pnl(put_payoff(S, K), put_premium)

def bull_call_spread_pnl(S, K_low, K_high, premium_low, premium_high):
    """Bull call spread: buy call at K_low, sell call at K_high (K_low < K_high).

    Bullish, but capped upside in exchange for a cheaper entry.
    premium_low is what you pay for the K_low call; premium_high is what you
    receive for the K_high call.
    """
    return long_pnl(call_payoff(S, K_low), premium_low) + short_pnl(call_payoff(S, K_high), premium_high)

def forward_payoff(S, K):
    """Payoff at expiry of a LONG forward with delivery price K.

    NOT floored at zero - a forward OBLIGATES you to buy at K.
    If S < K you buy something worth S for K and you eat the difference.
    That asymmetry vs. call_payoff is the entire point.
    """
    return S - K

