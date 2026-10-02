# How a Router Decides Without Throwing Away Your Cache

**TL;DR:** A model switch costs you the cached conversation, so the better model can still be the worse decision. The fix is to treat the switch as the last option, after turning the reasoning dial on the model you already have.

Published from [The AI Commit](https://theaicommit.com/#2026-10-02/code) — AI in Production, 2026-10-02.

## Run

```bash
python3 code_example.py
```

## Output

```
Two ways to meet a turn your current model cannot handle.

Current model: small (reach 0.55 low, 0.64 high)

   at turn   raise effort   switch to mid   switch to frontier
  ------------------------------------------------------------
         5 $       0.0010 $        0.0063 $             0.0210
        10 $       0.0010 $        0.0126 $             0.0420
        20 $       0.0010 $        0.0252 $             0.0840
        40 $       0.0010 $        0.0504 $             0.1680
        60 $       0.0010 $        0.0756 $             0.2520
       100 $       0.0010 $        0.1260 $             0.4200

  Raising effort costs the same whenever you do it. Switching does not —
  it is priced on a conversation that keeps growing.

But effort has a ceiling. What each option can actually reach:

  option                         reach      cache
  ------------------------------------------------
  small, low effort               0.55       kept
  small, high effort              0.64       kept
  mid, low effort                 0.78  discarded
  mid, high effort                0.87  discarded
  frontier, high effort           1.01  discarded

  So the rule is not 'prefer effort'. It is: if effort reaches the bar,
  take it, because it is cheap AND keeps the cache. If it does not reach,
  no amount of thinking substitutes for capability and you must pay.

For a turn needing 0.60 — reachable either way — the cheaper option is:

  effort, at every conversation length. One turn of history already
  costs $0.0013 to re-read against $0.0010 to think harder,
  so with these rates the switch never wins on a task effort can reach.

Run this with your own rates. Short conversations: switch freely, the
cache is worth little. Long ones: the cache is most of what you have
already paid for, and effort is how you avoid spending it again.

```

## Code

See [`code_example.py`](code_example.py).
