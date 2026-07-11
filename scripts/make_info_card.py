"""
Build a neofetch-style info card SVG to sit to the RIGHT of the ASCII
portrait: colored key/value rows for role, leadership, tech stack, and
highlights -- NOT GitHub stats (the contribution graph covers those).

Static content, hand-authored below. Lines fade/slide in on a short stagger so
it feels like the panel is printing alongside the portrait. STATIC=1 emits the
frozen state for Quick Look previews.
"""
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "info-card.svg")
STATIC = bool(os.environ.get("STATIC"))

W, H = 480, 430
PAD = 20
TITLEBAR_H = 30
KEY_X = PAD
VAL_X = PAD + 92
LINE_H = 20.5

# Bleach-tinged terminal palette (matches clash-ascii.svg)
BG = "#0a0a0c"
BG2 = "#101014"
FRAME = "#2a2d34"
MUTED = "#7d8590"
INK = "#e8e6e1"
KEY = "#e8a33d"       # amber keys
SECTION = "#5ec8d8"   # reiatsu-blue section headers
GREEN = "#3fb950"
ACCENT = "#c73a3a"    # a single hollow-mask red accent, used sparingly

# content model: tuples describing each row
# ("host",)                    -> "clashlex@github" + rule
# ("kv", key, value)           -> amber key + light value
# ("sec", title)               -> blue "— title —" rule
# ("bul", text)                -> green dot + light text
# ("gap",)                     -> vertical space
ROWS = [
    ("host",),
    ("kv", "Now", "2nd-yr B.Tech CSE, KMEA Engg. College"),
    ("kv", "Also", "Campus Mantri @ GeeksforGeeks"),
    ("kv", "Also", "Google Student Ambassador"),
    ("gap",),
    ("sec", "Stack"),
    ("kv", "Frontend", "HTML, CSS, JS, React"),
    ("kv", "Backend", "Python, Node, Supabase"),
    ("kv", "Other", "WebGL/Canvas, MediaPipe, "),
    ("gap",),
    ("sec", "Building"),
    ("bul", "Clean AI -- Smart Storage Cleansing AI"),
    ("bul", "Cyber Slide -- Interactive Game"),
    ("bul", "AQUA SENSE -- water quality monitoring system"),
    ("bul", "RESILII TWIN -- Industrial Safety DigitalTwin"),
]


def esc(s):
    return html.escape(s)


def rise(inner, i):
    """fade + slight upward slide, staggered by row index; freezes visible."""
    if STATIC:
        return f"<g>{inner}</g>"
    delay = 0.15 + i * 0.06
    return (f'<g opacity="0" transform="translate(0,5)">{inner}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" '
            f'begin="{delay:.2f}s" dur="0.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>')


parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    '<defs>'
    f'<linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#ibg)"/>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]
win_stroke = "#7d8590"
parts.append(f'<g stroke="{win_stroke}" stroke-width="1.2" stroke-linecap="round" fill="none">')
parts.append(f'<line x1="{W - 100}" y1="{TITLEBAR_H/2 + 4}" x2="{W - 90}" y2="{TITLEBAR_H/2 + 4}"/>')
parts.append(f'<rect x="{W - 65}" y="{TITLEBAR_H/2 - 4}" width="10" height="10" rx="1"/>')
parts.append(f'<path d="M{W - 30},{TITLEBAR_H/2 - 4} L{W - 20},{TITLEBAR_H/2 + 4} M{W - 20},{TITLEBAR_H/2 - 4} L{W - 30},{TITLEBAR_H/2 + 4}"/>')
parts.append('</g>')
parts.append(f'<text x="{PAD}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
             f'text-anchor="start">clashlex@github: ~$ neofetch</text>')

y = TITLEBAR_H + 30
for i, row in enumerate(ROWS):
    kind = row[0]
    if kind == "gap":
        y += LINE_H * 0.5
        continue
    if kind == "host":
        inner = (f'<text x="{KEY_X}" y="{y:.1f}" font-size="14" font-weight="700">'
                 f'<tspan fill="{ACCENT}">clash</tspan><tspan fill="{MUTED}">@</tspan>'
                 f'<tspan fill="{SECTION}">github</tspan></text>'
                 f'<line x1="{KEY_X+108}" y1="{y-4:.1f}" x2="{W-PAD}" y2="{y-4:.1f}" '
                 f'stroke="{FRAME}" stroke-opacity="0.8"/>')
    elif kind == "sec":
        title = esc(row[1])
        inner = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{SECTION}" font-size="12.5" font-weight="700">'
                 f'&#8212; {title}</text>'
                 f'<line x1="{KEY_X + 12 + len(row[1])*8}" y1="{y-4:.1f}" x2="{W-PAD}" y2="{y-4:.1f}" '
                 f'stroke="{FRAME}" stroke-opacity="0.8"/>')
    elif kind == "kv":
        key, val = esc(row[1]), esc(row[2])
        inner = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">{key}</text>'
                 f'<text x="{VAL_X}" y="{y:.1f}" fill="{INK}" font-size="12">{val}</text>')
    elif kind == "bul":
        txt = esc(row[1])
        inner = (f'<circle cx="{KEY_X+3}" cy="{y-4:.1f}" r="2.5" fill="{GREEN}"/>'
                 f'<text x="{KEY_X+14}" y="{y:.1f}" fill="{INK}" font-size="12">{txt}</text>')
    else:
        continue
    parts.append(rise(inner, i))
    y += LINE_H

parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w") as f:
    f.write(svg)
print("wrote", OUT, len(svg), "bytes;", W, "x", H, "content_bottom", round(y))
