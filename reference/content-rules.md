# Content Rules — What Goes On a Crew Doc (and What Never Does)

The lint (`scripts/wo_lint.py`) enforces the hard ones deterministically.
The rest are judgment calls this page makes explicit.

## Hard rules (lint FAILs)

1. **No prices.** Work orders are crew-facing; pricing lives in the estimate
   and the customer proposal. A dollar amount on a crew doc leaks margin to
   the job site. The generator scrubs them; the lint catches survivors.
2. **No unresolved placeholders.** TBD, TODO, {braces}, XXX — a crew acts on
   what the doc says. If a fact is unknown, the doc isn't ready; go get the
   fact. (Intentional fill-in blanks — `__________` for install date, crew
   lead, recorded readings — are fine and expected.)
3. **No AI attribution.** Docs are credited to the person who owns the work.

## Judgment rules (lint flags for REVIEW)

4. **State what IS happening.** Never present options to a crew ("could use
   tandem breakers OR decommission the circuit"). Decisions are made before
   dispatch; the doc records the decision.
5. **Positive instructions.** Write the action to take, not the mistake to
   avoid: "keep insulation 3 inches clear of the flue" beats "don't insulate
   over the flue." A first-week tech follows dos faster than don'ts.
6. **One ventilation standard.** Set your net-free-area ratio in the config
   (this package defaults to 1:300 — verify your local code) and the lint
   flags any doc that drifts from it.

## Working rules (on you, not the lint)

7. **Never assume.** Missing scope info means ASK the person who knows —
   not "probably." A wrong guess on a work order wastes a crew-day on-site.
8. **Specs come from the source of truth.** Pull square footages, R-values,
   and equipment sizing from your model/estimate system of record; never
   recalculate by hand on the doc. Two sources of the same number WILL drift.
9. **Write for the newest tech on the crew.** Real product names, plain
   language, day plan and contact number up front. If the greenest hire can
   run the day from the doc, everyone can.
10. **No scope invention.** Nothing appears on a work order that isn't in the
    sold scope — no "while we're there" items, no maintenance-plan sections,
    no equipment removal that wasn't agreed.

## Why a lint at all

Every rule above got its wording from a doc that failed it in the field.
A deterministic pass is the only reviewer that never gets tired: run it on
every generated doc (the generator does this automatically), fix FAILs before
anything ships, and read REVIEW items with human eyes.
