#!/usr/bin/env python3
"""Regenerate every graphic in the package (Pillow only — no other deps).

    python3 tools/make_graphics.py

Outputs:
    assets/logo-placeholder.png                 white wordmark for the banner
    docs/img/banner.png                         README hero
    docs/img/phasing-diagram.png                sequencing invariants flow
    docs/img/doc-family.png                     MASTER -> trade docs map
    examples/resilient-retrofits/jobs/alder-st/photos/*.png
                                                schematic sample "site photos"

Restyle by editing the palette below and re-running — every visual rebuilds
from code, so the package stays fully duplicatable.
"""

import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INK = (34, 48, 63)          # body text
SLATE = (31, 78, 121)       # primary
SLATE_FILL = (227, 234, 242)
GATE = (176, 118, 30)       # the blower-door gate accent
GATE_FILL = (248, 238, 219)
GREEN = (78, 122, 60)       # QC / done
GREEN_FILL = (230, 239, 226)
PAPER = (250, 250, 248)
MUTE = (110, 122, 134)

ARIAL = '/System/Library/Fonts/Supplemental/Arial.ttf'
ARIAL_BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'


def font(size, bold=False):
    try:
        return ImageFont.truetype(ARIAL_BOLD if bold else ARIAL, size)
    except OSError:
        return ImageFont.load_default()


def text_center(d, xy, s, f, fill):
    l, t, r, b = d.textbbox((0, 0), s, font=f)
    d.text((xy[0] - (r - l) / 2, xy[1] - (b - t) / 2 - t), s, font=f, fill=fill)


def arrow(d, x0, y0, x1, y1, color=MUTE, w=3, head=9):
    d.line([x0, y0, x1, y1], fill=color, width=w)
    import math
    ang = math.atan2(y1 - y0, x1 - x0)
    for s in (0.5,):
        pass
    p1 = (x1 - head * 1.6 * math.cos(ang - 0.42), y1 - head * 1.6 * math.sin(ang - 0.42))
    p2 = (x1 - head * 1.6 * math.cos(ang + 0.42), y1 - head * 1.6 * math.sin(ang + 0.42))
    d.polygon([(x1, y1), p1, p2], fill=color)


def box(d, x, y, w, h, fill, outline, radius=14, width=3):
    d.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill,
                        outline=outline, width=width)


# ─── assets/logo-placeholder.png ────────────────────────────────────────────

def make_logo():
    img = Image.new('RGBA', (960, 250), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    W = (255, 255, 255, 255)
    # house glyph
    d.polygon([(45, 135), (140, 45), (235, 135)], outline=W, width=12)
    d.rectangle([75, 135, 205, 215], outline=W, width=12)
    d.rectangle([120, 165, 160, 215], fill=W)
    text = font(84, bold=True)
    d.text((275, 85), 'YOUR COMPANY', font=text, fill=W)
    img.save(os.path.join(ROOT, 'assets', 'logo-placeholder.png'))


# ─── docs/img/banner.png ────────────────────────────────────────────────────

def make_banner():
    W, H = 1400, 320
    img = Image.new('RGB', (W, H), SLATE)
    d = ImageDraw.Draw(img)
    top, bottom = (26, 60, 94), (44, 92, 138)
    for y in range(H):
        t = y / H
        d.line([0, y, W, y], fill=tuple(round(a + (b - a) * t) for a, b in zip(top, bottom)))
    for i, x in enumerate(range(60, W, 96)):
        d.line([x, 0, x - 40, H], fill=(255, 255, 255, 10), width=1)
    text_center(d, (W / 2, 118), 'CREW WORK ORDERS', font(72, bold=True), (255, 255, 255))
    text_center(d, (W / 2, 205), 'scope  →  days  →  branded crew docs', font(34), (208, 222, 238))
    text_center(d, (W / 2, 262), 'a template package you rebrand with one config file',
                font(24), (170, 190, 212))
    img.save(os.path.join(ROOT, 'docs', 'img', 'banner.png'))


# ─── docs/img/phasing-diagram.png ───────────────────────────────────────────

STEPS = [
    ('1 · OPEN', 'demo out, open the\nattic / crawl / belly', SLATE, SLATE_FILL),
    ('2 · PENETRATE', 'ducts, linesets, wiring\nthrough the open plane', SLATE, SLATE_FILL),
    ('3 · AIR-SEAL', 'complete the plane —\nplates, cans, chases', SLATE, SLATE_FILL),
    ('4 · TEST', 'blower door verifies\ntight — THE GATE', GATE, GATE_FILL),
    ('5 · INSULATE', 'blow to spec — always\nthe LAST production step', SLATE, SLATE_FILL),
    ('6 · QC DAY', 'final test, walk every\nmeasure, sign-off', GREEN, GREEN_FILL),
]


def make_phasing():
    W, H = 1560, 470
    img = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(img)
    text_center(d, (W / 2, 46), 'SEQUENCING INVARIANTS — WHY THE DAYS LAND WHERE THEY DO',
                font(30, bold=True), INK)
    bw, bh, gap, y = 226, 176, 34, 96
    x = (W - (bw * 6 + gap * 5)) / 2
    for i, (title, body, edge, fill) in enumerate(STEPS):
        box(d, x, y, bw, bh, fill, edge)
        text_center(d, (x + bw / 2, y + 38), title, font(26, bold=True), edge)
        for j, line in enumerate(body.split('\n')):
            text_center(d, (x + bw / 2, y + 84 + j * 30), line, font(20), INK)
        if i < 5:
            arrow(d, x + bw + 4, y + bh / 2, x + bw + gap - 4, y + bh / 2)
        x += bw + gap
    # day bands
    bands = [('DAY 1', 0, 1, SLATE), ('DAY 2 (LAST PRODUCTION DAY)', 1, 5, SLATE),
             ('QC — SEPARATE DAY', 5, 6, GREEN)]
    x0 = (W - (226 * 6 + 34 * 5)) / 2
    by = y + bh + 44
    for label, a, b, color in bands:
        bx0 = x0 + a * 260
        bx1 = x0 + b * 260 - 34
        d.line([bx0, by, bx1, by], fill=color, width=4)
        d.line([bx0, by - 8, bx0, by + 8], fill=color, width=4)
        d.line([bx1, by - 8, bx1, by + 8], fill=color, width=4)
        text_center(d, ((bx0 + bx1) / 2, by + 28), label, font(21, bold=True), color)
    text_center(d, (W / 2, by + 78),
                'crews stack on production days · the blower door gates the blow · nobody QCs their own work',
                font(21), MUTE)
    img.save(os.path.join(ROOT, 'docs', 'img', 'phasing-diagram.png'))


# ─── docs/img/doc-family.png ────────────────────────────────────────────────

def make_family():
    W, H = 1240, 520
    img = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(img)
    text_center(d, (W / 2, 44), 'THE DOCUMENT FAMILY', font(30, bold=True), INK)
    # master
    mw, mh = 420, 120
    mx, my = (W - mw) / 2, 92
    box(d, mx, my, mw, mh, SLATE, SLATE)
    text_center(d, (W / 2, my + 40), 'MASTER WORK ORDER', font(28, bold=True), (255, 255, 255))
    text_center(d, (W / 2, my + 82), 'schedule · all trades · per-day checklists',
                font(20), (208, 222, 238))
    # trades
    tw, th, ty = 320, 130, 300
    labels = [('HVAC', 'equipment, ducts,\ncommissioning record'),
              ('WEATHERIZATION', 'air-seal, insulation,\nventilation QA'),
              ('ELECTRICAL', 'only when real\nelectrician scope exists')]
    xs = [70, 70 + tw + 40, 70 + 2 * (tw + 40)]
    for (label, body), tx in zip(labels, xs):
        arrow(d, W / 2, my + mh, tx + tw / 2, ty - 8, color=SLATE, w=3)
        box(d, tx, ty, tw, th, SLATE_FILL, SLATE)
        text_center(d, (tx + tw / 2, ty + 34), label, font(24, bold=True), SLATE)
        for j, line in enumerate(body.split('\n')):
            text_center(d, (tx + tw / 2, ty + 74 + j * 27), line, font(19), INK)
    text_center(d, (W / 2, 478),
                'return visits get the same format as a one-day PUNCH LIST — never a text thread',
                font(21), MUTE)
    img.save(os.path.join(ROOT, 'docs', 'img', 'doc-family.png'))


# ─── sample "site photos" (schematics, clearly not real) ────────────────────

PHOTO_BG = (238, 240, 236)
PHOTO_INK = (52, 64, 58)
PHOTO_ACCENT = (123, 160, 91)


def _photo_canvas(title):
    img = Image.new('RGB', (880, 620), PHOTO_BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 879, 619], outline=(200, 205, 198), width=3)
    d.rectangle([0, 540, 880, 620], fill=(225, 228, 221))
    d.text((28, 560), title, font=font(30, bold=True), fill=PHOTO_INK)
    d.text((622, 22), 'SAMPLE — schematic,', font=font(20), fill=(150, 108, 96))
    d.text((622, 46), 'not a site photo', font=font(20), fill=(150, 108, 96))
    return img, d


def make_photos():
    out = os.path.join(ROOT, 'examples', 'resilient-retrofits', 'jobs', 'alder-st', 'photos')
    os.makedirs(out, exist_ok=True)

    img, d = _photo_canvas('Furnace closet — hallway')
    box(d, 320, 120, 240, 360, (215, 219, 212), PHOTO_INK, radius=6)
    d.rectangle([395, 170, 485, 250], outline=PHOTO_INK, width=4)
    d.line([440, 120, 440, 60], fill=PHOTO_INK, width=8)
    d.ellipse([405, 300, 475, 370], outline=PHOTO_INK, width=4)
    d.text((70, 140), 'gas furnace', font=font(24), fill=PHOTO_INK)
    arrow(d, 190, 155, 315, 175, color=PHOTO_ACCENT, w=4)
    d.text((70, 400), 'flue exits\nthrough roof', font=font(22), fill=PHOTO_INK)
    img.save(os.path.join(out, '01-furnace-closet.png'))

    img, d = _photo_canvas('Attic from hatch — vermiculite-free')
    for x in range(60, 840, 90):
        d.polygon([(x, 460), (x + 45, 130), (x + 55, 130), (x + 10, 460)], outline=PHOTO_INK, width=3)
    d.line([40, 460, 850, 460], fill=PHOTO_INK, width=5)
    d.line([40, 130, 850, 130], fill=(180, 185, 178), width=3)
    d.rectangle([600, 380, 700, 460], outline=PHOTO_ACCENT, width=5)
    d.text((580, 330), 'hatch', font=font(22), fill=PHOTO_ACCENT)
    d.text((70, 80), 'rafters — baffles land at every eave bay', font=font(22), fill=PHOTO_INK)
    img.save(os.path.join(out, '02-attic-hatch.png'))

    img, d = _photo_canvas('Panel — spare spaces lower right')
    box(d, 300, 80, 280, 420, (222, 226, 219), PHOTO_INK, radius=6)
    for i in range(8):
        d.rectangle([330, 120 + i * 44, 430, 148 + i * 44], outline=PHOTO_INK, width=3)
        d.rectangle([450, 120 + i * 44, 550, 148 + i * 44], outline=PHOTO_INK, width=3)
    d.rectangle([450, 428, 550, 456], outline=PHOTO_ACCENT, width=5)
    d.rectangle([450, 384, 550, 412], outline=PHOTO_ACCENT, width=5)
    d.text((600, 390), 'ODU circuit\nlands here', font=font(22), fill=PHOTO_ACCENT)
    img.save(os.path.join(out, '03-panel.png'))

    img, d = _photo_canvas('East wall — ODU pad location')
    d.rectangle([60, 100, 620, 470], outline=PHOTO_INK, width=5)
    for y in range(130, 470, 40):
        d.line([60, y, 620, y], fill=(205, 209, 202), width=2)
    d.rectangle([650, 400, 830, 470], fill=(215, 219, 212), outline=PHOTO_INK, width=4)
    d.text((660, 415), 'pad', font=font(24), fill=PHOTO_INK)
    d.ellipse([560, 200, 600, 240], outline=PHOTO_ACCENT, width=5)
    d.text((380, 150), 'lineset penetration —\nsealed after ducts run', font=font(22), fill=PHOTO_ACCENT)
    img.save(os.path.join(out, '04-odu-wall.png'))

    img, d = _photo_canvas('Hall bath — fan location')
    for x in range(60, 840, 70):
        d.line([x, 60, x, 500], fill=(210, 214, 207), width=2)
    for y in range(60, 500, 70):
        d.line([60, y, 840, y], fill=(210, 214, 207), width=2)
    d.ellipse([380, 210, 500, 330], outline=PHOTO_INK, width=5)
    d.ellipse([415, 245, 465, 295], outline=PHOTO_INK, width=3)
    arrow(d, 500, 270, 720, 160, color=PHOTO_ACCENT, w=4)
    d.text((600, 100), 'duct out the roof,\nfirst 3 ft straight', font=font(22), fill=PHOTO_ACCENT)
    img.save(os.path.join(out, '05-bath-fan.png'))

    img, d = _photo_canvas('Range wall — hood duct path')
    d.rectangle([320, 300, 560, 500], outline=PHOTO_INK, width=4)
    d.ellipse([355, 330, 400, 360], outline=PHOTO_INK, width=3)
    d.ellipse([475, 330, 520, 360], outline=PHOTO_INK, width=3)
    d.polygon([(320, 240), (560, 240), (520, 180), (360, 180)], outline=PHOTO_INK, width=4)
    d.rectangle([420, 80, 460, 180], outline=PHOTO_ACCENT, width=5)
    arrow(d, 440, 80, 440, 40, color=PHOTO_ACCENT, w=5)
    d.text((490, 60), 'through cabinet,\nout the wall cap', font=font(22), fill=PHOTO_ACCENT)
    img.save(os.path.join(out, '06-range-hood.png'))


if __name__ == '__main__':
    make_logo()
    make_banner()
    make_phasing()
    make_family()
    make_photos()
    print('graphics rebuilt: logo, banner, phasing, doc-family, 6 sample photos')
