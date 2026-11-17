"""Thumbnail text + effects for 002 (after thumbscene.py renders th_*.png)."""
import math, random, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
D = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/mw-work/002/out"
F = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
W, H = 1280, 720; Y = (255, 214, 0); WH = (255, 255, 255); OR = (255, 92, 12)
def sparks(im, xy, n=170, seed=3, rx=420, ry=260):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); r = random.Random(seed)
    for i in range(n):
        a = r.uniform(0, 2 * math.pi); L = r.uniform(20, 260); x = xy[0] + math.cos(a) * r.uniform(30, rx); y = xy[1] + math.sin(a) * r.uniform(20, ry)
        d.line((x, y, x + math.cos(a) * L * .25, y + math.sin(a) * L * .25 + L * .08), fill=(255, r.randint(150, 220), 60, r.randint(150, 255)), width=r.choice([2, 3, 4]))
    g = ov.filter(ImageFilter.GaussianBlur(5)); im.paste(g, (0, 0), g); im.paste(ov, (0, 0), ov)
def text(im, lines, cols, x, y, size):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for l, c in zip(lines, cols):
        f = ImageFont.truetype(F, size); d.text((x, y), l, font=f, fill=c, stroke_width=int(size * .09), stroke_fill=(0, 0, 0)); y += int(size * 1.02)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.paste((0, 0, 0, 170), (0, 0), lay.split()[3]); sh = sh.filter(ImageFilter.GaussianBlur(14))
    im.paste(sh, (8, 10), sh); im.paste(lay, (0, 0), lay)
def glow(im, xy, r, col=(255, 110, 20), a=150):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(ov).ellipse((xy[0] - r, xy[1] - r, xy[0] + r, xy[1] + r), fill=col + (a,))
    ov = ov.filter(ImageFilter.GaussianBlur(r * .5)); im.alpha_composite(ov)
def base(name, bright=1.15):
    im = Image.open(f"{D}/th_{name}.png").convert("RGB"); im = ImageEnhance.Contrast(im).enhance(1.2); im = ImageEnhance.Brightness(im).enhance(bright); return im.convert("RGBA")
im = base("head"); glow(im, (880, 380), 200, a=90); sparks(im, (880, 380), n=120); text(im, ["64 KM"], [WH], 50, 30, 170); text(im, ["DURCH DIE", "ALPEN?!"], [Y, Y], 50, 470, 105)
im.convert("RGB").save(f"{D}/Thumbnail_1.jpg", quality=92)
im = base("berg", 1.1); text(im, ["1.720 m"], [WH], 50, 30, 170); text(im, ["FELS", "DARÜBER!"], [Y, Y], 50, 470, 105)
im.convert("RGB").save(f"{D}/Thumbnail_2.jpg", quality=92)
im = base("break", 1.05); glow(im, (900, 360), 200, (255, 200, 120), 90); sparks(im, (900, 360), seed=9); text(im, ["11,7 MRD. €"], [WH], 50, 30, 140); text(im, ["FÜR EIN", "LOCH?!"], [Y, Y], 50, 470, 110)
im.convert("RGB").save(f"{D}/Thumbnail_3.jpg", quality=92)
o = Image.new("RGB", (1280 * 3 + 40, 720), "white")
for i in range(3): o.paste(Image.open(f"{D}/Thumbnail_{i + 1}.jpg"), (i * 1300, 0))
o.resize((1980, 360)).save(f"{D}/thumbs_overview.jpg")
