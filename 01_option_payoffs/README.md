# Option payoffs and strategy diagrams

Payoff and profit functions for the basic option positions and two classic strategies,
written from the definitions with NumPy and matplotlib.

![Option payoff and strategy diagrams](payoff_diagrams.png)

## The model

<!-- Georges: write this section yourself before the repo goes public. Three to six
     sentences, your words. An interviewer will ask about whatever it says.

     Cover:
       - the difference between the payoff at expiry and the profit, and why the
         premium shifts the line down but does not change its shape
       - why a long call payoff is max(S - K, 0) and a forward is S - K with no floor,
         and what that difference means for the risk you are carrying
       - what a long straddle is a bet on, stated in terms of volatility rather than
         direction
       - why the bull call spread is capped on both sides, and what you gave up to
         reduce the premium

     Delete this comment when you have written it. -->

## What is implemented

| Function | What it returns |
|---|---|
| `call_payoff(S, K)` | Payoff at expiry of a long call, `max(S - K, 0)` |
| `put_payoff(S, K)` | Payoff at expiry of a long put, `max(K - S, 0)` |
| `forward_payoff(S, K)` | `S - K`, not floored at zero, because a forward obligates |
| `long_pnl(payoff, premium)` | Profit to the buyer, payoff less the premium paid |
| `short_pnl(payoff, premium)` | Profit to the seller, the exact mirror |
| `straddle_pnl(S, K, c, p)` | Long call plus long put at the same strike |
| `bull_call_spread_pnl(...)` | Long the low strike, short the high strike |

Every function is written against a NumPy array of spot prices, so the same code that
prices one point draws the whole diagram.

## Validation

Six tests, all of which check a property the payoff has to satisfy rather than a stored
number.

| Test | What it pins down |
|---|---|
| `test_call_payoff_itm_atm_otm` | The kink is at the strike, and the payoff is zero below it |
| `test_put_payoff_mirror_of_call` | Put and call payoffs are reflections about the strike |
| `test_long_and_short_are_zero_sum` | Buyer profit plus seller profit is exactly zero at every spot |
| `test_long_call_breakeven` | Profit crosses zero at strike plus premium, not at the strike |
| `test_straddle_worst_case_is_at_the_strike` | The straddle loses most when nothing happens |
| `test_bull_call_spread_caps_both_ways` | Both the maximum gain and the maximum loss are bounded |

The zero sum test is the one worth pointing at. It holds for every spot price on the
grid, which means the long and short sides cannot drift apart through a sign error.

## Usage

```bash
pip install -r ../requirements.txt
python -m pytest
python plot_strategies.py     # writes payoff_diagrams.png
```

## What I would do next

- Add the remaining spreads from Hull chapter 12: bear spreads, butterflies, calendars.
- Overlay the payoff at expiry with the value of the position before expiry, which is
  where the option premium and time value actually show up.
- Take real option chain prices for a single underlying and draw the strategy diagrams
  from live premiums instead of made up ones.

Built alongside Hull, *Options, Futures and Other Derivatives*, 11th edition,
chapters 10 and 12.
