#!/usr/bin/env python3
"""Crew work-order generator — branded .docx from one plain-markdown job file.

Reads a job folder containing job.md (see templates/job-intake.md) and renders:

    output/Work Order - MASTER - {Lastname} - {date}.docx     (always)
    output/Work Order - HVAC - {Lastname} - {date}.docx       (when in scope)
    output/Work Order - WEATHERIZATION - {Lastname} - {date}.docx
    output/Work Order - ELECTRICAL - {Lastname} - {date}.docx

Usage:
    python3 scripts/build_work_orders.py path/to/jobs/{job}/ [--config path/to/company.md]

Config resolution (first hit wins):
    1. --config PATH
    2. company.md found walking UP from the job folder (lets an example or a
       company workspace keep its own config next to its jobs)
    3. config/company.md at the package root

Content rules enforced here (see reference/content-rules.md for the why):
    - No prices on crew docs — dollar amounts are scrubbed with a printed note
    - Checklists come from data files (checklists/*.md) — add programs by
      dropping in a file, not by editing this script
    - Photos are required — the generator warns loudly when a job has none
    - Every output is linted by wo_lint.py (advisory: verdicts print, the
      build never silently blocks)
"""

import argparse
import glob
import os
import re
import subprocess
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx_helpers import add_body, add_checkbox, add_photo_grid, add_safety_banner, create_doc
from brand import Brand

PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TRADE_LABELS = {'hvac': 'HVAC', 'wx': 'WEATHERIZATION', 'elec': 'ELECTRICAL'}

TRADE_ALIASES = {
    'hvac': 'hvac', 'mechanical': 'hvac', 'mech': 'hvac', 'heating': 'hvac',
    'cooling': 'hvac', 'water heater': 'hvac', 'plumbing': 'hvac',
    'wx': 'wx', 'weatherization': 'wx', 'insulation': 'wx', 'envelope': 'wx',
    'air seal': 'wx', 'air sealing': 'wx',
    'elec': 'elec', 'electrical': 'elec', 'electrician': 'elec',
}

# Fallback routing when a scope row has no Trade value. The intake template
# asks for an explicit Trade column — these keywords are the safety net.
KEYWORD_ROUTES = [
    ('hvac', re.compile(r'heat pump|air handler|condenser|lineset|line set|thermostat|'
                        r'commission|refrigerant|water heater|hpwh|condensate|erv|'
                        r'range hood|hood vent|bath fan|exhaust fan|duct')),
    ('wx', re.compile(r'attic|wall|floor|crawl|belly|insul|air.?seal|blower|dense.?pack|'
                      r'weatherstrip|baffle|cellulose|hatch|skirting')),
    ('elec', re.compile(r'circuit|panel|breaker|wiring|disconnect|subpanel|service upgrade')),
]

_PRICE_RE = re.compile(r'\(?\$\s?[\d,]+(?:\.\d+)?\s?[kKmM]?'
                       r'(?:\s*(?:net|gross|/sf|/sqft|per sf))?\)?')

_WH_ONLY_RE = re.compile(r'hpwh|heat pump water heater|water heater')
_HP_RE = re.compile(r'ducted|ductless|mini.?split|air handler|wall head|heat pump(?! water)')


# ─── job.md parsing ─────────────────────────────────────────────────────────

def _sections(text):
    """Split markdown into {heading: body} keyed by lowercase ## heading."""
    parts = re.split(r'^##\s+', text, flags=re.M)
    out = {}
    for part in parts[1:]:
        lines = part.split('\n')
        out[lines[0].strip().lower()] = '\n'.join(lines[1:])
    return out


def _find_section(sections, *needles):
    for heading, body in sections.items():
        if all(n in heading for n in needles):
            return body
    return ''


def _bullets(body):
    return [line.strip()[2:].strip() for line in body.split('\n')
            if line.strip().startswith('- ')]


def _kv(body):
    """`- Key: value` bullets → dict with lowercase snake keys."""
    out = {}
    for b in _bullets(body):
        if ':' in b:
            key, value = b.split(':', 1)
            out[key.strip().lower().replace(' ', '_').replace('/', '_')] = value.strip()
    return out


def _table(body):
    """First markdown table in body → (headers, rows)."""
    rows = []
    for line in body.split('\n'):
        line = line.strip()
        if line.startswith('|') and '---' not in line:
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if any(cells):
                rows.append(cells)
    if not rows:
        return [], []
    return rows[0], rows[1:]


def normalize_trade(value, row_text):
    v = value.strip().lower()
    if v in TRADE_ALIASES:
        return TRADE_ALIASES[v]
    for trade, rx in KEYWORD_ROUTES:
        if rx.search(row_text.lower()):
            if v:
                print(f'  NOTE: unrecognized trade "{value}" — routed to {trade} by keywords')
            return trade
    return ''


def load_job(job_dir):
    job_path = os.path.join(job_dir, 'job.md')
    if not os.path.exists(job_path):
        raise FileNotFoundError(
            f'job.md not found in {job_dir} — copy templates/job-intake.md there and fill it in')
    with open(job_path, encoding='utf-8') as f:
        text = f.read()
    sections = _sections(text)

    info = _kv(_find_section(sections, 'job info'))
    access = _bullets(_find_section(sections, 'site access'))

    # Safety flags: the explicit list plus auto-detected red flags
    safety = []
    safety_line = next((a for a in access if a.lower().startswith('safety')), '')
    access = [a for a in access if not a.lower().startswith('safety')]
    if safety_line and 'none' not in safety_line.lower():
        safety += [s.strip() for s in safety_line.split(':', 1)[1].split(';') if s.strip()]
    blob = text.lower()
    if not safety_line:
        if re.search(r'pre.?1978|lead.?safe|lead paint', blob):
            safety.append('LEAD PAINT — follow lead-safe (RRP) practices')
        if 'asbestos' in blob:
            safety.append('ASBESTOS — follow local abatement rules')
        if re.search(r'knob\s*(&|and)\s*tube', blob):
            safety.append('KNOB & TUBE WIRING — keep insulation clear until verified')

    scope_headers, scope_raw = _table(_find_section(sections, 'scope'))
    scope_rows = []
    trade_idx = next((i for i, h in enumerate(scope_headers) if h.lower() == 'trade'), None)
    if trade_idx is None and scope_raw:
        print('  NOTE: Scope table has no Trade column — routing rows by keywords. '
              'Add a Trade column (see templates/job-intake.md) for exact control.')
    for row in scope_raw:
        row_text = ' '.join(row)
        raw_trade = row[trade_idx] if trade_idx is not None and trade_idx < len(row) else ''
        trade = normalize_trade(raw_trade, row_text)
        if not trade:
            print(f'  WARNING: could not route scope row to a trade (appears on MASTER only): '
                  f'{row_text[:60]}')
        cells = [c for i, c in enumerate(row) if i != trade_idx]
        scope_rows.append({'trade': trade, 'cells': cells})
    display_headers = ([h for i, h in enumerate(scope_headers) if i != trade_idx]
                       if scope_headers else [])

    day_section = _find_section(sections, 'day plan')
    day_headers, day_rows = _table(day_section)
    booking_rules = _bullets(day_section)

    equip_headers, equip_rows = _table(_find_section(sections, 'equipment'))

    house = _bullets(_find_section(sections, 'the house'))
    concerns = _bullets(_find_section(sections, 'homeowner concerns'))
    key_gates = _bullets(_find_section(sections, 'key gates'))

    checklist_override = [b.strip().lower().replace('-', '_') for b in
                          _bullets(_find_section(sections, 'checklists'))]

    notes = _bullets(_find_section(sections, 'notes'))
    walkthrough = _bullets(_find_section(sections, 'walkthrough'))

    # Checklist auto-selection scans only real job content (scope, day plan,
    # equipment) — never the template's own instructional prose.
    scope_text = ' '.join(
        [' '.join(r) for r in scope_raw]
        + [' '.join(r) for r in day_rows]
        + [' '.join(r) for r in equip_rows]).lower()

    return {
        'info': info, 'access': access, 'safety': safety,
        'scope_headers': display_headers, 'scope_rows': scope_rows,
        'day_headers': day_headers, 'day_rows': day_rows, 'booking_rules': booking_rules,
        'equip_headers': equip_headers, 'equip_rows': equip_rows,
        'house': house, 'concerns': concerns, 'key_gates': key_gates,
        'checklist_override': checklist_override,
        'notes': notes, 'walkthrough': walkthrough,
        'text': blob, 'scope_text': scope_text,
    }


# ─── Checklist libraries (data files, not code) ─────────────────────────────

def load_checklists(brand):
    """Parse every checklists/*.md across the config's checklist_dirs.
    Later directories override earlier ones by key (program overlays)."""
    libs = {}
    for d in brand.checklist_dirs():
        if not os.path.isdir(d):
            print(f'  WARNING: checklist dir not found: {d}')
            continue
        for path in sorted(glob.glob(os.path.join(d, '*.md'))):
            lib = _parse_checklist_file(path, brand)
            if lib:
                libs[lib['key']] = lib
    return libs


def _parse_checklist_file(path, brand):
    meta = {'title': '', 'key': '', 'applies': 'all', 'auto': '', 'qa': False,
            'type': 'checklist', 'order': 50, 'always': False}
    items = []
    vent = f"1:{brand.cfg['vent_ratio']}"
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip()
            if line.startswith('# '):
                meta['title'] = line[2:].strip()
            elif line.startswith('- '):
                items.append(line[2:].strip().replace('{vent_ratio}', vent))
            elif ':' in line and not items:
                key, value = line.split(':', 1)
                key, value = key.strip().lower(), value.strip()
                if key in ('qa', 'always'):
                    meta[key] = value.lower() == 'true'
                elif key == 'order':
                    meta[key] = int(value)
                elif key in meta:
                    meta[key] = value
    if not meta['key'] or not items:
        return None
    meta['items'] = items
    return meta


def select_checklists(libs, job):
    """always:true libs + auto-regex hits on the job text, unless the job's
    ## Checklists section lists keys explicitly (which replaces the auto set)."""
    selected = {k for k, lib in libs.items() if lib['always']}
    if job['checklist_override']:
        for key in job['checklist_override']:
            if key in libs:
                selected.add(key)
            else:
                print(f'  WARNING: job.md asks for unknown checklist "{key}" — '
                      f'available: {", ".join(sorted(libs))}')
    else:
        for key, lib in libs.items():
            if lib['auto'] and re.search(lib['auto'], job['scope_text']):
                selected.add(key)
    return selected


# ─── Photos ─────────────────────────────────────────────────────────────────

def load_photos(job_dir, trade):
    """(paths, captions) for a trade from photos/captions.md rows
    `| file | caption | trades |` (trades csv, blank = all; 'master' sees all)."""
    photo_dir = os.path.join(job_dir, 'photos')
    manifest = os.path.join(photo_dir, 'captions.md')
    paths, captions = [], []
    if os.path.exists(manifest):
        with open(manifest, encoding='utf-8') as f:
            for line in f.read().split('\n'):
                line = line.strip()
                if not line.startswith('|') or '---' in line:
                    continue
                cells = [c.strip() for c in line.split('|')[1:-1]]
                if len(cells) < 2 or cells[0].lower() in ('file', ''):
                    continue
                fname, caption = cells[0], cells[1]
                trades = ({t.strip().lower() for t in cells[2].split(',')}
                          if len(cells) > 2 and cells[2] else set(TRADE_LABELS))
                if trade != 'master' and trade not in trades:
                    continue
                p = os.path.join(photo_dir, fname)
                if os.path.exists(p):
                    paths.append(p)
                    captions.append(caption)
                else:
                    print(f'  WARNING: captions.md references missing photo: {fname}')
        return paths, captions
    imgs = sorted(glob.glob(os.path.join(photo_dir, '*.jp*g'))
                  + glob.glob(os.path.join(photo_dir, '*.png')))[:6]
    if imgs:
        print(f'  WARNING: no photos/captions.md — embedding first {len(imgs)} photos '
              'uncaptioned. Write captions.md for a crew-ready doc.')
    else:
        print('  WARNING: no site photos found — crew docs ship with a Reference Photos '
              'section. Add photos/ + captions.md before dispatching.')
    return imgs, ['' for _ in imgs]


# ─── Document builders ──────────────────────────────────────────────────────

def _scrub_prices(cell):
    return _PRICE_RE.sub('', cell).replace('  ', ' ').strip(' -–—·')


def _subtitle(info):
    last = (info.get('customer', '').split() or ['Job'])[-1]
    m = re.search(r',\s*([A-Za-z .]+),\s*([A-Z]{2})\b', info.get('address', ''))
    if m:
        return f'{last} Residence — {m.group(1).strip()}, {m.group(2)}'
    return f'{last} Residence'


def _col_widths(ncols):
    presets = {2: [2600, 6760], 3: [1900, 5700, 1760], 4: [700, 2300, 4600, 1760]}
    return presets.get(ncols, [9360 // ncols] * ncols)


def _doc_shell(brand, doc_type, job, install_value):
    doc = create_doc()
    brand.header(doc, doc_type, _subtitle(job['info']))
    info = job['info']
    rows = [
        ('Customer', info.get('customer', '')),
        ('Address', info.get('address', '')),
        ('Homeowner phone', info.get('phone', '')),
    ]
    if brand.cfg['crew_contact']:
        rows.append(('Questions on site', brand.cfg['crew_contact']))
    rows += [
        ('Job #', info.get('job_number', info.get('job', ''))),
        ('Install Dates', install_value),
        ('Crew Lead', '___________________________'),
    ]
    brand.two_col(doc, rows)
    add_safety_banner(doc, job['safety'])
    return doc


def _scope_table(brand, doc, job, trade=None):
    headers = job['scope_headers'] or ['Task', 'Details', 'Location']
    rows = [r for r in job['scope_rows'] if trade is None or r['trade'] == trade]
    brand.heading(doc, 'Scope of Work')
    if not rows:
        add_body(doc, 'See the master work order for scope.', italic=True)
        return
    scrubbed = 0
    norm = []
    for r in rows:
        cells = (r['cells'] + [''] * len(headers))[:len(headers)]
        clean = [_scrub_prices(c) for c in cells]
        scrubbed += sum(1 for a, b in zip(cells, clean) if a != b)
        if trade is None:
            clean = [TRADE_LABELS.get(r['trade'], '—')] + clean
        norm.append(clean)
    if scrubbed:
        print(f'  NOTE: scrubbed {scrubbed} price token(s) — crew docs carry no dollar amounts.')
    hdrs = (['Trade'] + headers) if trade is None else headers
    brand.table(doc, hdrs, norm, widths=_col_widths(len(hdrs)))


def _equipment_table(brand, doc, job):
    if job['equip_rows']:
        brand.heading(doc, 'Equipment Arriving')
        brand.table(doc, job['equip_headers'], job['equip_rows'],
                    widths=_col_widths(len(job['equip_headers'])))


_TRADE_DAY_TOKENS = {
    'hvac': ('hvac', 'mech'),
    'wx': ('wx', 'weatherization'),
    'elec': ('elec', 'electric'),
}


def _notes(brand, doc, job, trade=None):
    """Notes for the crew. A note prefixed "hvac:" / "wx:" / "elec:" renders
    only on that trade's doc (and the MASTER); unprefixed notes go everywhere."""
    picked = []
    for n in job['notes']:
        m = _CREW_PREFIX_RE.match(n)
        note_trade = TRADE_ALIASES.get(m.group(1).strip().lower()) if m else None
        if note_trade and trade is not None and note_trade != trade:
            continue
        strip = m and note_trade and trade is not None
        picked.append(m.group(2) if strip else n)
    if picked:
        brand.heading(doc, 'Notes for Crew')
        for n in picked:
            add_body(doc, '•  ' + n)


def _trade_week(brand, doc, job, trade):
    """"This Trade in the Install Week" — which days this crew is on site."""
    tokens = _TRADE_DAY_TOKENS[trade]
    days = [row[0] for row in job['day_rows']
            if any(t in ' '.join(row[:2]).lower() for t in tokens)
            or any(t + ':' in ' '.join(row[2:]).lower() for t in tokens)]
    if days:
        brand.heading(doc, 'This Trade in the Install Week')
        for d in days:
            add_body(doc, '•  ' + d)


def _photos(brand, doc, job_dir, trade):
    paths, captions = load_photos(job_dir, trade)
    if paths:
        brand.heading(doc, 'Reference Photos')
        add_photo_grid(doc, paths, captions)


def _render_checklist(brand, doc, lib):
    title = f"{brand.cfg['qa_label']} — {lib['title']}" if lib['qa'] else lib['title']
    if lib['type'] == 'record':
        brand.heading(doc, title)
        brand.table(doc, ['Test', 'Value', 'Pass?'],
                    [[t, '________', '☐'] for t in lib['items']],
                    widths=[5200, 2400, 1760])
    else:
        brand.checklist(doc, title, lib['items'])


_CREW_PREFIX_RE = re.compile(r'^([A-Za-z][A-Za-z /+&-]{1,18}):\s+(.*)$')


def _day_checkbox(doc, item):
    """Checkbox with the crew prefix bolded ("HVAC: set ODU" -> bold HVAC)."""
    m = _CREW_PREFIX_RE.match(item)
    para = add_checkbox(doc, '')
    run0 = para.runs[0]
    if m:
        run0.text = '☐  ' + m.group(1).upper() + ' — '
        run0.bold = True
        run1 = para.add_run(m.group(2))
        run1.font.size = run0.font.size
        run1.font.name = run0.font.name
    else:
        run0.text = '☐  ' + item
    return para


def build_master(brand, job, job_dir):
    doc = _doc_shell(brand, 'MASTER WORK ORDER', job,
                     job['info'].get('install_dates', '___________________________'))
    if job['access']:
        brand.heading(doc, 'Site Access & Homeowner Notes')
        for a in job['access']:
            add_body(doc, '•  ' + a)
    if job['house']:
        brand.heading(doc, 'The House')
        for h in job['house']:
            add_body(doc, '•  ' + h)
    if job['concerns']:
        brand.heading(doc, 'Homeowner Concerns (from walkthrough)')
        for c in job['concerns']:
            add_body(doc, '•  ' + c)

    trades_in_job = [t for t in ('hvac', 'wx', 'elec')
                     if any(r['trade'] == t for r in job['scope_rows'])]
    if trades_in_job:
        brand.heading(doc, 'Trades Summary')
        summary = []
        for t in trades_in_job:
            tasks = [r['cells'][0] for r in job['scope_rows']
                     if r['trade'] == t and r['cells']]
            summary.append([TRADE_LABELS[t], ' · '.join(tasks)])
        brand.table(doc, ['Trade', 'In this job'], summary, widths=[2200, 7160])

    if job['day_rows']:
        brand.heading(doc, 'Schedule')
        brand.table(doc, job['day_headers'], job['day_rows'],
                    widths=_col_widths(len(job['day_headers'])))
        for rule in job['booking_rules']:
            add_body(doc, '•  ' + rule)
        add_body(doc, 'Book these dates:', bold=True)
        for row in job['day_rows']:
            day = row[0]
            if '—' in day:
                head, tail = day.split('—', 1)
                day = f'{head.strip()} · {tail.strip()}'
            add_body(doc, f'   {day}:  _______________________')
        if job['key_gates']:
            brand.heading(doc, 'Key Gates — sign off before moving on')
            for g in job['key_gates']:
                add_checkbox(doc, f'{g}    ______  (crew lead / time)')
    else:
        print('  NOTE: no Day Plan in job.md — MASTER renders without a schedule. '
              'See reference/day-phasing.md to phase the job.')

    _scope_table(brand, doc, job, trade=None)
    _equipment_table(brand, doc, job)

    for row in job['day_rows']:
        label = ' — '.join(c for c in row[:2] if c)
        items = [i.strip() for i in re.split(r'\s+·\s+|;\s*', ' '.join(row[2:])) if i.strip()]
        if items:
            brand.heading(doc, label.upper())
            for item in items:
                _day_checkbox(doc, item)
            add_checkbox(doc, f'{row[0].upper()} DONE — site clean and safe, next phase ready')
            add_checkbox(doc, 'Photos of today\'s work sent to the office')

    _notes(brand, doc, job)
    if job['walkthrough']:
        brand.checklist(doc, 'Homeowner Walkthrough', job['walkthrough'])
    _photos(brand, doc, job_dir, 'master')

    brand.heading(doc, 'Completion Sign-Off')
    brand.two_col(doc, [
        ('Crew Lead', 'Signature: ______________________________    Date: ____________'),
        ('Homeowner', 'Signature: ______________________________    Date: ____________'),
        ('Final QC by', 'Name: ____________________  Blower door / results attached  ☐'),
    ])
    brand.footer(doc)
    return doc


def build_trade(brand, job, job_dir, trade, libs, selected):
    label = TRADE_LABELS[trade]
    if trade == 'hvac':
        hvac_text = ' '.join(' '.join(r['cells']) for r in job['scope_rows']
                             if r['trade'] == 'hvac').lower()
        if _WH_ONLY_RE.search(hvac_text) and not _HP_RE.search(hvac_text):
            label = 'WATER HEATER'
    doc = _doc_shell(brand, f'{label} WORK ORDER', job, '___________________________')
    _trade_week(brand, doc, job, trade)
    _scope_table(brand, doc, job, trade=trade)
    _equipment_table(brand, doc, job)
    for key in sorted(selected, key=lambda k: (libs[k]['order'], k)):
        lib = libs[key]
        if lib['applies'] in (trade, 'all'):
            _render_checklist(brand, doc, lib)
    _notes(brand, doc, job, trade=trade)
    _photos(brand, doc, job_dir, trade)
    brand.footer(doc)
    return doc, label


# ─── Config resolution + main ───────────────────────────────────────────────

def find_config(job_dir, explicit):
    if explicit:
        return os.path.abspath(explicit)
    d = os.path.abspath(job_dir)
    while True:
        candidate = os.path.join(d, 'company.md')
        if os.path.exists(candidate):
            return candidate
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return os.path.join(PACKAGE_ROOT, 'config', 'company.md')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('job_dir', help='job folder containing job.md (+ photos/)')
    ap.add_argument('--config', help='company config (default: nearest company.md, '
                                     'else config/company.md)')
    args = ap.parse_args()

    job_dir = os.path.abspath(args.job_dir)
    config_path = find_config(job_dir, args.config)
    print(f'Config: {config_path}')
    brand = Brand.load(config_path)
    job = load_job(job_dir)
    libs = load_checklists(brand)
    selected = select_checklists(libs, job)

    lastname = (job['info'].get('customer', '').split() or ['Job'])[-1]
    today = date.today().strftime('%Y-%m-%d')
    out_dir = os.path.join(job_dir, 'output')
    os.makedirs(out_dir, exist_ok=True)

    generated = []

    doc = build_master(brand, job, job_dir)
    path = os.path.join(out_dir, f'Work Order - MASTER - {lastname} - {today}.docx')
    doc.save(path)
    generated.append(path)

    for trade in ('hvac', 'wx', 'elec'):
        if any(r['trade'] == trade for r in job['scope_rows']):
            doc, label = build_trade(brand, job, job_dir, trade, libs, selected)
            path = os.path.join(out_dir, f'Work Order - {label} - {lastname} - {today}.docx')
            doc.save(path)
            generated.append(path)

    print(f'\nGenerated {len(generated)} work order(s):')
    for p in generated:
        print(f'  {p}')

    lint = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wo_lint.py')
    if os.path.exists(lint):
        print('\nwo-lint:')
        for p in generated:
            r = subprocess.run([sys.executable, lint, p, '--config', config_path],
                               capture_output=True, text=True, timeout=60)
            verdict = next((ln.strip() for ln in (r.stdout or '').splitlines()
                            if ln.startswith(('PASS', 'REVIEW', 'FAIL'))), 'no verdict')
            print(f'  {os.path.basename(p)}: {verdict}')
            if verdict.startswith(('FAIL', 'REVIEW')):
                print(f'    -> details: python3 {lint} "{p}" --config {config_path}')


if __name__ == '__main__':
    main()
