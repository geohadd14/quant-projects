"""Draw the convergence plot: tree price against number of steps.

    python plot_convergence.py    -> writes convergence.png

Left panel is the headline: the CRR tree price walking into the Black-Scholes
value as N grows. Right panel is the same data on a log scale of the absolute
error, which is where the interesting structure shows up.

The zigzag in the left panel is real, not noise. With S0 = K the terminal nodes
straddle the strike differently depending on whether N is odd or even, so the
price alternates above and below the limit while the amplitude decays. Averaging
consecutive N is the standard trick for killing it, and it is worth knowing that
the oscillation is a property of where the nodes land rather than a bug.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from binomial import european_price
from black_scholes import call_price

S0, K, T, r, SIGMA = 100.0, 100.0, 1.0, 0.05, 0.20

bs = call_price(S0, K, T, r, SIGMA)
steps = np.arange(1, 201)
prices = np.array([european_price(S0, K, T, r, SIGMA, int(n), "call") for n in steps])
errors = np.abs(prices - bs)

fig, (left, right) = plt.subplots(1, 2, figsize=(13, 5))

left.plot(steps, prices, linewidth=1.0, label="CRR binomial tree")
left.axhline(bs, color="black", linestyle="--", linewidth=1.2,
             label=f"Black-Scholes = {bs:.4f}")
left.set_xlabel("steps in the tree (N)")
left.set_ylabel("call price")
left.set_title(f"Convergence: S0={S0:.0f} K={K:.0f} T={T:.0f}y "
               f"r={r:.0%} sigma={SIGMA:.0%}")
left.legend()
left.grid(alpha=0.25)

right.semilogy(steps, errors, linewidth=1.0)
right.set_xlabel("steps in the tree (N)")
right.set_ylabel("absolute error vs Black-Scholes")
right.set_title("Error decay, log scale")
right.grid(alpha=0.25, which="both")

fig.tight_layout()
fig.savefig("convergence.png", dpi=150)
print(f"wrote convergence.png")
print(f"  Black-Scholes      {bs:.6f}")
for n in (10, 50, 200, 1000, 5000):
    tree = european_price(S0, K, T, r, SIGMA, n, "call")
    print(f"  tree N={n:<6} {tree:.6f}   error {abs(tree - bs):.2e}")
