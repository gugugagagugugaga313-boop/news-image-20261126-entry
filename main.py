#!/usr/bin/env python3
"""News-image entry for 26 November 2026 (make.fun news-image-20261126).

Draws a 1024x1024 newspaper front page entirely with the Python
standard library: a pixel canvas, a small 5x7 bitmap font defined below,
and a hand-rolled PNG encoder (zlib + struct). No network, no random
numbers, no clock: two runs write identical bytes.

Stories (all reported on 26 November 2026, cross-checked against the
morning wires and digests dated that day):
  1. Gulf: Houthis claim a strike on Saudi Arabia's Ras Tanura refinery;
     tankers hit by mines in the Strait of Hormuz; oil prices jump.
  2. Gaza: Israel kills Hamas interior-security chief Mohammad Abuelouf;
     the ceasefire is under strain.
  3. Ukraine: Ukrainian strikes set two Russian oil refineries ablaze
     overnight; Putin vows retaliation.
  4. Space: BepiColombo enters orbit around Mercury after an 8-year trip.
  5. India: 18th anniversary of the 26/11 Mumbai attacks, on
     Constitution Day. Plus: US tariff plan, Pakistan's first astronaut
     to China's space station, Gukesh's Game 2 draw in the chess title
     match.
"""

import os
import struct
import zlib

W, H = 1024, 1024

NAVY = (16, 38, 63)
NAVY2 = (24, 56, 90)
GOLD = (217, 164, 65)
CREAM = (246, 241, 227)
WHITE = (255, 255, 255)
INK = (24, 24, 28)
GREY = (96, 96, 100)
RED = (178, 44, 36)
TEAL = (18, 110, 96)
ORANGE = (224, 110, 30)
SKY = (52, 120, 168)
BROWN = (146, 104, 66)
LIGHT = (232, 226, 210)


# ---------------------------------------------------------------- font
# 5x7 bitmap font, uppercase only. Each glyph is 7 rows of 5 bits.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "00100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "01100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(px, x, y, text, color, scale):
    """Draw uppercase text; unknown chars become a space."""
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    fill_rect(px, cx + col * scale, y + row * scale,
                              scale, scale, color)
        cx += 6 * scale
    return cx


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines."""
    words = text.upper().split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# -------------------------------------------------------------- canvas
def new_canvas():
    return bytearray(W * H * 3)


def put(px, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = color


def fill_rect(px, x, y, w, h, color):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            px[i], px[i + 1], px[i + 2] = color


def rect_border(px, x, y, w, h, color, t=3):
    fill_rect(px, x, y, w, t, color)
    fill_rect(px, x, y + h - t, w, t, color)
    fill_rect(px, x, y, t, h, color)
    fill_rect(px, x + w - t, y, t, h, color)


def circle(px, cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                put(px, xx, yy, color)


def ring(px, cx, cy, r, color, t=3):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d = (xx - cx) ** 2 + (yy - cy) ** 2
            if (r - t) ** 2 <= d <= r * r:
                put(px, xx, yy, color)


def triangle(px, x0, y0, x1, y1, x2, y2, color):
    """Filled triangle via scanline sampling."""
    minx, maxx = min(x0, x1, x2), max(x0, x1, x2)
    miny, maxy = min(y0, y1, y2), max(y0, y1, y2)

    def sign(ax, ay, bx, by, cx, cy):
        return (ax - cx) * (by - cy) - (bx - cx) * (ay - cy)

    for yy in range(miny, maxy + 1):
        for xx in range(minx, maxx + 1):
            d0 = sign(xx, yy, x0, y0, x1, y1)
            d1 = sign(xx, yy, x1, y1, x2, y2)
            d2 = sign(xx, yy, x2, y2, x0, y0)
            if (d0 >= 0 and d1 >= 0 and d2 >= 0) or \
               (d0 <= 0 and d1 <= 0 and d2 <= 0):
                put(px, xx, yy, color)


def flame(px, cx, base_y, size, outer, inner):
    """A simple flame: outer triangle + inner triangle, on a base."""
    triangle(px, cx - size, base_y, cx, base_y - 2 * size,
             cx + size, base_y, outer)
    triangle(px, cx - size // 2, base_y, cx, base_y - size,
             cx + size // 2, base_y, inner)


# ----------------------------------------------------------------- png
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(px):
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw.extend(px[y * W * 3:(y + 1) * W * 3])
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
            chunk(b"IEND", b""))


# --------------------------------------------------------------- icons
def icon_gulf(px, x, y):
    """Oil refinery tower with flame and smoke."""
    fill_rect(px, x + 18, y + 58, 26, 62, NAVY2)
    fill_rect(px, x + 52, y + 38, 26, 82, NAVY2)
    fill_rect(px, x + 86, y + 74, 22, 46, NAVY2)
    fill_rect(px, x + 24, y + 66, 6, 6, LIGHT)
    fill_rect(px, x + 24, y + 82, 6, 6, LIGHT)
    fill_rect(px, x + 58, y + 48, 6, 6, LIGHT)
    fill_rect(px, x + 58, y + 64, 6, 6, LIGHT)
    fill_rect(px, x + 58, y + 80, 6, 6, LIGHT)
    fill_rect(px, x + 10, y + 118, 106, 6, INK)
    triangle(px, x + 22, y + 58, x + 31, y + 40, x + 40, y + 58, RED)
    flame(px, x + 65, y + 40, 13, ORANGE, GOLD)
    circle(px, x + 30, y + 26, 9, GREY)
    circle(px, x + 46, y + 14, 11, GREY)
    circle(px, x + 64, y + 8, 8, GREY)


def icon_gaza(px, x, y):
    """City blocks under a burst."""
    fill_rect(px, x + 8, y + 66, 30, 54, NAVY2)
    fill_rect(px, x + 44, y + 46, 30, 74, NAVY2)
    fill_rect(px, x + 80, y + 80, 30, 40, NAVY2)
    fill_rect(px, x + 14, y + 74, 6, 6, LIGHT)
    fill_rect(px, x + 14, y + 90, 6, 6, LIGHT)
    fill_rect(px, x + 50, y + 54, 6, 6, LIGHT)
    fill_rect(px, x + 50, y + 70, 6, 6, LIGHT)
    fill_rect(px, x + 50, y + 86, 6, 6, LIGHT)
    fill_rect(px, x + 86, y + 88, 6, 6, LIGHT)
    fill_rect(px, x + 4, y + 118, 112, 6, INK)
    cx, cy = x + 62, y + 26
    for dx, dy in ((0, -20), (0, 20), (-20, 0), (20, 0),
                   (-14, -14), (14, -14), (-14, 14), (14, 14)):
        triangle(px, cx, cy, cx + dx, cy + dy, cx + dy // 2, cy + dx // 2,
                 GOLD)
    circle(px, cx, cy, 12, RED)
    circle(px, cx, cy, 6, GOLD)


def icon_ukraine(px, x, y):
    """Two refinery stacks burning."""
    fill_rect(px, x + 20, y + 44, 24, 76, GREY)
    fill_rect(px, x + 54, y + 28, 24, 92, GREY)
    fill_rect(px, x + 88, y + 60, 20, 60, GREY)
    fill_rect(px, x + 12, y + 118, 104, 6, INK)
    flame(px, x + 32, y + 46, 12, RED, GOLD)
    flame(px, x + 66, y + 30, 13, ORANGE, GOLD)
    circle(px, x + 98, y + 40, 8, GREY)
    circle(px, x + 110, y + 26, 10, GREY)


def icon_mercury(px, x, y):
    """Mercury with orbit ring and a small probe."""
    ring(px, x + 62, y + 62, 52, SKY, 4)
    circle(px, x + 62, y + 62, 38, BROWN)
    circle(px, x + 48, y + 50, 8, (110, 76, 46))
    circle(px, x + 76, y + 72, 6, (110, 76, 46))
    circle(px, x + 72, y + 46, 5, (110, 76, 46))
    circle(px, x + 52, y + 76, 4, (110, 76, 46))
    fill_rect(px, x + 100, y + 8, 16, 10, RED)
    fill_rect(px, x + 92, y + 11, 8, 4, GOLD)
    fill_rect(px, x + 116, y + 11, 8, 4, GOLD)


def icon_india(px, x, y):
    """Memorial arch with a candle flame."""
    fill_rect(px, x + 14, y + 40, 16, 80, NAVY2)
    fill_rect(px, x + 90, y + 40, 16, 80, NAVY2)
    fill_rect(px, x + 14, y + 28, 92, 14, NAVY2)
    fill_rect(px, x + 8, y + 118, 104, 6, INK)
    circle(px, x + 60, y + 28, 16, NAVY2)
    flame(px, x + 60, y + 84, 12, ORANGE, GOLD)
    fill_rect(px, x + 54, y + 84, 12, 30, WHITE)
    rect_border(px, x + 54, y + 84, 12, 30, INK, 2)


ICONS = {"gulf": icon_gulf, "gaza": icon_gaza, "ukraine": icon_ukraine,
         "mercury": icon_mercury, "india": icon_india}


# -------------------------------------------------------------- panels
def panel(px, x, y, w, h, kicker, accent, icon, headline, detail):
    fill_rect(px, x, y, w, h, WHITE)
    rect_border(px, x, y, w, h, NAVY, 3)
    fill_rect(px, x, y, w, 42, accent)
    draw_text(px, x + 14, y + 11, kicker, WHITE, 2)
    ix, iy = x + 16, y + 58
    ICONS[icon](px, ix, iy)
    tx = x + 152
    tw = w - 152 - 16
    lines = wrap_text(headline, 3, tw)
    ly = y + 58
    for line in lines[:3]:
        draw_text(px, tx, ly, line, INK, 3)
        ly += 26
    dy = y + h - 88
    fill_rect(px, x + 14, dy - 8, w - 28, 2, LIGHT)
    for line in wrap_text(detail, 2, w - 28)[:3]:
        draw_text(px, x + 14, dy, line, GREY, 2)
        dy += 18


def draw_page(px):
    fill_rect(px, 0, 0, W, H, CREAM)
    # Masthead.
    fill_rect(px, 0, 0, W, 172, NAVY)
    fill_rect(px, 0, 172, W, 6, GOLD)
    kicker = "THE WORLD IN ONE DAY"
    draw_text(px, (W - text_width(kicker, 3)) // 2, 20, kicker, GOLD, 3)
    date = "26 NOVEMBER 2026"
    draw_text(px, (W - text_width(date, 7)) // 2, 52, date, WHITE, 7)
    sub = "THURSDAY  -  WORLD NEWS IN ONE IMAGE"
    draw_text(px, (W - text_width(sub, 3)) // 2, 122, sub, (190, 205, 220), 3)

    px0, py0 = 24, 194
    pw, ph, gap = 480, 288, 16
    panel(px, px0, py0, pw, ph, "GULF  -  OIL UNDER FIRE", RED, "gulf",
          "HOUTHIS CLAIM SAUDI REFINERY HIT",
          "RAS TANURA ATTACKED, FIRES SEEN FROM SPACE. TANKERS HIT BY MINES IN HORMUZ. OIL UP.")
    panel(px, px0 + pw + gap, py0, pw, ph, "GAZA  -  CEASEFIRE STRAINED",
          TEAL, "gaza",
          "ISRAEL KILLS HAMAS SECURITY CHIEF",
          "COL. MOHAMMAD ABUELOUF KILLED IN GAZA. HIS WIFE AND TWO CHILDREN ALSO KILLED.")
    panel(px, px0, py0 + ph + gap, pw, ph, "UKRAINE  -  WAR IN ITS 5TH YEAR",
          NAVY2, "ukraine",
          "UKRAINE HITS TWO RUSSIAN REFINERIES",
          "REFINERIES ABLAZE AFTER OVERNIGHT STRIKES. PUTIN VOWS RETALIATION.")
    panel(px, px0 + pw + gap, py0 + ph + gap, pw, ph,
          "SPACE  -  AFTER 8 YEARS IN FLIGHT", SKY, "mercury",
          "BEPICOLOMBO REACHES MERCURY",
          "THE EUROPEAN-JAPANESE PROBE ENTERS ORBIT AROUND THE SMALLEST PLANET.")

    # Bottom band: India + also-today.
    bx, by, bw, bh = 24, 798, 976, 202
    fill_rect(px, bx, by, bw, bh, WHITE)
    rect_border(px, bx, by, bw, bh, NAVY, 3)
    fill_rect(px, bx, by, bw, 42, NAVY)
    draw_text(px, bx + 14, by + 11, "INDIA  -  18 YEARS SINCE 26/11",
              WHITE, 2)
    # Small memorial candle at the right, clear of the divider below.
    flame(px, bx + 880, by + 108, 14, ORANGE, GOLD)
    fill_rect(px, bx + 874, by + 108, 12, 22, WHITE)
    rect_border(px, bx + 874, by + 108, 12, 22, INK, 2)
    tx = bx + 152
    draw_text(px, tx, by + 60, "MUMBAI REMEMBERS 26/11", INK, 3)
    draw_text(px, tx, by + 92,
              "INDIA MARKS CONSTITUTION DAY ON THE", GREY, 2)
    draw_text(px, tx, by + 112,
              "ANNIVERSARY OF THE MUMBAI ATTACKS.", GREY, 2)
    fill_rect(px, bx + 14, by + 132, bw - 28, 2, LIGHT)
    also = ("US PLANS NEW TARIFFS ON CHINA, EU AND BRAZIL  -  "
            "PAKISTAN'S FIRST ASTRONAUT JOINS CHINA'S SPACE STATION  -  "
            "GUKESH DRAWS GAME 2 OF THE CHESS FINAL")
    draw_text(px, bx + 14, by + 144, "ALSO TODAY:", RED, 2)
    iy = by + 162
    for line in wrap_text(also, 2, bw - 28)[:2]:
        draw_text(px, bx + 14, iy, line, INK, 2)
        iy += 18


def main():
    px = new_canvas()
    draw_page(px)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(encode_png(px))


if __name__ == "__main__":
    main()
