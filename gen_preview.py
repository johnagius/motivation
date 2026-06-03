#!/usr/bin/env python3
"""Generate preview.png — the link-preview card shown when the book is shared
(e.g. on WhatsApp status). 1200x630, matching the moon-book aesthetic."""
import math, random, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1200, 630
random.seed(12)

# ---- background: deep space vertical gradient ----
top = (16, 22, 44)      # deep blue near the top
bot = (5, 7, 15)        # void
grad = Image.new("RGB", (1, H))
for y in range(H):
    t = y / (H - 1)
    grad.putpixel((0, y), tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
img = grad.resize((W, H)).convert("RGB")
draw = ImageDraw.Draw(img, "RGBA")

# subtle warm glow lower-left
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([-200, H - 260, 420, H + 260], fill=(232, 184, 95, 26))
glow = glow.filter(ImageFilter.GaussianBlur(120))
img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
draw = ImageDraw.Draw(img, "RGBA")

# ---- stars ----
for _ in range(160):
    x, y = random.randint(0, W), random.randint(0, int(H * 0.85))
    r = random.choice([0, 0, 0, 1, 1, 2]) / 2 + 0.3
    a = random.randint(60, 200)
    draw.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))

# ---- moon (right side) with glow ----
cx, cy, R = 980, 250, 120
halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
hd = ImageDraw.Draw(halo)
hd.ellipse([cx - R * 2.1, cy - R * 2.1, cx + R * 2.1, cy + R * 2.1], fill=(232, 184, 95, 60))
halo = halo.filter(ImageFilter.GaussianBlur(90))
img = Image.alpha_composite(img.convert("RGBA"), halo).convert("RGB")
draw = ImageDraw.Draw(img, "RGBA")

moon = Image.new("RGBA", (R * 2, R * 2), (0, 0, 0, 0))
md = ImageDraw.Draw(moon)
lx, ly = R * 0.72, R * 0.62          # light origin
for yy in range(R * 2):
    for xx in range(R * 2):
        dx, dy = xx - R, yy - R
        if dx * dx + dy * dy <= R * R:
            d = math.hypot(xx - lx, yy - ly) / (R * 1.7)
            d = min(max(d, 0), 1)
            c = (int(253 - 153 * d), int(251 - 156 * d), int(243 - 163 * d))
            md.point((xx, yy), fill=c + (255,))
# a few craters
for (mx, my, mr) in [(-40, -30, 14), (28, 26, 10), (10, -36, 7), (-18, 40, 9)]:
    md.ellipse([R + mx - mr, R + my - mr, R + mx + mr, R + my + mr], fill=(111, 107, 94, 70))
img.paste(moon, (cx - R, cy - R), moon)
draw = ImageDraw.Draw(img, "RGBA")

# ---- fonts ----
def F(path, size):
    return ImageFont.truetype(path, size)
SERIF   = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS    = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

GOLD = (232, 184, 95)
CREAM = (243, 236, 217)
STEEL = (125, 147, 184)

def text_track(d, xy, s, font, fill, tracking=0):
    x, y = xy
    for ch in s:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + tracking

x0 = 90
# eyebrow
text_track(draw, (x0, 110), "AN ILLUSTRATED READING", F(SANS, 22), GOLD, 6)
# title
tf = F(SERIF, 96)
draw.text((x0, 168), "We Choose", font=tf, fill=CREAM)
draw.text((x0, 268), "to Go to the", font=tf, fill=CREAM)
draw.text((x0, 368), "Moon", font=F(SERIF_I, 96), fill=GOLD)
# rule
draw.rectangle([x0, 492, x0 + 70, 494], fill=GOLD)
# byline
text_track(draw, (x0, 520), "JOHN F. KENNEDY  ·  RICE UNIVERSITY, 1962",
           F(SANS, 22), STEEL, 3)

img.convert("RGB").save(os.path.join(HERE, "preview.png"), "PNG")
print("wrote preview.png")
