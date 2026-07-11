import sys
from PIL import Image, ImageEnhance, ImageFilter

SRC = "source-prepped.png"
COLS = 100
ROWS = 53
RAMP = " .`:-=+*cs#%@"
CONTRAST = 1.05
BRIGHTNESS = 1.0
GAMMA = 1.35
WHITE_FLOOR = 0.70

im = Image.open(SRC).convert("L")
im = ImageEnhance.Brightness(im).enhance(BRIGHTNESS)
im = ImageEnhance.Contrast(im).enhance(CONTRAST)
im = im.resize((COLS, ROWS), Image.LANCZOS)
px = im.load()

for y in range(ROWS):
    chars = []
    for x in range(COLS):
        lum = px[x, y] / 255.0
        lum = pow(lum, GAMMA)
        if lum >= WHITE_FLOOR:
            chars.append(" ")
            continue
        idx = int((1.0 - lum) * (len(RAMP) - 1) + 0.5)
        idx = max(0, min(len(RAMP) - 1, idx))
        chars.append(RAMP[idx])
    print("".join(chars))
