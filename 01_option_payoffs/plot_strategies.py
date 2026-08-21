"""Plot payoff/P&L diagrams once payoffs.py passes its tests.

Plotting boilerplate only: every number on these charts comes from payoffs.py.
Run:  python plot_strategies.py   -> writes payoff_diagrams.png

How it works, since everything here gets reused in later projects:
- np.linspace builds the x-axis: a grid of possible expiry prices around the strike.
- Each subplot draws pnl vs S, a horizontal line at 0 (the breakeven axis), and
  shades profit region green / loss region red with fill_between.
"""

import matplotlib

matplotlib.use("Agg")  # write to file, no display window needed
import matplotlib.pyplot as plt
import numpy as np

from payoffs import (
    call_payoff,
    put_payoff,
    long_pnl,
    short_pnl,
    straddle_pnl,
    bull_call_spread_pnl,
)

K = 100.0
S = np.linspace(60, 140, 401)

panels = [
    ("Long call (K=100, prem=5)", long_pnl(call_payoff(S, K), 5.0)),
    ("Short call (K=100, prem=5)", short_pnl(call_payoff(S, K), 5.0)),
    ("Long put (K=100, prem=4)", long_pnl(put_payoff(S, K), 4.0)),
    ("Short put (K=100, prem=4)", short_pnl(put_payoff(S, K), 4.0)),
    ("Long straddle (K=100, prems 4+3)", straddle_pnl(S, K, 4.0, 3.0)),
    ("Bull call spread (100/110, 6-2)", bull_call_spread_pnl(S, K, 110.0, 6.0, 2.0)),
]

fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharex=True)
for ax, (title, pnl) in zip(axes.flat, panels):
    ax.plot(S, pnl, linewidth=2)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axvline(K, color="grey", linewidth=0.8, linestyle="--")
    ax.fill_between(S, pnl, 0, where=pnl > 0, alpha=0.15, color="green")
    ax.fill_between(S, pnl, 0, where=pnl < 0, alpha=0.15, color="red")
    ax.set_title(title, fontsize=10)
    ax.set_xlabel("S at expiry")
    ax.set_ylabel("P&L")

fig.suptitle("Option payoff diagrams - Hull ch 10 & 12", fontsize=13)
fig.tight_layout()
fig.savefig("payoff_diagrams.png", dpi=150)
print("wrote payoff_diagrams.png")
