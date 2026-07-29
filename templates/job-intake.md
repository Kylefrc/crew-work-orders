# Job — {Customer Full Name}

Copy this file to `jobs/{job-name}/job.md` and fill every line. The generator
reads this one file. Rules while filling it in: state what IS happening (no
options, no "or"), no prices anywhere, and if a fact is unknown, go ask —
a blank guessed at here becomes wasted crew time on-site.

## Job Info

- Customer: {Full Name}
- Address: {Street, City, ST ZIP}
- Phone: {customer phone}
- Job Number: {your job / project #}
- Install Dates: {e.g. Aug 4–6, then QC day}

## Site Access & Safety

- Access: {entry door, gate code, parking, key location}
- Occupants: {who is home during work; pets}
- Safety flags: {e.g. LEAD PAINT — pre-1978, follow RRP; or "none"}

## The House

- {year built, stories, foundation type, square footage}
- {existing heat / hot water / ventilation}
- {anything the crew should know about the structure}

## Homeowner Concerns

- {what the customer said they care about — comfort, noise, a cold room}
- {explicit expectations: "X is NOT in this scope (homeowner aware)"}

## Scope of Work

Trade routes each row to the right crew doc: `hvac`, `wx` (weatherization),
or `elec`. Ventilation ductwork (range hood, bath fan) is hvac — they run the
ducts; wx seals around them after.

| Trade | Task | Details | Location |
|---|---|---|---|
| hvac | {task} | {specs, model, sizes — no prices} | {where in the home} |
| wx | {task} | {sqft, R-values, materials} | {where} |
| elec | {task} | {amperage, breaker, run} | {where} |

## Day Plan

Work items separated by " · ". Sequencing rules live in
reference/day-phasing.md — phase the job there first, then record it here.

Give each day a headline in the Day cell — it becomes that day's checklist
heading. Prefix items with the crew ("HVAC: …", "WX: …") and they render
with the crew name bolded.

| Day | Crews | Work |
|---|---|---|
| Day 1 (Mon) — {HEADLINE} | {crews on site} | {HVAC: item · WX: item · item} |
| Day 2 (Tue) — {HEADLINE} | {crews} | {HVAC: item · WX: item} |
| QC Day — {HEADLINE} | {assessor/lead} | {final test · walkthrough · sign-off} |

- {booking rule — why the order is locked, e.g. "attic opens Day 1 so ducts run Day 2 before the blow"}
- {booking rule}

## Equipment Arriving

| Item | Model | Qty |
|---|---|---|
| {equipment} | {model number} | {qty} |

## Checklists

Leave this section EMPTY to auto-select quality checklists from the scope
(recommended). To pin them manually, list keys, one per bullet — see
checklists/ for what exists (e.g. `hvac_ductless`, `attic`, `bath_fan`).

## Notes for Crew

- {site-specific note worth reading before knocking on the door}

## Homeowner Walkthrough

- {what the crew lead shows the homeowner at the end — thermostat, filters, vents}
