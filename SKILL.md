---
name: crew-work-orders
description: >
  Generate branded, crew-ready work orders (.docx) for residential trade and
  retrofit jobs — HVAC, weatherization/insulation, electrical. Turns a scope
  of work into a day-phased MASTER work order plus per-trade crew docs with
  quality checklists, photos, and a deterministic lint gate. Use when the user
  says "build a work order", "crew sheet", "install packet", "scope doc for
  the crew", "break this job into days", or wants to set this package up for
  their own company ("rebrand this", "add our checklists", "set up our
  config"). Works for any trades company — branding, license, contact, and
  checklist libraries all come from one config file.
---

# Crew Work Orders

Turn a sold scope into the documents a crew actually runs the day from:
one day-phased **MASTER** + per-trade docs (**HVAC / WEATHERIZATION /
ELECTRICAL**), branded, photo-backed, and linted before anything ships.

## The one rule above all others

**Never assume on a work order.** If scope, day plan, equipment, access, or
any fact is missing or ambiguous — ask the user. State what IS happening,
never options. A wrong guess wastes a crew-day on-site; a question costs a
minute. This rule outranks speed.

## The voice

Everything you write into a job file or work order uses the crew voice —
`reference/content-rules.md` §Voice has the full list. The short version:

- Short sentences. One fact each. "The belly opens first, on Day 1."
- Actors do things: "WX opens the attic." "The electrician comes for one day."
- The why rides with the rule: "A bigger breaker fails inspection."
- The homeowner is a person with a name; care instructions (paths clear,
  power back on nightly, comfort during no-heat windows) are work
  instructions.
- Every judgment call gets a STOP-and-call line naming the config's
  site contact.
- Caps only on the words that prevent an irreversible mistake: ONE, NOT,
  STOP, DIFFERENT.
- Pre-empt confusion: if paperwork could mislead ("two units with nearly the
  same serial"), give the field rule ("count the systems on site").
- Photo captions are instructions, not descriptions.

## Workflow: build a work order

1. **Collect the job.** Create `jobs/{job-name}/` and copy
   `templates/job-intake.md` to `jobs/{job-name}/job.md`. Fill it from what
   the user gives you; **interview for every blank you cannot fill from their
   materials** (customer, address, scope rows, day plan, equipment models,
   access, safety flags). Do not invent specs, and do not put prices anywhere.
2. **Route the trades.** Every scope row gets a Trade: `hvac`, `wx`, or
   `elec`. Ventilation ductwork (range hood, bath fans) is **hvac** — they
   run the ducts; wx seals around them after. A separate `elec` doc exists
   only for real electrician scope (new circuits, panel work) — a
   disconnect/reconnect stays on the install crew's rows.
3. **Phase the days.** Read `reference/day-phasing.md`. Match the job to an
   archetype; apply the sequencing invariants (open first → penetrations →
   air-seal → blower door → insulate LAST → separate QC day). If the job fits
   no archetype, ask the user how they want it phased — then offer to capture
   their answer as a new archetype in that file.
4. **Photos.** Put site photos in `jobs/{job-name}/photos/` and write
   `photos/captions.md` (`| file | caption | trades |`). Work orders ship
   with captioned photos — no photos is a warning you resolve, not ignore.
5. **Generate.**
   `python3 scripts/build_work_orders.py jobs/{job-name}/`
   (add `--config path/to/company.md` if the job isn't under a folder with
   one). Read the console: trade-routing notes, price scrubs, photo warnings.
6. **Lint gate.** The generator lints every output. **FAIL = fix the source
   and regenerate** — never hand-edit the .docx and never deliver a FAIL.
   REVIEW items get human eyes. Full detail:
   `python3 scripts/wo_lint.py "<output.docx>" --config <company.md>`.
7. **Deliver.** Point the user at `jobs/{job-name}/output/`. Offer a PDF
   export alongside the .docx when recipients may not have Word.

## Workflow: adopt for a company ("rebrand this")

1. Edit `config/company.md`: name, license line, prepared-by, the phone
   crews should call, two brand colors, ventilation ratio (confirm local
   code), and a logo path (or blank for the wordmark banner).
2. Drop their logo into `assets/` — white/light artwork on transparent
   renders best on the colored banner.
3. Regenerate the sample job against their config and show them the result:
   `python3 scripts/build_work_orders.py examples/resilient-retrofits/jobs/alder-st/ --config config/company.md`
4. Their program checklists: see below. Their archetypes: capture into
   `reference/day-phasing.md` as jobs teach them.

## Workflow: add a program/QA checklist library

Checklists are data, not code. One markdown file per checklist in a
directory listed in the config's `checklist_dirs` (comma-separated; later
directories override earlier ones by `key` — that's how a program overlay
replaces a generic checklist). File format:

```
# Title Shown On The Doc
key: snake_case_id
applies: hvac | wx | elec | all
auto: regex that selects it from scope text
qa: true            (prefixes the config's qa_label)
type: checklist     (or "record" for a Test/Value/Pass table)
order: 30           (render order)
always: false       (true = on every job)

- item one
- item two
```

See `examples/resilient-retrofits/checklists-pcef/` for a real program
overlay (PCEF/Energy Trust inspection items layered over the generic set).

## Hard rules (the lint enforces 1–3)

1. **No prices on crew docs** — pricing lives in the estimate.
2. **No unresolved placeholders** — blanks for on-site recording are fine;
   TBDs are not.
3. **No AI attribution** — docs are credited to a person.
4. **Positive instructions** — write the action to take, not the mistake to
   avoid.
5. **Photos required.** 4–6 captioned site photos minimum.

## Package map

| Path | What |
|---|---|
| `config/company.md` | The one file that rebrands everything |
| `templates/job-intake.md` | Per-job fill-in → becomes `jobs/{name}/job.md` |
| `scripts/build_work_orders.py` | job.md + config → branded .docx set |
| `scripts/wo_lint.py` | Deterministic hard-rule gate |
| `checklists/` | Generic QA libraries (data files) |
| `reference/` | Document format · day phasing · content rules |
| `examples/resilient-retrofits/` | Fully-worked real-company example |
| `tools/make_graphics.py` | Rebuilds every graphic in the package |
