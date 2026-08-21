# Binomial option pricer

European and American options priced on a Cox Ross Rubinstein tree.

> **Status: in progress.** The test suite is written and defines the specification.
> Seventeen tests, currently failing against a skeleton. The implementation goes in
> `binomial.py`.

## Build order

Work down this list. Each step turns on a group of tests.

1. **One step tree on paper first, no code.** Derive the risk neutral probability by
   hand. Do not skip this: the whole model is this one step repeated.
2. `crr_parameters(sigma, dt)` gives the Cox Ross Rubinstein choice of `u` and `d`.
   Turns on `test_crr_up_and_down_are_reciprocal`, `test_crr_known_value`,
   `test_higher_vol_gives_a_wider_tree`.
3. `risk_neutral_prob(r, q, dt, u, d)`. Turns on the two probability tests plus
   `test_arbitrage_inputs_are_rejected`, which is the one that checks bad inputs raise
   instead of quietly returning a plausible wrong price.
4. `terminal_prices(S0, u, d, N)`. Turns on the two recombination tests.
5. `european_price(...)`, by backward induction. Turns on the hand computed one step
   call, put call parity, convergence to Black-Scholes, and the two monotonicity tests.
6. `american_price(...)`. The only change is one comparison at each node. Understand
   why before writing it. Turns on the last four tests.

## The finance

<!-- TODO, in your own words, three to six sentences:
     - what risk neutral valuation is, and why the real world drift of the stock
       does not appear anywhere in the price
     - where u, d and p come from, and what is being matched
     - what changes for American exercise, and why it is only one comparison -->

## The implementation

<!-- TODO, the choices worth defending:
     - why d = 1/u makes the tree recombine, and why that matters:
       N+1 terminal nodes instead of 2^N
     - how the backward induction is done
     - why an arbitrage violating input raises rather than returning a number -->

## Validation

<!-- TODO, fill the Got column once it runs. A table beats prose here. -->

| Check | Expected | Got |
|---|---|---|
| Put call parity, K = 95 | `c - p = S0 - K exp(-rT)` | |
| Convergence, N = 2000 | Black-Scholes 10.4506 | |
| American call, q = 0 | Equals the European call | |
| American put | Strictly above the European put | |
| Deep in the money American put | Worth its intrinsic value | |

The convergence plot is the demo image for this project. Price against number of steps,
with the Black-Scholes value as a horizontal line. That single picture is the pitch, so
it goes at the top of the README once it exists.

## The interview question this answers

"Walk me through how you would price an American option." And the follow up that most
candidates fumble: "Why is early exercise never optimal for an American call on a non
dividend paying stock?" Know the answer before the code is finished, because
`test_american_call_equals_european_without_dividends` is asserting exactly that, and if
the code disagrees the code is wrong.

## Usage

```bash
pip install -r ../requirements.txt
python -m pytest
```

Read alongside Hull, *Options, Futures and Other Derivatives*, 11th edition, chapter 13,
section by section while building. Chapter 11 first if put call parity is not solid yet,
since it becomes one of the tests.
