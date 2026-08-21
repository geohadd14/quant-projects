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

<!-- Georges: write this yourself before the repo goes public. Three to six sentences.
     An interviewer will ask about whatever it says.

     Cover:
       - what risk neutral valuation is, and why the stock's real world drift does
         not appear anywhere in the answer
       - where u, d and p come from, and what is being matched
       - what changes for American exercise, and why it is only one comparison

     The derivations are in the docstrings of binomial.py. Read those first. -->

## The implementation

<!-- Georges: the choices worth defending.

     - why d = 1/u makes the tree recombine: N+1 terminal nodes instead of 2^N,
       which is the difference between N = 5000 running instantly and never finishing
     - how one backward step is a single vectorised line over the whole level
     - why an arbitrage violating input raises instead of returning a number -->

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
