"""
Convert a portrait photo into a 1-bit Dithered SVG using Floyd-Steinberg error diffusion.
"""
import os
import sys
from PIL import Image, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-prepped.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "clash-dither.svg")

COLS = 130
ROWS = 130
CELL_SIZE = 6

CONTRAST = 1.2
BRIGHTNESS = 1.1

PAD = 20
TITLEBAR_H = 30
STATUS_H = 30
ART_W = COLS * CELL_SIZE
ART_H = ROWS * CELL_SIZE
CANVAS_W = ART_W + PAD * 2
CANVAS_H = TITLEBAR_H + ART_H + STATUS_H + PAD

BG = "#0a0a0c"
BG2 = "#101014"
FRAME = "#2a2d34"
TITLE_TEXT = "#7d8590"
INK = "#e8e6e1"
PROMPT = "#5ec8d8"

try:
    im = Image.open(SRC).convert("L")
except FileNotFoundError:
    print(f"Error: Could not find {SRC}")
    sys.exit(1)

im = ImageEnhance.Brightness(im).enhance(BRIGHTNESS)
im = ImageEnhance.Contrast(im).enhance(CONTRAST)
im = im.resize((COLS, ROWS), Image.LANCZOS)

# Convert to float array for error diffusion
pixels = []
for y in range(ROWS):
    row = []
    for x in range(COLS):
        row.append(im.getpixel((x, y)) / 255.0)
    pixels.append(row)

# Floyd-Steinberg Error Diffusion
for y in range(ROWS):
    for x in range(COLS):
        old_val = pixels[y][x]
        # Quantize to 0 or 1
        new_val = 1.0 if old_val >= 0.5 else 0.0
        pixels[y][x] = new_val
        
        err = old_val - new_val
        
        # Diffuse the error to neighbors
        if x + 1 < COLS:
            pixels[y][x + 1] += err * 7.0 / 16.0
        if y + 1 < ROWS:
            if x - 1 >= 0:
                pixels[y + 1][x - 1] += err * 3.0 / 16.0
            pixels[y + 1][x] += err * 5.0 / 16.0
            if x + 1 < COLS:
                pixels[y + 1][x + 1] += err * 1.0 / 16.0

STATIC = bool(os.environ.get("STATIC"))
art_top = TITLEBAR_H + PAD * 0.35

parts = []
parts.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
    f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, '
    f'Menlo, Consolas, monospace">'
)
parts.append('<defs>'
             f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
             f'</linearGradient>')

if not STATIC:
    parts.append(f'<clipPath id="reveal">')
    parts.append(f'<rect x="0" y="0" width="{CANVAS_W}" height="0">')
    parts.append(f'<animate attributeName="height" from="0" to="{CANVAS_H}" begin="0s" '
                 f'dur="1.5s" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1"/>')
    parts.append(f'</rect></clipPath>')

parts.append('</defs>')

parts.append(f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/>')
parts.append(f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" '
             f'fill="none" stroke="{FRAME}" stroke-width="1"/>')

parts.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')
win_stroke = "#7d8590"
parts.append(f'<g stroke="{win_stroke}" stroke-width="1.2" stroke-linecap="round" fill="none">')
parts.append(f'<line x1="{CANVAS_W - 100}" y1="{TITLEBAR_H/2 + 4}" x2="{CANVAS_W - 90}" y2="{TITLEBAR_H/2 + 4}"/>')
parts.append(f'<rect x="{CANVAS_W - 65}" y="{TITLEBAR_H/2 - 4}" width="10" height="10" rx="1"/>')
parts.append(f'<path d="M{CANVAS_W - 30},{TITLEBAR_H/2 - 4} L{CANVAS_W - 20},{TITLEBAR_H/2 + 4} M{CANVAS_W - 20},{TITLEBAR_H/2 - 4} L{CANVAS_W - 30},{TITLEBAR_H/2 + 4}"/>')
parts.append('</g>')
parts.append(f'<text x="{PAD}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
             f'text-anchor="start">clashlex@github: ~$ ./bankai --dither</text>')

# ---- Render dithered pixels -----------------------------------------------
clip_attr = ' clip-path="url(#reveal)"' if not STATIC else ''
parts.append(f'<g fill="{INK}"{clip_attr}>')

# The SVG is light ink on dark background, so draw INK where pixels are > 0.5 (bright areas)
# Note: we add +0.5 to width/height to avoid tiny rendering gaps between adjacent rectangles
for y in range(ROWS):
    for x in range(COLS):
        if pixels[y][x] > 0.5:
            cx = PAD + x * CELL_SIZE
            cy = art_top + y * CELL_SIZE
            parts.append(f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{CELL_SIZE+0.5}" height="{CELL_SIZE+0.5}" />')

parts.append('</g>')

status_line_y = TITLEBAR_H + ART_H + PAD * 0.35
status_y = status_line_y + 19
parts.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{CANVAS_W}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>')
parts.append(f'<text x="{PAD}" y="{status_y:.1f}" fill="{TITLE_TEXT}" font-size="13">'
             f'clashlex@github:~$ whoami <tspan fill="{INK}">Ansil  </tspan></text>')
parts.append(f'<rect x="{PAD+190}" y="{status_y-12:.1f}" width="8" height="14" fill="{PROMPT}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
             f'dur="1s" repeatCount="indefinite"/></rect>')

parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w") as f:
    f.write(svg)
print("wrote", OUT, len(svg), "bytes;", CANVAS_W, "x", CANVAS_H)
