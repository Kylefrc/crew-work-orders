# Content Rules — What Goes On a Crew Doc (and How It Sounds)

The lint (`scripts/wo_lint.py`) enforces the hard ones deterministically.
The voice rules make the doc land with the person actually holding it.

## Hard rules (lint FAILs)

1. **No prices.** Work orders are crew-facing; pricing lives in the estimate
   and the customer proposal. A dollar amount on a crew doc leaks margin to
   the job site. The generator scrubs them; the lint catches survivors.
2. **No unresolved placeholders.** TBD, TODO, {braces}, XXX — a crew acts on
   what the doc says. If a fact is unknown, the doc isn't ready; go get the
   fact. (Intentional fill-in blanks — `__________` for install date, crew
   lead, recorded readings — are fine and expected.)
3. **No AI attribution.** Docs are credited to the person who owns the work.

## Voice — write like you're standing next to the crew

This is the difference between a doc that gets read and a doc that gets
skimmed. Every rule below comes from docs that worked in the field.

4. **Short sentences. One fact each.** "The belly opens first, on Day 1.
   The old ducts come apart from below. Demo waits until WX has the belly
   open." A first-week tech can follow that at 7am in a driveway. Semicolon
   chains and comma stacks get skimmed.
5. **Actors do things.** Name who acts: "WX opens the belly." "The electrician
   comes for one day." "The vendor hauls the old units." Never "the belly
   shall be opened."
6. **The why rides with the rule.** When an order is locked, say what breaks
   if it's ignored: "Install the 20A breaker exactly. 20A is both the
   smallest and the largest allowed. A bigger breaker fails inspection."
   A crew that knows the why doesn't improvise around the what.
7. **The homeowner is a person with a name.** "Kathy lives alone and uses a
   wheelchair. Keep every path clear. Make sure she can get to every part of
   her home." Care instructions are work instructions — nightly power/water/
   locked-up restores, comfort windows when heat is out, delivery times set
   with the person. Write them with the same weight as torque specs.
8. **STOP-and-call is an instruction, not a failure.** Every judgment call
   gets an escalation line with a named person: "If the room is short,
   STOP and call Kyle." "Call Kyle before changing the rest of the week."
   The config's questions-on-site contact is who they call.
9. **Caps are for risk words only.** ONE, NOT, STOP, DIFFERENT, READ FIRST —
   the words that prevent an irreversible mistake: "Remove ONE Daikin
   system." "Space #114 is a DIFFERENT job." A doc that shouts everywhere
   shouts nothing.
10. **Pre-empt the confusion.** If the paperwork could mislead, say so and
    give the field rule: "The assessment shows two Daikins with nearly the
    same serial. That is likely one unit written down twice. Count the
    systems on site." "Some makers name the door swing from outside, some
    from inside. Wrong-handed special-order doors cannot be returned —
    confirm the handing rule with the supplier."
11. **Positive instructions by default; negatives only for traps.** Routine
    steps are written as the action to take. "Do not / never" is reserved
    for irreversible mistakes, safety, and confusion traps — and each one
    earns its place. The lint flags every negative for a human look;
    the review question is "is this a trap, or lazy phrasing?"
12. **State what IS happening.** Never options ("could use tandem breakers
    OR decommission the circuit"). Decisions are made before dispatch; the
    doc records the decision.
13. **Translate the jargon in place.** "R-32 refrigerant (A2L, mildly
    flammable)." "MCA 19.6 / MOP 20A — 20A is the only legal breaker."
    Ground every number in what it means on-site.
14. **Photo captions are instructions.** "Eaton 200A panel. Land the ONE new
    20A/240V heat-pump circuit here." beats "Photo of electrical panel."
    Every photo earns its place by telling the crew what to do with what
    they're seeing.

## Working rules (on you, not the lint)

15. **Never assume.** Missing scope info means ASK the person who knows —
    not "probably." A wrong guess on a work order wastes a crew-day on-site.
16. **Specs come from the source of truth.** Pull square footages, R-values,
    and equipment sizing from your model/estimate system of record; never
    recalculate by hand on the doc. Two sources of the same number WILL drift.
17. **Write for the newest tech on the crew.** Real product names, plain
    language, day plan and contact number up front. If the greenest hire can
    run the day from the doc, everyone can.
18. **No scope invention.** Nothing appears on a work order that isn't in the
    sold scope — no "while we're there" items, no maintenance-plan sections,
    no equipment removal that wasn't agreed.

## Why a lint at all

Every rule above got its wording from a doc that failed it in the field.
A deterministic pass is the only reviewer that never gets tired: run it on
every generated doc (the generator does this automatically), fix FAILs before
anything ships, and read REVIEW items with human eyes.
