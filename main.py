#!/usr/bin/env python3
"""The World in One Day -- Saturday 21 November 2026.

A self-contained Python program (standard library only) that draws one
1024x1024 PNG summing up the world news of Saturday 21 November 2026 and
writes it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

Everything is rendered by code: a hand-built 5x7 bitmap font, a small
raster canvas (rectangles, lines, circles, polygons), panel illustrations
drawn from primitives, and the day's headlines laid out as a front page.
The program uses no network, no clock and no randomness, so two runs
produce byte-identical output.

News content lives in the STORIES structure below and comes from real
reporting of 21 November 2026 (Reuters, BBC, Al Jazeera, The Guardian,
France 24, UPI and others); see the repository README for the summary.
"""

import os
import struct
import zlib
from math import isqrt

# ---------------------------------------------------------------------------
# The day's news (Saturday 21 November 2026), as reported that day.
# ---------------------------------------------------------------------------

DATE_LINE = "SATURDAY · 21 NOVEMBER 2026"

LEAD = {
    "kicker": "MIDDLE EAST · MANAMA, BAHRAIN",
    "headline": "IRAN STRIKES US BASES IN BAHRAIN",
    "body": [
        "REVOLUTIONARY GUARDS SAY THEY HIT US POSITIONS AT",
        "AL-RIFFA AND AWALI. BAHRAIN REPORTS A FIRE AT A",
        "CIVILIAN INDUSTRIAL SITE, NO INJURIES, AND SAYS",
        "ITS AIR DEFENCES INTERCEPTED OTHER ATTACKS.",
        "TRUMP SAYS HE WANTS A PERMANENT DEAL WITH IRAN.",
    ],
}

SECOND = {
    "kicker": "UKRAINE · KRYVYI RIH, THE PRESIDENT'S HOMETOWN",
    "headline": "RUSSIAN MISSILE HITS ZELENSKY'S HOMETOWN",
    "body": [
        "A BALLISTIC MISSILE STRUCK THE CITY CENTRE: 2 KILLED, DOZENS WOUNDED.",
        "A SEPARATE STRIKE ON LVIV KILLED TWO PEOPLE. IT CAME A DAY AFTER",
        "RUSSIAN MISSILES FELL IN POLAND, A NATO MEMBER. WARSAW CALLED IT",
        "A DELIBERATE PROVOCATION; NATO: A GRAVE VIOLATION OF ITS AIRSPACE.",
    ],
}

PANELS = [
    {
        "kicker": "CLIMATE · ANTALYA, TURKIYE",
        "accent": (16, 108, 108),
        "headline": ["COP31 TALKS RUN PAST", "DEADLINE, NO DEAL YET"],
        "body": [
            "FOSSIL FUELS SPLIT NEARLY 200",
            "COUNTRIES. A PROTESTER DISRUPTS",
            "THE CLOSING PLENARY IN ANGER.",
        ],
        "icon": "globe",
    },
    {
        "kicker": "JUSTICE · SINALOA, MEXICO",
        "accent": (150, 52, 40),
        "headline": ["MEXICO CAPTURES FBI'S", "MOST-WANTED CARTEL BOSS"],
        "body": [
            "'CHAPO ISIDRO' SEIZED IN A RAID",
            "IN GUASAVE. GUNFIGHTS, FIRES",
            "AND BLOCKADES FOLLOW: 11 DEAD.",
        ],
        "icon": "shield",
    },
    {
        "kicker": "MARKETS · NEW YORK",
        "accent": (30, 110, 60),
        "headline": ["AI SELL-OFF PUSHES US", "STOCKS INTO CORRECTION"],
        "body": [
            "S&P 500 AND DOW IN CORRECTION;",
            "NASDAQ ERASES ITS 2026 GAINS.",
            "ANTHROPIC IPO STUMBLES DAY 2.",
        ],
        "icon": "chart",
    },
    {
        "kicker": "POLITICS · SHENZHEN, CHINA",
        "accent": (88, 60, 140),
        "headline": ["TRUMP DEFENDS PUTIN", "TIES AFTER SUMMIT"],
        "body": [
            "ZELENSKY CALLS PUTIN 'A KILLER'",
            "AFTER THE THREE-WAY SUMMIT.",
            "NUCLEAR-RISK TALKS AGREED.",
        ],
        "icon": "flags",
    },
]

MINIS = [
    {
        "kicker": "SCIENCE · MATHS",
        "accent": (16, 108, 108),
        "body": [
            "MATHEMATICIAN CLAIMS AI HELPED",
            "PROVE RIEMANN; CHECKS GO ON.",
        ],
    },
    {
        "kicker": "BRAZIL · BRASILIA",
        "accent": (150, 52, 40),
        "body": [
            "EX-PRESIDENT BOLSONARO IN ICU;",
            "ABDOMEN BLOCKED; STABLE, AWAKE",
        ],
    },
]

TICKER = [
    "ALSO TODAY +++ TWO TANKER INCIDENTS NEAR THE STRAIT OF HORMUZ",
    "FRANCE: 82,500 MARCH OVER COST OF LIVING +++ EU-INDONESIA DEAL SIGNED",
    "RUGBY: IRELAND BEAT SOUTH AFRICA 20-17 +++ TRUMP TELLS EUROPE: DEFUND UKRAINE",
]

SOURCES = "SOURCES: REUTERS · BBC · AL JAZEERA · THE GUARDIAN · FRANCE 24 · UPI · DW"

# ---------------------------------------------------------------------------
# Colours.
# ---------------------------------------------------------------------------

PAPER = (247, 243, 232)
WHITE = (255, 255, 255)
INK = (18, 24, 38)
NAVY = (22, 40, 63)
DARK_BAND = (20, 34, 54)
RED = (178, 34, 52)
GOLD = (198, 152, 46)
GREY = (96, 100, 108)
ORANGE = (232, 122, 36)
YELLOW = (244, 196, 48)
SKY = (120, 170, 220)

# ---------------------------------------------------------------------------
# A 5x7 bitmap font. Each glyph is seven rows of five pixels, written out
# as strings so the letterforms stay easy to check by eye.
# ---------------------------------------------------------------------------

FONT = {
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": (".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "'": (".#...", ".#...", "#....", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": (".##..", ".#...", "#....", "#....", "#....", ".#...", ".##.."),
    ")": ("..##.", "...#.", "....#", "....#", "....#", "...#.", "..##."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#..##"),
    "$": (".####", "#.#..", "#.#..", ".###.", "..#.#", "..#.#", "####."),
    "·": (".....", ".....", ".....", ".##..", ".##..", ".....", "....."),
}

GLYPH_W = 5
GLYPH_H = 7


def text_width(text, scale):
    """Pixel width of a string: 5 px glyph + 1 px gap, times the scale."""
    if not text:
        return 0
    return (len(text) * (GLYPH_W + 1) - 1) * scale


# ---------------------------------------------------------------------------
# The canvas: an RGB pixel buffer with drawing primitives.
# ---------------------------------------------------------------------------


class Canvas:
    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.pixels = bytearray(background) * (width * height)

    def set_pixel(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i:i + 3] = bytes(colour)

    def fill_rect(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.width + x0) * 3
            self.pixels[i:i + len(row)] = row

    def outline_rect(self, x, y, w, h, colour, thick=2):
        self.fill_rect(x, y, w, thick, colour)
        self.fill_rect(x, y + h - thick, w, thick, colour)
        self.fill_rect(x, y, thick, h, colour)
        self.fill_rect(x + w - thick, y, thick, h, colour)

    def fill_circle(self, cx, cy, r, colour):
        for dy in range(-r, r + 1):
            dx = isqrt(r * r - dy * dy)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, colour)

    def outline_circle(self, cx, cy, r, colour, thick=2):
        # Ring drawn as many small filled circles along the circumference;
        # _circle_points returns offsets from the centre, so add it back.
        steps = max(24, r * 6)
        for (px, py) in _circle_points(r, steps):
            self.fill_circle(cx + px, cy + py, thick, colour)

    def outline_ellipse(self, cx, cy, rx, ry, colour, thick=1):
        steps = max(24, rx * 4)
        for (px, py) in _circle_points(100, steps):
            self.fill_circle(cx + px * rx // 100, cy + py * ry // 100,
                             thick, colour)

    def line(self, x0, y0, x1, y1, colour, thick=2):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        r = max(1, thick // 2)
        for i in range(steps + 1):
            x = x0 + (x1 - x0) * i // steps
            y = y0 + (y1 - y0) * i // steps
            self.fill_circle(x, y, r, colour)

    def fill_polygon(self, points, colour):
        ys = [p[1] for p in points]
        top = max(0, min(ys))
        bottom = min(self.height - 1, max(ys))
        n = len(points)
        for y in range(top, bottom + 1):
            hits = []
            for i in range(n):
                xa, ya = points[i]
                xb, yb = points[(i + 1) % n]
                if ya == yb:
                    continue
                if (ya <= y < yb) or (yb <= y < ya):
                    x = xa + (y - ya) * (xb - xa) // (yb - ya)
                    hits.append(x)
            hits.sort()
            for i in range(0, len(hits) - 1, 2):
                self.fill_rect(hits[i], y, hits[i + 1] - hits[i] + 1, 1, colour)

    def text(self, x, y, text, scale, colour, bold=False):
        cursor = x
        for ch in text.upper():
            glyph = FONT.get(ch)
            if glyph is None:
                glyph = FONT[" "]
            for row_i, row in enumerate(glyph):
                for col_i, cell in enumerate(row):
                    if cell == "#":
                        px = cursor + col_i * scale
                        py = y + row_i * scale
                        self.fill_rect(px, py, scale, scale, colour)
                        if bold:
                            self.fill_rect(px + scale, py, scale, scale, colour)
            cursor += (GLYPH_W + 1) * scale
        return cursor

    def text_centred(self, cx, y, text, scale, colour, bold=False):
        w = text_width(text, scale) + (scale if bold else 0)
        return self.text(cx - w // 2, y, text, scale, colour, bold)


_SIN_TABLE = None


def _circle_points(r, steps):
    """Points on a circle, from a fixed sine table (deterministic)."""
    global _SIN_TABLE
    if _SIN_TABLE is None:
        import math

        _SIN_TABLE = [int(round(10000 * math.sin(2 * math.pi * i / 720)))
                      for i in range(720)]
    points = []
    for i in range(steps):
        idx = (i * 720 // steps) % 720
        s = _SIN_TABLE[idx]
        c = _SIN_TABLE[(idx + 180) % 720]
        points.append((0, 0))  # placeholder replaced below
        points[-1] = (int(round(r * c / 10000)), int(round(r * s / 10000)))
    return points


def save_png(canvas, path):
    """Write the canvas as a PNG with correct chunks and checksums."""
    raw = bytearray()
    stride = canvas.width * 3
    for y in range(canvas.height):
        raw.append(0)  # filter: none
        start = y * stride
        raw.extend(canvas.pixels[start:start + stride])
    compressed = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", compressed)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)


# ---------------------------------------------------------------------------
# Panel illustrations, each drawn from primitives inside a small box.
# ---------------------------------------------------------------------------


def draw_missile_scene(cv, x, y, w, h, dark_bg=False):
    """A missile rising over a row of base buildings, with a burst."""
    ground = y + h - 18
    block = (90, 100, 118) if not dark_bg else (140, 155, 175)
    # Base buildings along the bottom.
    cv.fill_rect(x + 4, ground - 16, 34, 16, block)
    cv.fill_rect(x + 46, ground - 24, 26, 24, block)
    cv.fill_rect(x + 80, ground - 12, 40, 12, block)
    cv.fill_rect(x, ground, w, 3, block)
    # Missile body, slim, angled up to the right.
    tip = (x + w - 26, y + 8)
    tail = (x + 34, y + h - 44)
    body = [
        (tail[0] - 4, tail[1] + 4),
        (tail[0] + 4, tail[1] - 4),
        (tip[0] - 8, tip[1] - 4),
        (tip[0] - 2, tip[1] + 8),
    ]
    cv.fill_polygon(body, (206, 210, 216))
    cv.fill_polygon([(tip[0] - 8, tip[1] - 4), (tip[0] - 2, tip[1] + 8),
                     (tip[0] + 8, tip[1] - 2)], RED)
    # Fins at the tail.
    cv.fill_polygon([(tail[0] - 4, tail[1] + 4), (tail[0] - 16, tail[1] + 14),
                     (tail[0] - 2, tail[1] + 13)], NAVY)
    cv.fill_polygon([(tail[0] + 4, tail[1] - 4), (tail[0] + 13, tail[1] - 16),
                     (tail[0] + 14, tail[1] - 2)], NAVY)
    # Flame and smoke trail.
    cv.fill_polygon([(tail[0] - 10, tail[1] + 10), (tail[0] + 1, tail[1] - 1),
                     (tail[0] - 20, tail[1] + 28)], ORANGE)
    cv.fill_polygon([(tail[0] - 13, tail[1] + 15), (tail[0] - 5, tail[1] + 7),
                     (tail[0] - 20, tail[1] + 27)], YELLOW)
    for i in range(4):
        sx = tail[0] - 26 - i * 14
        sy = tail[1] + 30 + i * 9
        cv.fill_circle(sx, sy, 6 - i // 2, (198, 200, 204))
    # Burst star near the tip.
    cx, cy = tip[0] + 18, tip[1] + 16
    star = []
    for i in range(16):
        r = 13 if i % 2 == 0 else 5
        pts = _circle_points(r, 16)
        star.append((cx + pts[i][0], cy + pts[i][1]))
    cv.fill_polygon(star, GOLD)


def draw_skyline_scene(cv, x, y, w, h):
    """City rooftops under a descending missile (for the dark band)."""
    base = y + h
    tone = (96, 116, 142)
    heights = [26, 40, 30, 48, 34, 44, 28, 38]
    bx = x
    for bw, bh in zip([22, 18, 26, 20, 24, 18, 26, 20], heights):
        cv.fill_rect(bx, base - bh, bw, bh, tone)
        bx += bw + 4
    # Descending missile.
    tip = (x + w - 30, y + h - 20)
    tail = (x + w - 78, y + 6)
    cv.fill_polygon([(tail[0] - 6, tail[1] + 6), (tail[0] + 6, tail[1] - 6),
                     (tip[0], tip[1] - 8), (tip[0] + 8, tip[1])], (206, 210, 216))
    cv.fill_polygon([(tail[0] - 12, tail[1] + 12), (tail[0], tail[1]),
                     (tail[0] - 20, tail[1] + 22)], ORANGE)
    # Windows, in two staggered rows.
    for i, wx in enumerate(range(x + 4, x + w - 10, 16)):
        cv.fill_rect(wx, base - 12 - (i % 2) * 12, 4, 4, YELLOW)


def draw_globe_icon(cv, x, y, size):
    r = size // 2 - 2
    cx, cy = x + size // 2, y + size // 2
    cv.fill_circle(cx, cy, r, (168, 216, 234))
    cv.outline_circle(cx, cy, r, NAVY, thick=2)
    # Meridians as ellipses, parallels as straight lines.
    cv.outline_ellipse(cx, cy, r // 2, r, NAVY, thick=1)
    cv.line(cx, cy - r, cx, cy + r, NAVY, thick=1)
    cv.line(cx - r, cy, cx + r, cy, NAVY, thick=1)
    cv.line(cx - r * 3 // 4, cy - r // 2, cx + r * 3 // 4, cy - r // 2, NAVY, thick=1)
    cv.line(cx - r * 3 // 4, cy + r // 2, cx + r * 3 // 4, cy + r // 2, NAVY, thick=1)
    # A hot spot for the warming planet.
    cv.fill_circle(cx + r // 3, cy - r // 3, 4, RED)


def draw_shield_icon(cv, x, y, size):
    cx = x + size // 2
    shield = [
        (x + 4, y + 2),
        (x + size - 4, y + 2),
        (x + size - 4, y + size // 2),
        (cx, y + size - 2),
        (x + 4, y + size // 2),
    ]
    cv.fill_polygon(shield, NAVY)
    star = []
    for i in range(10):
        r = 9 if i % 2 == 0 else 4
        p = _circle_points(r, 10)
        star.append((cx + p[i][0], y + size // 2 - 4 + p[i][1]))
    cv.fill_polygon(star, GOLD)


def draw_chart_icon(cv, x, y, size):
    cv.line(x + 4, y + 4, x + 4, y + size - 6, INK, thick=2)
    cv.line(x + 4, y + size - 6, x + size - 2, y + size - 6, INK, thick=2)
    pts = [(x + 8, y + 12), (x + 20, y + 18), (x + 30, y + 14),
           (x + 42, y + 30), (x + size - 8, y + size - 16)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], RED, thick=3)
    tip = pts[-1]
    cv.fill_polygon([(tip[0], tip[1]), (tip[0] - 12, tip[1] - 2),
                     (tip[0] - 2, tip[1] - 12)], RED)


def draw_flags_icon(cv, x, y, size):
    # Three small flags on poles: United States, China, Russia (simplified).
    pole = (90, 90, 96)
    fx = x + 1
    for i in range(3):
        cv.fill_rect(fx, y + 2, 2, size - 4, pole)
        fw, fh = 17, 12
        top = y + 2
        if i == 0:  # Stars and stripes, simplified.
            for s in range(6):
                cv.fill_rect(fx + 2, top + s * 2, fw, 1,
                             RED if s % 2 == 0 else WHITE)
            cv.fill_rect(fx + 2, top, 7, 5, NAVY)
        elif i == 1:  # China: red field, one gold star.
            cv.fill_rect(fx + 2, top, fw, fh, (222, 41, 57))
            cv.fill_circle(fx + 6, top + 4, 2, YELLOW)
        else:  # Russia: white, blue, red bands.
            cv.fill_rect(fx + 2, top, fw, 4, WHITE)
            cv.fill_rect(fx + 2, top + 4, fw, 4, (28, 70, 160))
            cv.fill_rect(fx + 2, top + 8, fw, 4, (213, 43, 30))
        fx += fw + 4


ICON_DRAWERS = {
    "globe": draw_globe_icon,
    "shield": draw_shield_icon,
    "chart": draw_chart_icon,
    "flags": draw_flags_icon,
}

# ---------------------------------------------------------------------------
# Page layout.
# ---------------------------------------------------------------------------

PAGE_W = 1024
PAGE_H = 1024
MARGIN = 34
CONTENT_W = PAGE_W - 2 * MARGIN


def draw_masthead(cv):
    cv.fill_rect(MARGIN, 20, CONTENT_W, 4, RED)
    cv.text_centred(PAGE_W // 2, 32,
                    "THE DAY IN ONE PICTURE · WORLD NEWS, TOLD IN ONE IMAGE",
                    2, GREY)
    cv.text_centred(PAGE_W // 2, 54, "THE WORLD IN ONE DAY", 7, INK)
    cv.fill_rect(MARGIN, 112, CONTENT_W, 3, NAVY)
    cv.fill_rect(MARGIN, 119, CONTENT_W, 1, NAVY)
    # The date band: the single most important line on the page.
    cv.fill_rect(MARGIN, 128, CONTENT_W, 44, INK)
    cv.text_centred(PAGE_W // 2, 139, DATE_LINE, 3, WHITE, bold=True)


def draw_lead(cv, y):
    h = 216
    cv.fill_rect(MARGIN, y, CONTENT_W, h, WHITE)
    cv.outline_rect(MARGIN, y, CONTENT_W, h, NAVY, thick=2)
    cv.fill_rect(MARGIN, y, 10, h, RED)
    x = MARGIN + 28
    # Kicker chip.
    kw = text_width(LEAD["kicker"], 2) + 20
    cv.fill_rect(x, y + 16, kw, 26, RED)
    cv.text(x + 10, y + 22, LEAD["kicker"], 2, WHITE, bold=True)
    cv.text(x, y + 58, LEAD["headline"], 3, NAVY)
    ty = y + 94
    for line in LEAD["body"]:
        cv.text(x, ty, line, 2, INK)
        ty += 21
    draw_missile_scene(cv, 800, y + 20, 176, 176)


def draw_second(cv, y):
    h = 170
    cv.fill_rect(MARGIN, y, CONTENT_W, h, DARK_BAND)
    cv.fill_rect(MARGIN, y, 10, h, GOLD)
    x = MARGIN + 28
    cv.text(x, y + 14, SECOND["kicker"], 2, GOLD, bold=True)
    cv.text(x, y + 40, SECOND["headline"], 3, WHITE)
    ty = y + 76
    for line in SECOND["body"]:
        cv.text(x, ty, line, 2, WHITE)
        ty += 21
    draw_skyline_scene(cv, 806, y + 12, 170, 58)


def draw_panel(cv, x, y, w, h, panel):
    cv.fill_rect(x, y, w, h, WHITE)
    cv.outline_rect(x, y, w, h, NAVY, thick=2)
    cv.fill_rect(x, y, w, 6, panel["accent"])
    tx = x + 14
    cv.text(tx, y + 14, panel["kicker"], 2, panel["accent"], bold=True)
    hy = y + 36
    for line in panel["headline"]:
        cv.text(tx, hy, line, 2, NAVY)
        hy += 19
    by = y + 78
    for line in panel["body"]:
        cv.text(tx, by, line, 2, INK)
        by += 17
    ICON_DRAWERS[panel["icon"]](cv, x + w - 58, y + 10, 46)


def draw_mini(cv, x, y, w, h, mini):
    cv.fill_rect(x, y, w, h, WHITE)
    cv.outline_rect(x, y, w, h, NAVY, thick=2)
    cv.fill_rect(x, y, 6, h, mini["accent"])
    tx = x + 16
    cv.text(tx, y + 9, mini["kicker"], 2, mini["accent"], bold=True)
    by = y + 30
    for line in mini["body"]:
        cv.text(tx, by, line, 2, INK)
        by += 17


def draw_footer(cv, y):
    ty = y
    for line in TICKER:
        cv.text_centred(PAGE_W // 2, ty, line, 2, INK)
        ty += 18
    cv.fill_rect(MARGIN, ty + 2, CONTENT_W, 1, GREY)
    cv.text_centred(PAGE_W // 2, ty + 8, SOURCES, 1, GREY)


def render():
    cv = Canvas(PAGE_W, PAGE_H, PAPER)
    draw_masthead(cv)
    draw_lead(cv, 186)
    draw_second(cv, 414)
    # Four panels in a 2x2 grid.
    pw = (CONTENT_W - 16) // 2
    ph = 126
    positions = [(MARGIN, 596), (MARGIN + pw + 16, 596),
                 (MARGIN, 734), (MARGIN + pw + 16, 734)]
    for (px, py), panel in zip(positions, PANELS):
        draw_panel(cv, px, py, pw, ph, panel)
    # Two mini stories side by side.
    mw = (CONTENT_W - 16) // 2
    draw_mini(cv, MARGIN, 872, mw, 64, MINIS[0])
    draw_mini(cv, MARGIN + mw + 16, 872, mw, 64, MINIS[1])
    draw_footer(cv, 948)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = save_png(render(), path)
    print("wrote", path, size, "bytes")


if __name__ == "__main__":
    main()
