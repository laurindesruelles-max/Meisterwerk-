"""Thumbnails 004: dunkel, glühend, EIN Motiv, 2 Zeilen weiß/gelb mit dicker Kontur"""
import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
WK = "/home/claude/mw-work/004"; F = "/usr/share/fonts/opentype/inter/"
W, H = 1280, 720; Y = (255, 214, 0); WH = (255, 255, 255)
def sparks(im, xy, n=140, seed=3, spread=380):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); r = random.Random(seed)
    for i in range(n):
        a = r.uniform(-math.pi, 0); L = r.uniform(20, 200); x = xy[0] + math.cos(a) * r.uniform(20, spread); y = xy[1] + math.sin(a) * r.uniform(10, spread * .6)
        d.line((x, y, x + math.cos(a) * L * .25, y + math.sin(a) * L * .25 + L * .08), fill=(255, r.randint(150, 220), 60, r.randint(150, 255)), width=r.choice([2, 3, 4]))
    g = ov.filter(ImageFilter.GaussianBlur(5)); im.alpha_composite(g); im.alpha_composite(ov)
def text(im, lines, cols, x, y, size):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = ImageFont.truetype(F + "InterDisplay-Black.otf", size)
    for l, c in zip(lines, cols):
        d.text((x, y), l, font=f, fill=c, stroke_width=int(size * .09), stroke_fill=(0, 0, 0)); y += int(size * 1.02)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.paste((0, 0, 0, 170), (0, 0), lay.split()[3]); sh = sh.filter(ImageFilter.GaussianBlur(14))
    im.alpha_composite(sh, (8, 10)); im.alpha_composite(lay)
def base(p, bright=1.1, crop=None):
    im = Image.open(p).convert("RGB")
    if crop: im = im.crop(crop)
    im = im.resize((W, H), Image.LANCZOS); im = ImageEnhance.Contrast(im).enhance(1.12); im = ImageEnhance.Brightness(im).enhance(bright)
    return im.convert("RGBA")
# 1: glühender Kolben
im = base(f"{WK}/r/thumb2_a/f_0001.png", 1.05); sparks(im, (900, 230))
text(im, ["ABSICHTLICH"], [WH], 40, 40, 128); text(im, ["NICHT RUND?!"], [Y], 40, 560, 118)
im.convert("RGB").save(f"{WK}/Thumbnail_1.jpg", quality=92)
# 2: heißer Kolben unter der Messuhr
im = base(f"{WK}/r/064_messuhr_heiss/f_0100.png", 1.05, crop=(60, 0, 960, 506))
text(im, ["12 TONNEN"], [WH], 40, 30, 130); text(im, ["AUF 200 GRAMM?!"], [Y], 40, 575, 104)
im.convert("RGB").save(f"{WK}/Thumbnail_2.jpg", quality=92)
# 3: Kolben im Zylinder mit Flamme
im = base(f"{WK}/r/thumb2_c/f_0001.png", 1.1); sparks(im, (1000, 120), n=90, seed=7, spread=260)
text(im, ["WARUM IST ER"], [WH], 40, 60, 116); text(im, ["SCHIEF?!"], [Y], 40, 190, 150)
im.convert("RGB").save(f"{WK}/Thumbnail_3.jpg", quality=92)
o = Image.new("RGB", (1280 * 3 + 40, 720), "white")
for i in range(3): o.paste(Image.open(f"{WK}/Thumbnail_{i + 1}.jpg"), (i * 1300, 0))
o.resize((1980, 360)).save(f"{WK}/thumbs.jpg")
