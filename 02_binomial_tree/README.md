# Binomial option pricer

European and American options priced on a Cox Ross Rubinstein tree, written from
the risk neutral derivation. 17 tests, no dependency beyond NumPy.

![Tree price converging to the Black-Scholes value](convergence.png)

The tree walks into the Black-Scholes value as the step count grows. The zigzag is
real: with the spot sitting exactly on the strike, the terminal nodes straddle K
differently depending on whether N is odd or even, so the price alternates above and
below the limit while the amplitude decays. That is a property of where the nodes land,
not a bug.

## The finance

Price a one step option by building a portfolio that cannot surprise you. Short one
call and buy delta shares, choosing delta so the portfolio is worth the same amount
whether the stock goes up or down. Its value at the end is then known today, so it has
to earn exactly the risk free rate. Not more, because that would be free money, and
not less, because nobody would hold it. Discount that known value back at r, take off
the shares, and what is left is the price of the call. Riskless here means the payoff
is certain, not that the position cannot lose.

Rearranging that argument gives the shortcut this code actually uses:

```
c = e^(-r*dt) * (p*Cu + (1-p)*Cd)     with  p = (e^((r-q)*dt) - d) / (u - d)
```

p is not the real probability of an up move and it is not a forecast. It is the number
that makes the stock grow at the risk free rate in expectation: solve
p*u + (1-p)*d = e^((r-q)*dt) for p and you get the formula above. That is the concrete
reason the stock's real world drift never appears in the answer. It is never used. Two
traders who disagree completely about where the stock is going still agree on this
price, because the hedge removes the thing they disagree about.

u and d come from matching variance. CRR sets u = exp(sigma*sqrt(dt)) so that the log
returns on the tree have the same variance over one step, sigma^2 * dt, as the
continuous model being approximated. Setting d = 1/u keeps the grid of log prices
centred on log(S0).

American exercise adds one right: stop at any node instead of waiting for expiry. So
at every node you take the better of holding on and cashing in, and the entire change
to the algorithm is

```
value = max(continuation, intrinsic)
```

It is only one comparison because backward induction already computes the continuation
value at every node. That is what pricing the European consists of. The part that
looks hard, that today's decision depends on future decisions, costs nothing here,
because you always arrive at a node already knowing what its two children are worth.
That is also why a tree prices an American option and the Black Scholes formula
cannot: the formula assumes exercise only at T.

For a call on a non dividend paying stock the comparison never fires. The European
call already satisfies c >= S0 - K*e^(-r*T), and since e^(-r*T) < 1 that lower bound
sits strictly above the intrinsic value S0 - K. The option is always worth more alive
than exercised, so the American call equals the European call. Exercising early would
pay K sooner than necessary and throw away the protection if the stock later falls
below K. Puts are the mirror image: exercising hands you K now and you earn interest
on it, so early exercise can pay, and the American put is strictly more expensive than
the European one. Dividends flip the call back, which is why q is a parameter.

## The implementation

The tree recombines, and that is the only reason any of this is tractable. An up move
followed by a down move and a down followed by an up both land on S0*u*d, so the nodes
collapse onto a lattice: N+1 prices at expiry instead of 2^N. At N = 5000 that is 5001
numbers rather than 2^5000, which is the difference between instant and impossible.
This comes from u and d being multiplicative, not from the CRR choice d = 1/u. What
d = 1/u adds is that up then down returns exactly to S0, which centres the grid.

One backward step is a single line over an entire level of the tree:

```
v = disc * (p * v[1:] + (1 - p) * v[:-1])
```

v holds the option values at one level, lowest node first. v[1:] drops the bottom
entry, which lines it up as the up child of each node one level down. v[:-1] drops the
top entry and lines up as the down child. The result is one element shorter, which is
exactly the next level in. The loop runs N times with no per node Python work. The
American version is the same line followed by np.maximum against the intrinsic value
at that level.

Inputs that imply an arbitrage raise instead of returning a price. p has to land
strictly inside (0, 1). If it does not, the riskless growth factor exp((r-q)*dt) sits
outside the range [d, u] that the stock can reach in one step, so one side of the
trade is free money and the inputs describe a market that cannot exist. Returning a
number there would be worse than raising, because the number looks reasonable and
prices without complaining. A wrong price that does not announce itself is harder to
catch than a crash.

## What is implemented

| Function | What it does |
|---|---|
| `crr_parameters(sigma, dt)` | The CRR choice of `u = exp(sigma sqrt(dt))` and `d = 1/u` |
| `risk_neutral_prob(r, q, dt, u, d)` | `p = (exp((r-q)dt) - d) / (u - d)`, raising if it falls outside `(0, 1)` |
| `terminal_prices(S0, u, d, N)` | The `N+1` prices at expiry, lowest first |
| `european_price(...)` | Backward induction, one vectorised line per level |
| `american_price(...)` | The same, plus `max(continuation, intrinsic)` at every node |
| `black_scholes.call_price(...)` | Closed form, only as the reference the tree converges to |

## Validation

Every check below is a property the model has to satisfy, not a stored number.
Reproduce them with `python -m pytest` and `python plot_convergence.py`.

| Check | Expected | Got |
|---|---|---|
| Put call parity, `K = 95`, `N = 2000` | `c - p = S0 - K exp(-rT)` | `9.6332046724` against `9.6332046724` |
| One step call by hand, `u = 1.25`, `d = 0.8`, `r = 0` | `(4/9) x 25 = 11.1111` | matches |
| Convergence, `N = 200` | Black-Scholes `10.450584` | `10.440591`, error `1.0e-02` |
| Convergence, `N = 5000` | Black-Scholes `10.450584` | `10.450184`, error `4.0e-04` |
| American call, `q = 0` | Exactly equal to the European call | equal to `1e-8` |
| American put, `S0 = 90`, `K = 100` | Strictly above the European put | `11.4928` against `10.2143` |
| Deep in the money American put, `S0 = 1` | Worth its intrinsic `K - S = 99` | `99.000000` |
| Arbitrage inputs | `ValueError`, not a price | raises |

The error roughly halves each time N doubles, which is the `O(1/N)` convergence CRR is
supposed to give. Put call parity holding to ten decimal places is the check worth
pointing at: it is not something you can fit, it either holds or the tree is wrong.

## Usage

```bash
pip install -r ../requirements.txt
python -m pytest
python plot_convergence.py     # writes convergence.png
```

## The interview question this answers

"Walk me through how you would price an American option." And the follow up most
candidates fumble: "Why is early exercise never optimal for an American call on a non
dividend paying stock?"

The short answer: exercising early throws away the remaining time value and the
protection of not having paid K yet. You would be giving up an asset worth more than
its intrinsic value. `test_american_call_equals_european_without_dividends` asserts
exactly this, and `test_dividends_make_early_exercise_worth_something` shows the
statement breaking once a large enough dividend yield gives you a reason to want the
stock itself.

## What I would do next

- Discrete cash dividends instead of a continuous yield, which is what real single
  stocks actually pay.
- A trinomial tree, and a comparison of convergence against this one for the same work.
- Use the tree to back out implied volatility for American options, which the closed
  form cannot do because there is no closed form to invert.

Built alongside Hull, *Options, Futures and Other Derivatives*, 11th edition,
chapter 13, with chapter 11 behind the put call parity test.
