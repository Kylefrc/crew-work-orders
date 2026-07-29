# Work Order Document Format

What a crew-ready work order looks like. The generator enforces most of this;
this doc explains the target so you can extend it without breaking it.

## Format rules

- **File type: .docx.** Crews open these on phones and shop computers; Word
  format survives both. Never deliver markdown or plain text.
- **Branded, every time.** Color banner with logo (or wordmark), branded
  tables, company footer. An unbranded doc reads as a draft and gets ignored.
- **Photos are required.** A work order without site photos gets bounced by
  whoever runs your QC — and deserves it. 4–6 captioned photos minimum.
- **Contact up front.** The site-questions phone line renders directly under
  the job info block, before any scope. When a crew hits a surprise, the
  number they call is the first thing on page 1. Use the number crews
  actually reach — not the sales line.
- **Attribution is a person.** Footer = company · license # · "Prepared by:
  {name}". Software (including AI tooling) is never credited on a crew doc.

## The document family

| Doc | Audience | Contents |
|---|---|---|
| **MASTER** | Office / dispatch / crew leads | Everything: schedule, all trades, per-day checklists, walkthrough |
| **Per-trade** (HVAC / WEATHERIZATION / ELECTRICAL) | The crew doing that trade | That trade's scope + quality checklists + photos |
| **Punch / fix list** | Return-visit crew | Only the punch items for one return day, same format |

A water-heater-only job titles its mechanical doc **WATER HEATER WORK ORDER**.
A separate ELECTRICAL doc exists only when there is real electrician scope —
new circuits, panel work. A disconnect/reconnect of an existing circuit stays
a line on the install crew's doc; never spawn a doc nobody dispatches.

## Section order

1. **Banner** — logo/wordmark + doc type + "{Lastname} Residence — {City}, {ST}"
2. **Job info block** — customer, address, phone, **questions-on-site contact**, job #, install dates, crew lead (blank to fill on-site)
3. **Safety banner** (red, only when flags exist — lead paint, asbestos, knob & tube)
4. **Site Access & Homeowner Notes** (MASTER) — entry, codes, parking, occupants, pets
5. **The House** (MASTER) — year, size, foundation, existing systems, structural notes
6. **Homeowner Concerns** (MASTER) — what the customer cares about, incl. explicit "NOT in this scope (homeowner aware)" lines
7. **Trades Summary** (MASTER) — one row per trade, what they own on this job
8. **Schedule** (MASTER) — Day · Crews · Work table + booking-rule bullets
   (each rule a short story with the why) + "Book these dates" blanks with
   the day headlines (see day-phasing.md)
9. **Key Gates** (MASTER) — one sign-off line per day: the facts that must be
   true before the next phase starts, with a crew-lead/time blank; recorded
   numbers (blower door CFM50) get a fill-in inside the line
10. **This Trade in the Install Week** (per-trade) — which days this crew is
    on site, straight from the schedule
11. **Scope of Work** — table, no prices, specific specs and locations
12. **Equipment Arriving** — item, model number, qty
13. **Per-day checklists** (MASTER) — headline per day, crew-prefixed
    checkbox items, ending in a "DAY N DONE" gate + "photos sent to the office"
14. **Quality checklists** (per-trade) — from the checklists/ libraries,
    auto-selected from scope
15. **Notes for Crew** — trade-prefixed notes ("hvac: …") land only on that
    trade's doc; the MASTER keeps everything
16. **Homeowner Walkthrough** — what the lead shows the customer before leaving
17. **Reference Photos** — captioned grid; captions are instructions
    ("Land the ONE new circuit here"), never descriptions
18. **Completion Sign-Off** (MASTER) — crew lead, homeowner, final QC
19. **Footer** — company · license · prepared by

## File naming

`Work Order - {TYPE} - {Lastname} - {YYYY-MM-DD}.docx` — sortable, and a
crew lead can tell docs apart from a phone's file list.

## Delivering to Windows users

Export a PDF alongside the .docx when the recipient's setup is unknown.
On a Mac without Word, Pages exports .docx → PDF cleanly (File → Export To),
including embedded photo grids.
