"""
Convert a portrait photo into a smooth vector halftone SVG.
Uses a classic 45-degree angled grid (like newspaper print) for a 
highly aesthetic, professional halftone pattern.
"""
import os
import sys
import math
from PIL import Image, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-prepped.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "clash-halftone.svg")

COLS = 100
ROWS = 100
CELL_SIZE = 8

CONTRAST = 1.15
BRIGHTNESS = 1.05
GAMMA = 1.2
WHITE_FLOOR = 0.90
MAX_RADIUS = CELL_SIZE * 0.65  # allow slight overlap for darker areas

PAD = 20
TITLEBAR_H = 30
STATUS_H = 30
ART_W = COLS * CELL_SIZE
ART_H = ROWS * CELL_SIZE
CANVAS_W = ART_W + PAD * 2
CANVAS_H = TITLEBAR_H + ART_H + STATUS_H + PAD

# Angle for the halftone grid (45 degrees is classic)
ANGLE = 45

# Same aesthetic frame palette
BG = "#0a0a0c"
BG2 = "#101014"
FRAME = "#2a2d34"
TITLE_TEXT = "#7d8590"
INK = "#e8e6e1"
PROMPT = "#5ec8d8"

# ---- 1. sample the image into a grayscale grid ----------------------------
try:
    im = Image.open(SRC).convert("L")
except FileNotFoundError:
    print(f"Error: Could not find {SRC}")
    sys.exit(1)

im = ImageEnhance.Brightness(im).enhance(BRIGHTNESS)
im = ImageEnhance.Contrast(im).enhance(CONTRAST)
im = im.resize((COLS, ROWS), Image.LANCZOS)
px = im.load()

STATIC = bool(os.environ.get("STATIC"))
art_top = TITLEBAR_H + PAD * 0.35

# ---- 2. assemble SVG ------------------------------------------------------
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

# Define clip path for the scanline reveal animation
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
             f'text-anchor="start">clashlex@github: ~$ ./bankai --halftone --angle=45</text>')

# ---- 3. Render diagonal lines (45-degree angle) ------------------------------
clip_attr = ' clip-path="url(#reveal)"' if not STATIC else ''
parts.append(f'<g{clip_attr}>')

ANGLE = 45
angle_rad = math.radians(ANGLE)
cos_a = math.cos(angle_rad)
sin_a = math.sin(angle_rad)

# Draw lines in a rotated coordinate system
parts.append(f'<g transform="translate({PAD + ART_W/2:.1f}, {art_top + ART_H/2:.1f}) rotate({ANGLE})" fill="{INK}">')

MAX_THICKNESS = CELL_SIZE * 0.95  # leave a tiny gap between diagonal rows

diag = int(math.hypot(ART_W, ART_H))
grid_steps = int(diag / CELL_SIZE / 2) + 2

for gy in range(-grid_steps, grid_steps + 1):
    for gx in range(-grid_steps, grid_steps + 1):
        rx = gx * CELL_SIZE
        ry = gy * CELL_SIZE
        
        # Map rotated coordinates back to image space
        img_x = rx * cos_a - ry * sin_a + ART_W / 2.0
        img_y = rx * sin_a + ry * cos_a + ART_H / 2.0
        
        px_x = int(img_x / CELL_SIZE)
        px_y = int(img_y / CELL_SIZE)
        
        if 0 <= px_x < COLS and 0 <= px_y < ROWS:
            lum = px[px_x, px_y] / 255.0
            lum = pow(lum, GAMMA)
            
            if lum >= WHITE_FLOOR:
                continue
                
            thickness = (1.0 - lum) * MAX_THICKNESS
            if thickness < 0.5:
                continue
                
            # Draw a horizontal rectangle segment in the local rotated space
            rect_x = rx - CELL_SIZE / 2.0
            rect_y = ry - thickness / 2.0
            
            # The +0.5 width overlaps adjacent segments on the same diagonal line
            # so they merge into one seamless continuous line.
            parts.append(f'<rect x="{rect_x:.2f}" y="{rect_y:.2f}" width="{CELL_SIZE + 0.5}" height="{thickness:.2f}"/>')

parts.append('</g></g>')

# status bar with a steady blinking cursor
status_line_y = TITLEBAR_H + ART_H + PAD * 0.35
status_y = status_line_y + 19
parts.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{CANVAS_W}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>')
parts.append(f'<text x="{PAD}" y="{status_y:.1f}" fill="{TITLE_TEXT}" font-size="13">'
             f'clashlex@github:~$ whoami <tspan fill="{INK}">Ansil</tspan></text>')
parts.append(f'<rect x="{PAD+190}" y="{status_y-12:.1f}" width="8" height="14" fill="{PROMPT}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
             f'dur="1s" repeatCount="indefinite"/></rect>')

parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w") as f:
    f.write(svg)
print("wrote", OUT, len(svg), "bytes;", CANVAS_W, "x", CANVAS_H)
