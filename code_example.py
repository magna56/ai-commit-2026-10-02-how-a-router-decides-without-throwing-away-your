"""
Price the two ways to meet a harder turn: raise the effort, or switch the model.

The article's claim is that switching is the expensive option and most routers
only have that one. This prices both against the same requirement, at several
conversation depths, so you can see where the crossover actually sits with your
own numbers rather than taking the claim on faith.

Prices are representative, not quoted -- cached input at roughly a tenth of
fresh input is the ratio the whole argument rests on. Put your provider's real
figures in RATES. Stdlib only.
"""

# $ per million tokens.
RATES = {
    "small":    {"in": 0.30, "cached": 0.03, "out": 1.20, "skill": 0.55},
    "mid":      {"in": 1.80, "cached": 0.18, "out": 7.00, "skill": 0.78},
    "frontier": {"in": 6.00, "cached": 0.60, "out": 24.0, "skill": 0.92},
}

# Raising effort keeps the model, so it keeps the cache. It buys capability by
# spending output tokens -- more thinking before the answer.
EFFORT = {"low": (1.0, 0.00), "high": (3.4, 0.09)}

TOKENS_PER_TURN = 700
OUT_PER_TURN = 350


def effort_cost(model):
    """Extra spend to think harder on the model you already have."""
    extra = OUT_PER_TURN * (EFFORT["high"][0] - EFFORT["low"][0])
    return extra * RATES[model]["out"] / 1e6


def switch_cost(frm, to, turn):
    """What moving costs: the whole conversation re-read as fresh input.

    The cache you had with `frm` does not transfer. `to` reads every prior
    turn at its full input rate, and that history grows every turn.
    """
    history = turn * TOKENS_PER_TURN
    return history * RATES[to]["in"] / 1e6


def reach(model, effort):
    return RATES[model]["skill"] + EFFORT[effort][1]


def main():
    print("Two ways to meet a turn your current model cannot handle.\n")
    print("Current model: small (reach 0.55 low, 0.64 high)\n")
    print(f"  {'at turn':>8} {'raise effort':>14} {'switch to mid':>15} "
          f"{'switch to frontier':>20}")
    print("  " + "-" * 60)
    for turn in (5, 10, 20, 40, 60, 100):
        e = effort_cost("small")
        m = switch_cost("small", "mid", turn)
        f = switch_cost("small", "frontier", turn)
        print(f"  {turn:>8} ${e:>13.4f} ${m:>14.4f} ${f:>19.4f}")

    print("\n  Raising effort costs the same whenever you do it. Switching does not —")
    print("  it is priced on a conversation that keeps growing.\n")

    # The part that decides it: effort only reaches so far.
    print("But effort has a ceiling. What each option can actually reach:\n")
    print(f"  {'option':<28} {'reach':>7}  {'cache':>9}")
    print("  " + "-" * 48)
    for label, model, eff, keeps in (
        ("small, low effort", "small", "low", True),
        ("small, high effort", "small", "high", True),
        ("mid, low effort", "mid", "low", False),
        ("mid, high effort", "mid", "high", False),
        ("frontier, high effort", "frontier", "high", False),
    ):
        print(f"  {label:<28} {reach(model, eff):>7.2f}  "
              f"{'kept' if keeps else 'discarded':>9}")

    print("\n  So the rule is not 'prefer effort'. It is: if effort reaches the bar,")
    print("  take it, because it is cheap AND keeps the cache. If it does not reach,")
    print("  no amount of thinking substitutes for capability and you must pay.\n")

    # Where the two cross, for a task effort CAN reach.
    # A turn needing 0.60: mid at low effort reaches it, and so does small at
    # high effort. Both are valid, so price decides.
    print("For a turn needing 0.60 — reachable either way — the cheaper option is:\n")
    e = effort_cost("small")
    cross = next((t for t in range(1, 400) if switch_cost("small", "mid", t) > e), None)
    if cross is None or cross <= 1:
        print(f"  effort, at every conversation length. One turn of history already")
        print(f"  costs ${switch_cost('small', 'mid', 1):.4f} to re-read against ${e:.4f} to think harder,")
        print("  so with these rates the switch never wins on a task effort can reach.\n")
    else:
        print(f"  switching, up to turn {cross - 1}; effort from turn {cross} onward.\n")

    print("Run this with your own rates. Short conversations: switch freely, the")
    print("cache is worth little. Long ones: the cache is most of what you have")
    print("already paid for, and effort is how you avoid spending it again.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
