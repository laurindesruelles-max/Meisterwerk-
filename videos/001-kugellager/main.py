"""Meisterwerk pilot – main part compositor. Reuses helpers from intro.py."""
import os, sys, math, random, json, re, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.argv = [sys.argv[0]] + ["none"] + sys.argv[1:]
import intro as I
from intro import W, H, FPS, BG, font, ease, eout, img, kenburns, typed, typed_sfx, big_number, pill, brand, measure, vignette_punch, ORANGE, INK, GREY, F, dur
sys.argv = [sys.argv[0]] + sys.argv[2:]
D = I.D
random.seed(11)

# ---------- clips ----------
NFR = {}
_cache = {}
def nframes(clip):
    if clip not in NFR:
        d = f"{D}/r2/{clip}" if os.path.isdir(f"{D}/r2/{clip}") else f"{D}/r_{clip}"
        NFR[clip] = (d, len([f for f in os.listdir(d) if f.startswith("f_")]))
    return NFR[clip]
def frame_rgba(clip, idx):
    d, n = nframes(clip); idx = int(min(max(idx, 1), n)); k = (clip, idx)
    if k not in _cache:
        if len(_cache) > 40: _cache.clear()
        _cache[k] = Image.open(f"{d}/f_{idx:04d}.png").convert("RGBA").resize((W, H), Image.LANCZOS)
    return _cache[k]
SHADOW = I.SHADOW
def clip(name, pos, zoom=1.0, shadow=True, cx=.5, cy=.5):
    a = frame_rgba(name, math.floor(pos)); f = pos - math.floor(pos)
    if f > .05: a = Image.blend(a, frame_rgba(name, math.floor(pos) + 1), f)
    if name == "ofen":
        h = min(1, max(0, (pos - 1) / 39)) * (1 - min(1, max(0, (pos - 52) / 16)))
        if h > 0.01:
            r, g, b, al = a.split()
            hot = Image.merge("RGBA", (Image.new("L", a.size, 255), Image.new("L", a.size, 120), Image.new("L", a.size, 30), al))
            lum = a.convert("L").point(lambda x: min(255, int(x * 1.2)))
            hot2 = Image.merge("RGBA", (lum.point(lambda x: min(255, 120 + x)), lum.point(lambda x: int(x * .55)), lum.point(lambda x: int(x * .12)), al))
            mask = al.point(lambda x: int(x * h * .85))
            # keep the oil box / plate darker: only bright parts glow
            a = Image.composite(hot2, a, Image.composite(mask, Image.new("L", a.size, 0), lum.point(lambda x: 255 if x > 140 else 0)))
            glow = Image.merge("RGBA", (Image.new("L", a.size, 255), Image.new("L", a.size, 110), Image.new("L", a.size, 20), lum.point(lambda x: int(min(255, max(0, x - 120)) * h))))
            glow = glow.filter(ImageFilter.GaussianBlur(28)); a = Image.alpha_composite(a, glow)
    im = BG.copy()
    if shadow: im = Image.composite(Image.new("RGB", (W, H), (150, 145, 138)), im, SHADOW)
    if zoom > 1:
        w, h = int(W * zoom), int(H * zoom); l = int((w - W) * cx); t = int((h - H) * cy)
        a = a.resize((w, h), Image.BICUBIC).crop((l, t, l + W, t + H))
    elif zoom < 1:
        w, h = int(W * zoom), int(H * zoom); s = a.resize((w, h), Image.BICUBIC)
        a = Image.new("RGBA", (W, H), (0, 0, 0, 0)); a.paste(s, ((W - w) // 2, (H - h) // 2 + int(H * .04)))
    im.paste(a, (0, 0), a)
    return im
def still(name, t, T, z0=1.0, z1=1.1, cx0=.5, cy0=.5, cx1=.5, cy1=.5):
    d, n = nframes(name)
    key = ("still", name)
    if key not in _cache:
        fr = Image.open(f"{d}/f_0001.png").convert("RGBA"); im = BG.copy(); im.paste(fr.resize((W, H), Image.LANCZOS), (0, 0), fr.resize((W, H), Image.LANCZOS)); _cache[key] = im
    return kenburns(_cache[key], t, T, z0, z1, cx0, cy0, cx1, cy1)
def pw(vt, pts):
    """piecewise-linear map vt -> frame from [(vt, frame), ...]"""
    if vt <= pts[0][0]: return pts[0][1]
    for (a, fa), (b, fb) in zip(pts, pts[1:]):
        if vt <= b: return fa + (fb - fa) * (vt - a) / (b - a)
    return pts[-1][1]

# ---------- effects ----------
def sparks(im, t, t0, t1, xy, n=70, spread=(-2.6, -0.3), speed=900, seed=1):
    if t < t0 or t > t1 + .6: return
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); rnd = random.Random(seed)
    for i in range(n * 3):
        born = t0 + rnd.random() * (t1 - t0); age = t - born
        if age < 0 or age > .45: continue
        a = rnd.uniform(*spread); v = speed * rnd.uniform(.4, 1.2)
        x = xy[0] + math.cos(a) * v * age; y = xy[1] + math.sin(a) * v * age + 1400 * age * age
        x2 = x - math.cos(a) * 18; y2 = y - math.sin(a) * 18 - 30 * age
        al = int(255 * (1 - age / .45))
        d.line((x2, y2, x, y), fill=(255, 190, 70, al), width=3)
    glow = ov.filter(ImageFilter.GaussianBlur(4))
    im.paste(glow, (0, 0), glow); im.paste(ov, (0, 0), ov)
def shake(im, t, t0, amp=22, d=.4):
    x = t - t0
    if 0 <= x < d:
        a = amp * (1 - x / d); dx = int(a * math.sin(x * 90)); dy = int(a * math.cos(x * 70))
        return im.transform(im.size, Image.AFFINE, (1, 0, dx, 0, 1, dy), resample=Image.BILINEAR, fillcolor=(236, 232, 226))
    return im
def flash_white(im, t, t0, d=.18):
    x = t - t0
    if 0 <= x < d: return Image.blend(im, Image.new("RGB", (W, H), (255, 255, 255)), .6 * (1 - x / d))
    return im
def chapter_card(t, num, title):
    im = BG.copy(); d = ImageDraw.Draw(im); a = eout(t / .4)
    d.text((W / 2, H / 2 - 120), f"KAPITEL {num}", font=font(F + "Inter-Bold.otf", 44), fill=tuple(int(c * a + 244 * (1 - a)) for c in GREY), anchor="mm")
    f = font(F + "InterDisplay-Black.otf", 170 * (.92 + .08 * a)); d.text((W / 2, H / 2 + 10), title.upper(), font=f, fill=INK, anchor="mm")
    d.rounded_rectangle((W / 2 - 140 * a, H / 2 + 120, W / 2 + 140 * a, H / 2 + 134), 7, fill=ORANGE)
    return im
def callout(im, t, t0, xy, text, side=1, length=260):
    if t < t0: return
    p = eout((t - t0) / .35); d = ImageDraw.Draw(im)
    d.ellipse((xy[0] - 9, xy[1] - 9, xy[0] + 9, xy[1] + 9), fill=ORANGE)
    ex = xy[0] + side * length * p; d.line((xy[0], xy[1], ex, xy[1]), fill=ORANGE, width=4)
    if p > .7:
        f = font(F + "Inter-Bold.otf", 44); tw = d.textlength(text, font=f)
        d.text((ex + 16 if side > 0 else ex - 16 - tw, xy[1] - 27), text, font=f, fill=INK)
def ellipse_wobble(im, t, t0, c=(W / 2, H / 2 - 20), r=470):
    if t < t0: return
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    k = .06 * ease((t - t0) / .8) * (1 + .3 * math.sin((t - t0) * 6))
    d.ellipse((c[0] - r * (1 + k), c[1] - r * (1 - k), c[0] + r * (1 + k), c[1] + r * (1 - k)), outline=ORANGE + (255,), width=6)
    d.ellipse((c[0] - r, c[1] - r, c[0] + r, c[1] + r), outline=(28, 28, 32, 120), width=2)
    im.paste(ov, (0, 0), ov)
def scanline(im, t, t0, t1):
    if t < t0 or t > t1: return
    y = 120 + (H - 240) * ((t - t0) / (t1 - t0) * 2 % 1)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    d.rectangle((0, y - 40, W, y + 40), fill=ORANGE + (40,)); d.line((0, y, W, y), fill=ORANGE + (230,), width=4)
    im.paste(ov, (0, 0), ov)
def waveform(im, t, t0, spike_at):
    if t < t0: return
    a = ease((t - t0) / .4)
    x0, y0, w0, h0 = 110, 700, 760, 260
    bx = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(bx)
    bd.rounded_rectangle((x0, y0, x0 + w0, y0 + h0), 22, fill=(255, 255, 255, int(235 * a))); im.paste(bx, (0, 0), bx)
    d = ImageDraw.Draw(im); d.text((x0 + 28, y0 + 18), "KÖRPERSCHALL", font=font(F + "Inter-Bold.otf", 30), fill=GREY)
    pts = []; rnd = random.Random(3)
    for i in range(240):
        x = x0 + 28 + i * (w0 - 56) / 239; tt = t * 3 + i * .08
        amp = 18 + 8 * math.sin(tt * 3.1)
        sp = 0
        if t > spike_at:
            for k in range(3):
                c = ((t - spike_at) * 160 + k * 70) % (w0 - 56)
                if abs((x - x0 - 28) - c) < 6: sp = 85
        y = y0 + 150 + amp * math.sin(tt * 7.3 + rnd.random()) + sp * (1 if i % 2 else -1)
        pts.append((x, y))
    d.line(pts, fill=ORANGE if t > spike_at else INK, width=3)
    if t > spike_at + .3:
        d.text((x0 + w0 - 28, y0 + 18), "FEHLER ERKANNT", font=font(F + "Inter-Bold.otf", 30), fill=ORANGE, anchor="ra")

# ---------- timeline ----------
S = json.load(open(f"{D}/main_script.json"))
VO = {x["n"]: f"{D}/vo2/{x['n']}.mp3" for x in S}
L = {n: dur(p) for n, p in VO.items()}
CH = {201: (2, "Die Kugel"), 301: (3, "Die Ringe"), 401: (4, "Der Käfig"), 501: (5, "Die Montage")}
PAD = {105: .5, 106: .4, 205: .4, 212: .4, 306: .4, 402: .4, 503: .3, 506: .4, 603: 1.5}
segs = []; t = 0; vo_at = {}
segs.append(("card1", t, 2.2)); t += 2.2
for x in S:
    n = x["n"]
    if n in CH: segs.append((f"card{CH[n][0]}", t, 2.2)); t += 2.2
    lead = .15; vo_at[n] = t + lead
    d_ = lead + L[n] + PAD.get(n, .15)
    segs.append((n, t, d_)); t += d_
TOTAL = t
print("main total", round(TOTAL, 1))
def seg_at(t):
    for s in reversed(segs):
        if s[1] <= t: return s
    return segs[0]

def frame(t):
    sid, s0, T = seg_at(t); lt = t - s0
    if isinstance(sid, str):
        num = int(sid[4:]); title = {1: "Die Erfindung", 2: "Die Kugel", 3: "Die Ringe", 4: "Der Käfig", 5: "Die Montage"}[num]
        return chapter_card(lt, num, title)
    v = vo_at[sid]; vt = t - v
    im = None
    if sid == 101:
        im = kenburns(img("bomber_town"), lt, T, 1.6, 1.75, .5, 1.0, .55, 1.0)
        typed(im, t, v + .2, ["SCHWEINFURT", "UM 1880"], (120, 120))
        pill(im, t, v + 3.2, "FRIEDRICH FISCHER", (120, 330), size=50)
        pill(im, t, v + 3.6, "SCHLOSSER & DREHER", (120, 440), size=40, color=GREY)
    elif sid == 102:
        if vt < 3.8: im = kenburns(img("bike"), lt, 4.0, 1.0, 1.12)
        else:
            im = clip("kugel", 1 + (vt - 3.8) * 24 * .5); im = vignette_punch(im, vt, 3.8)
            typed(im, t, v + 4.0, ["ENGLAND:", "HANDARBEIT AN DER DREHBANK"], (110, 110), size=40)
            for i, (w_, at) in enumerate([("UNGENAU", 8.3), ("TEUER", 9.55), ("BRECHEN", 10.4)]):
                pill(im, t, v + at, w_, (1380, 600 + i * 120), size=52, color=ORANGE)
    elif sid == 103:
        if vt < 5.5:
            im = BG.copy(); big_number(im, t, v + 2.3, 1883, lambda x: f"{int(1860 + (x - 1860) if x > 1860 else 1860)}", (W / 2, H / 2), size=260, dur_c=1.0)
            if vt < 2.3: pill(im, t, v + .1, "JAHRELANGES TÜFTELN", (W / 2 - 330, H / 2 - 40), size=56)
        else:
            im = clip("muehle", 1 + (vt - 5.5) * 24 * .6); im = vignette_punch(im, vt, 5.5)
            for i, (w_, at) in enumerate([("GLEICH GROSS", 9.0), ("WIRKLICH RUND", 10.3), ("IN MASSEN", 11.7)]):
                pill(im, t, v + at, w_, (110, 150 + i * 115), size=52)
    elif sid == 104:
        if vt < 8.0:
            im = clip("muehle", 1 + (8.0 * .6 * 24) * 0 + (vt + 8.0 * 0) * 24 * .45 + 20)
            pill(im, t, v + 2.7, "OBEN: STEHT", (110, 150), size=48); pill(im, t, v + 3.6, "UNTEN: DREHT SICH", (110, 260), size=48)
        else:
            im = clip("kugel", 1 + (vt - 8.0) * 24 * .8); im = vignette_punch(im, vt, 8.0)
            pill(im, t, v + 8.3, "DREHACHSE WECHSELT STÄNDIG", (110, 150), size=50)
    elif sid == 105:
        im = clip("kugel", 40); measure(im, t, v + .1)
        big_number(im, t, v + .9, 2, lambda x: f"{x / 100:.2f} mm".replace(".", ","), (W / 2, 110), size=96, dur_c=.7, panel=True)
        pill(im, t, v + 4.0, "SENSATION · 1883", (110, 880), size=46, color=ORANGE)
    elif sid == 106:
        if vt < 9.9:
            im = kenburns(img("map"), lt, 10.0, 1.1, 1.45, .5, .55, .6, .62)
            pill(im, t, v + 1.6, "F A G", (110, 150), size=60, color=ORANGE)
            pill(im, t, v + 3.7, "+ WEITERE KUGELFABRIKEN", (110, 270), size=48)
            typed(im, t, v + 7.2, ["SCHWEINFURT =", "STADT DER WÄLZLAGER"], (1080, 800), size=42)
        else:
            im = kenburns(img("bomber_sky"), vt - 9.9, T - 9.9, 1.05, 1.2); im = vignette_punch(im, vt, 9.9)
            typed(im, t, v + 10.2, ["1943"], (120, 120), size=60)
    elif sid == 107:
        im = still("viele", lt, T, 1.05, 1.25, .3, .4, .6, .5)
        pill(im, t, v + .3, "BIS HEUTE", (110, 150), size=56, color=ORANGE)
    elif sid == 201:
        im = still("draht", lt, T, 1.0, 1.15)
        typed(im, t, v + 2.6, ["WÄLZLAGERSTAHL", "100Cr6"], (110, 110), size=46)
        pill(im, t, v + 6.5, "≈ 1 % KOHLENSTOFF", (110, 330), size=48); pill(im, t, v + 8.6, "≈ 1,5 % CHROM", (110, 450), size=48)
    elif sid == 202:
        im = clip("schneiden", 1 + vt * 24 * .45, zoom=1.3, cx=.15, cy=.12)
        pill(im, t, v + 6.0, "ROHLING", (110, 150), size=56, color=ORANGE)
    elif sid == 203:
        pos = pw(vt, [(0, 1), (5.0, 1), (6.4, 34), (10.5, 96)])
        im = clip("stauchen", pos, zoom=1 + .05 * ease(vt / 5))
        im = flash_white(im, t, v + 6.4); im = shake(im, t, v + 6.4)
        typed(im, t, v + 2.3, ["KALTSTAUCHEN"], (110, 110), size=50)
        big_number(im, t, v + 8.5, 20, lambda x: f"10–{int(round(x))} t", (W / 2, 900), size=110, dur_c=.6, panel=True)
    elif sid == 204:
        pos = pw(vt, [(0, 20), (1.0, 34), (1.6, 34), (1.7, 22), (2.4, 34), (3.0, 34), (3.1, 22), (3.8, 34), (6.2, 60)])
        im = clip("stauchen", pos)
        for at in (1.0, 2.4, 3.8): im = shake(im, t, v + at, amp=14, d=.3)
        pill(im, t, v + 3.0, "GEHÖRSCHUTZ PFLICHT", (110, 150), size=52, color=ORANGE)
    elif sid == 205:
        im = clip("stauchen", pw(vt, [(0, 60), (7.7, 96)]), zoom=1.15)
        callout(im, t, v + 3.0, (W / 2 + 30, H / 2 - 20), "GRAT", side=1, length=320)
    elif sid == 206:
        im = clip("muehle", 1 + vt * 24 * .4)
        pill(im, t, v + 2.3, "ENTGRATEN", (110, 150), size=56, color=ORANGE)
        pill(im, t, v + 5.2, "OBEN: STEHT", (110, 270), size=46); pill(im, t, v + 6.4, "UNTEN: DREHT SICH", (110, 370), size=46)
        pill(im, t, v + 8.2, "FISCHERS PRINZIP", (110, 470), size=46)
    elif sid == 207:
        im = clip("kugel", 1 + vt * 24 * .6, zoom=1.05)
        pill(im, t, v + 2.0, "RUND – ABER NOCH WEICH", (110, 150), size=54, color=ORANGE)
    elif sid == 208:
        im = clip("ofen", pw(vt, [(0, 1), (2.4, 40), (4.9, 48), (5.6, 64), (8.2, 80)]))
        big_number(im, t, v + 2.4, 800, lambda x: f"> {int(round(x))} °C", (W / 2, 120), size=100, dur_c=.8, panel=True)
        pill(im, t, v + 4.6, "ÖL- ODER SALZBAD", (110, 880), size=50)
    elif sid == 209:
        im = clip("ofen", pw(vt, [(0, 80), (6.8, 96)]), zoom=1.05)
        pill(im, t, v + 3.4, "HART & VERSCHLEISSFEST", (110, 150), size=52, color=ORANGE)
        pill(im, t, v + 4.6, "62–65 HRC", (110, 270), size=48)
    elif sid == 210:
        if vt < 5.1:
            im = clip("kugel", 40); ellipse_wobble(im, t, v + 2.1)
            pill(im, t, v + 2.2, "VERZUG", (110, 150), size=56, color=ORANGE)
        else:
            im = clip("muehle", 1 + (vt - 5.1) * 24 * .45 + 30); im = vignette_punch(im, vt, 5.1)
            sparks(im, t, v + 5.3, v + 12.8, (W * .70, H * .52), seed=4); sparks(im, t, v + 5.5, v + 12.8, (W * .33, H * .56), spread=(-2.9, -.6), seed=9)
            pill(im, t, v + 7.0, "SCHLEIFEN", (110, 150), size=56, color=ORANGE)
            pill(im, t, v + 10.6, "WENIGE TAUSENDSTEL mm", (110, 270), size=48)
    elif sid == 211:
        im = clip("kugel", 1 + vt * 24 * .35, zoom=1.0 + .06 * ease(vt / T))
        if vt > 2.4 and vt < 11:
            gx = int(-400 + (W + 800) * ((vt - 2.4) / 3.0 % 1))
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(ov).polygon([(gx, 0), (gx + 140, 0), (gx - 160, H), (gx - 300, H)], fill=(255, 255, 255, 70))
            ov = ov.filter(ImageFilter.GaussianBlur(30)); im.paste(ov, (0, 0), ov)
        pill(im, t, v + 2.5, "LÄPPEN", (110, 150), size=56, color=ORANGE)
        pill(im, t, v + 3.6, "GUSSEISEN + SCHLEIFPASTE", (110, 270), size=46)
        big_number(im, t, v + 11.4, 1, lambda x: "< 0,0001 mm", (W / 2, 900), size=100, dur_c=.3, panel=True)
    elif sid == 212:
        im = clip("kugel", 30); scanline(im, t, v + .3, v + 5.4)
        for i, (w_, at) in enumerate([("GRÖSSE ✓", 3.2), ("RUNDHEIT ✓", 4.0), ("RISSE ✓", 4.8)]):
            pill(im, t, v + at, w_, (110, 150 + i * 115), size=50)
        if vt > 5.7:
            pill(im, t, v + 5.8, "1 FEHLER = LAGER KAPUTT", (110, 520), size=50, color=ORANGE)
    elif sid == 301:
        im = clip("lager", 4, zoom=.85)
        pill(im, t, v + 1.9, "AUSSENRING", (110, 150), size=50); pill(im, t, v + 2.9, "INNENRING", (110, 260), size=50)
    elif sid == 302:
        if vt < 4.2:
            im = clip("ofen", 40, zoom=1.35, cx=.25, cy=.4); pill(im, t, v + 1.4, "STAHLROHR ODER SCHMIEDETEIL", (110, 150), size=46)
        else:
            im = clip("drehen", 1 + (vt - 4.2) * 24 * .75, zoom=1.35, cx=.5, cy=.3); im = vignette_punch(im, vt, 4.2)
            pill(im, t, v + 4.5, "DREHEN", (110, 150), size=56, color=ORANGE)
            pill(im, t, v + 6.8, "+ ETWAS AUFMASS", (110, 270), size=46)
    elif sid == 303:
        im = clip("ofen", pw(vt, [(0, 1), (3.0, 40), (6.9, 48), (7.6, 64), (11.4, 96)]))
        big_number(im, t, v + 2.3, 850, lambda x: f"≈ {int(round(x))} °C", (W / 2, 120), size=100, dur_c=.8, panel=True)
        pill(im, t, v + 4.3, "MEHRERE STUNDEN", (110, 880), size=48)
        pill(im, t, v + 8.6, "SCHRUMPFT & VERZIEHT SICH", (110, 880 - 115), size=46, color=ORANGE)
    elif sid == 304:
        if vt < 4.8:
            im = clip("drehen", 96, zoom=1.35, cx=.5, cy=.3); pill(im, t, v + .4, "ZU HART ZUM DREHEN", (110, 150), size=52, color=ORANGE)
        else:
            im = clip("schleifen", 1 + (vt - 4.8) * 24 * .8); im = vignette_punch(im, vt, 4.8)
            pill(im, t, v + 5.0, "SCHLEIFEN", (110, 150), size=56, color=ORANGE)
    elif sid == 305:
        im = clip("schleifen", 1 + (vt + 1.9) * 24 * .7)
        an = json.load(open(f"{D}/r2/schleifen/anchors.json")).get("spark", [.6, .5])
        sparks(im, t, v, v + 8.9, (an[0] * W, an[1] * H), seed=21, spread=(-2.8, -1.2))
        for i, (w_, at) in enumerate([("SEITENFLÄCHEN", .2), ("AUSSENDURCHMESSER", 1.6), ("LAUFBAHN", 5.2)]):
            pill(im, t, v + at, w_, (110, 150 + i * 115), size=50, color=ORANGE if i == 2 else INK, strike_at=None)
    elif sid == 306:
        im = clip("honen", 1 + vt * 24 * .4)
        pill(im, t, v + .3, "HONEN", (110, 150), size=56, color=ORANGE)
        pill(im, t, v + 3.9, "SPIEGELGLATT", (110, 270), size=48)
        pill(im, t, v + 7.7, "LÄNGERE LEBENSDAUER", (110, 380), size=46); pill(im, t, v + 9.6, "LEISERER LAUF", (110, 490), size=46)
    elif sid == 401:
        im = clip("lager", 50, zoom=.95)
        callout(im, t, v + 1.6, (W / 2 + 260, H / 2 - 140), "KÄFIG", side=1, length=240)
    elif sid == 402:
        pos = pw(vt, [(0, 1), (2.7, 30), (8.8, 96)])
        im = clip("kaefig", pos, zoom=.85); im = shake(im, t, v + 2.7, amp=12)
        pill(im, t, v + 1.0, "STANZEN", (110, 150), size=56, color=ORANGE)
        pill(im, t, v + 7.3, "2 HÄLFTEN PRO LAGER", (110, 270), size=46)
        pill(im, t, v + 9.3, "AUCH: MESSING · KUNSTSTOFF", (110, 380), size=44)
    elif sid == 501:
        im = clip("lager", 60 + vt * 24 * .4)
        pill(im, t, v + 3.8, "WIE KOMMEN DIE KUGELN HINEIN?", (110, 150), size=52, color=ORANGE)
    elif sid == 502:
        im = clip("lager", 120, zoom=1.2)
        pill(im, t, v + .2, "KEINE ÖFFNUNG", (110, 150), size=52)
        pill(im, t, v + 2.4, "KUGEL DICKER ALS SPALT", (110, 260), size=52, color=ORANGE)
    elif sid == 503:
        im = clip("montage", pw(vt, [(0, 1), (6.8, 10), (10.4, 84), (10.8, 86)]))
        pill(im, t, v + 1.2, "INNENRING ZUR SEITE", (110, 150), size=48)
        pill(im, t, v + 3.5, "SICHELFÖRMIGE LÜCKE", (110, 260), size=48, color=ORANGE)
        pill(im, t, v + 9.3, "DICHT AN DICHT", (110, 370), size=48)
    elif sid == 504:
        im = clip("montage", pw(vt, [(0, 96), (2.5, 112), (2.9, 112), (4.7, 128), (6.9, 130)]))
        pill(im, t, v + .3, "VERTEILEN", (110, 150), size=48); pill(im, t, v + 2.9, "ZENTRIEREN", (110, 260), size=48)
        pill(im, t, v + 5.1, "GEFANGEN", (110, 370), size=56, color=ORANGE)
    elif sid == 505:
        im = clip("montage", pw(vt, [(0, 130), (3.0, 152), (5.6, 160), (6.9, 178), (7.4, 192)]))
        pill(im, t, v + .5, "KÄFIGHÄLFTEN", (110, 150), size=48); pill(im, t, v + 4.9, "FETT", (110, 260), size=48)
        pill(im, t, v + 5.9, "DICHTSCHEIBEN", (110, 370), size=48)
    elif sid == 506:
        im = clip("lager", 60 + (vt * 24 * .5) % 60)
        waveform(im, t, v + 1.5, v + 6.4)
        pill(im, t, v + 1.6, "GERÄUSCHPRÜFUNG", (110, 150), size=52, color=ORANGE)
    elif sid == 601:
        if vt < 1.4: im = still("draht", vt + 1, 3)
        elif vt < 2.2: im = clip("ofen", 40); im = vignette_punch(im, vt, 1.4)
        elif vt < 3.9: im = clip("ofen", 56 + (vt - 2.2) * 12); im = vignette_punch(im, vt, 2.2)
        else: im = clip("lager", 60 + (vt - 3.9) * 24 * .6); im = vignette_punch(im, vt, 3.9)
        for w_, at, y in (("DRAHT", 0, 150), ("FEUER", 1.5, 260), ("ÖL", 2.3, 370), ("GEDULD", 3.0, 480)):
            pill(im, t, v + at, w_, (110, y), size=50, color=ORANGE if w_ == "GEDULD" else INK)
    elif sid == 602:
        if vt < 2.6:
            im = kenburns(img("map"), vt, 2.6, 1.3, 1.45, .6, .62, .62, .64); typed(im, t, v + .2, ["SCHWEINFURT, 1883"], (1080, 820), size=44)
        else:
            im = still("viele", vt - 2.6, T - 2.6, 1.05, 1.3, .3, .3, .7, .6); im = vignette_punch(im, vt, 2.6)
            big_number(im, t, v + 2.8, 30, lambda x: f"≈ {int(round(x))} MRD. / JAHR", (W / 2, H / 2), size=120, dur_c=1.0, panel=True)
    elif sid == 603:
        im = BG.copy(); d = ImageDraw.Draw(im)
        d.text((W / 2, 170), "MEISTERWERK", font=font(F + "InterDisplay-Black.otf", 110), fill=INK, anchor="mm")
        d.text((W / 2, 260), "Wie die Dinge wirklich gebaut werden", font=font(F + "Inter-SemiBold.otf", 42), fill=GREY, anchor="mm")
        # comment prompt
        if vt > .2:
            a_ = eout((vt - .2) / .35); bx = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(bx)
            bd.rounded_rectangle((W / 2 - 560, 360 + 30 * (1 - a_), W / 2 + 560, 560 + 30 * (1 - a_)), 30, fill=(255, 255, 255, int(240 * a_)))
            im.paste(bx, (0, 0), bx); d = ImageDraw.Draw(im)
            d.text((W / 2, 420 + 30 * (1 - a_)), "WELCHES BAUTEIL ALS NÄCHSTES?", font=font(F + "InterDisplay-Black.otf", 58), fill=INK, anchor="mm")
            # speech bubble icon + text
            cx, cy = W / 2 - 300, 505 + 30 * (1 - a_)
            d.rounded_rectangle((cx - 34, cy - 24, cx + 34, cy + 20), 10, fill=ORANGE); d.polygon([(cx - 14, cy + 18), (cx - 26, cy + 36), (cx + 2, cy + 18)], fill=ORANGE)
            d.text((cx + 60, cy - 2), "Schreib es in die Kommentare", font=font(F + "Inter-SemiBold.otf", 44), fill=GREY, anchor="lm")
        if vt > 7.4:
            b_ = eout((vt - 7.4) / .3); s_ = .8 + .2 * b_
            bw, bh = 470 * s_, 120 * s_; x0 = W / 2 - 300
            d.rounded_rectangle((x0 - bw / 2, 680, x0 + bw / 2, 680 + bh), 60, fill=ORANGE)
            d.text((x0, 680 + bh / 2), "ABONNIEREN", font=font(F + "InterDisplay-Black.otf", 54 * s_), fill=(255, 255, 255), anchor="mm")
        if vt > 8.7:
            c_ = eout((vt - 8.7) / .3); x1, y1 = W / 2 + 200, 740
            sw = math.sin((vt - 8.7) * 14) * 18 * max(0, 1 - (vt - 8.7) / 1.6)
            bell = Image.new("RGBA", (220, 220), (0, 0, 0, 0)); bdd = ImageDraw.Draw(bell)
            bdd.pieslice((40, 30, 180, 170), 180, 360, fill=INK); bdd.rectangle((40, 100, 180, 150), fill=INK)
            bdd.polygon([(28, 160), (192, 160), (180, 140), (40, 140)], fill=INK); bdd.ellipse((92, 160, 128, 192), fill=INK); bdd.ellipse((100, 16, 120, 36), fill=INK)
            bell = bell.rotate(sw, resample=Image.BICUBIC, center=(110, 20)).resize((int(150 * c_) + 1, int(150 * c_) + 1))
            im.paste(bell, (int(x1 - bell.width / 2), int(y1 - bell.height / 2)), bell); d = ImageDraw.Draw(im)
            d.text((x1 + 110, y1), "Glocke aktivieren", font=font(F + "Inter-Bold.otf", 44), fill=INK, anchor="lm")
    if im is None: im = BG.copy()
    if sid not in (603,): brand(im)
    return im

def sfx_events():
    ev = []
    for sid, s0, T in segs:
        if isinstance(sid, str): ev += [(s0 + .05, "boom", .45), (s0 + .05, "clink", .25)]
    a = vo_at
    typed_sfx(ev, a[101] + .2, ["SCHWEINFURT", "UM 1880"]); ev += [(a[101] + 3.2, "mclick", .35)]
    typed_sfx(ev, a[102] + 4.0, ["ENGLAND:", "HANDARBEIT AN DER DREHBANK"]); ev += [(a[102] + x, "clink", .3) for x in (8.3, 9.55, 10.4)]
    ev += [(a[103] + 2.3, "tick", .4), (a[103] + 5.5, "roll", .35)] + [(a[103] + x, "mclick", .35) for x in (9.0, 10.3, 11.7)]
    ev += [(a[104] + x, "mclick", .3) for x in (2.7, 3.6, 8.3)] + [(a[104] + .3, "roll", .3)]
    ev += [(a[105] + .9, "tick", .45)]
    ev += [(a[106] + x, "mclick", .35) for x in (1.6, 3.7)]; typed_sfx(ev, a[106] + 7.2, ["SCHWEINFURT =", "STADT DER WÄLZLAGER"]); typed_sfx(ev, a[106] + 10.2, ["1943"])
    ev += [(a[106] + 9.9, "sub_drop", .4)]
    typed_sfx(ev, a[201] + 2.6, ["WÄLZLAGERSTAHL", "100Cr6"]); ev += [(a[201] + x, "mclick", .35) for x in (6.5, 8.6)]
    ev += [(a[202] + x, "mclick", .5) for x in (21 / 24 / .45, 49 / 24 / .45)] + [(a[202] + x + .3, "clink", .35) for x in (35 / 24 / .45, 63 / 24 / .45)]
    typed_sfx(ev, a[203] + 2.3, ["KALTSTAUCHEN"]); ev += [(a[203] + 6.4, "boom", .8), (a[203] + 6.4, "stamp", .6), (a[203] + 6.45, "hiss", .25), (a[203] + 8.5, "tick", .4)]
    ev += [(a[204] + x, "stamp", .55) for x in (1.0, 2.4, 3.8)] + [(a[204] + x, "boom", .35) for x in (1.0, 2.4, 3.8)]
    ev += [(a[205] + 3.0, "mclick", .35)]
    ev += [(a[206] + .2, "roll", .4), (a[206] + 4.0, "roll", .35), (a[206] + 7.5, "roll", .3)] + [(a[206] + x, "mclick", .3) for x in (2.3, 5.2, 6.4, 8.2)]
    ev += [(a[208] + 2.4, "tick", .4), (a[208] + 4.9, "hiss", .7), (a[208] + 5.0, "sub_drop", .3)]
    ev += [(a[209] + x, "mclick", .35) for x in (3.4, 4.6)]
    ev += [(a[210] + 2.2, "mclick", .35), (a[210] + 5.3, "hiss", .25), (a[210] + 7.0, "mclick", .35), (a[210] + 9.0, "hiss", .2), (a[210] + 10.6, "mclick", .3)]
    ev += [(a[211] + x, "mclick", .3) for x in (2.5, 3.6)] + [(a[211] + 11.4, "tick", .45), (a[211] + 11.4, "clink", .35)]
    ev += [(a[212] + x, "tick", .35) for x in (3.2, 4.0, 4.8)] + [(a[212] + 5.8, "slap", .3)]
    ev += [(a[301] + x, "mclick", .35) for x in (1.9, 2.9)]
    ev += [(a[302] + 1.4, "mclick", .3), (a[302] + 4.2, "hiss", .25), (a[302] + 4.5, "mclick", .35), (a[302] + 6.8, "mclick", .3)]
    ev += [(a[303] + 2.3, "tick", .4), (a[303] + 4.3, "mclick", .3), (a[303] + 7.0, "hiss", .7), (a[303] + 7.05, "sub_drop", .3), (a[303] + 8.6, "mclick", .3)]
    ev += [(a[304] + .4, "slap", .3), (a[304] + 4.8, "hiss", .35), (a[304] + 5.0, "mclick", .35)]
    ev += [(a[305] + x, "mclick", .35) for x in (.2, 1.6, 5.2)] + [(a[305] + x, "hiss", .18) for x in (0, 2.5, 5.0, 7.5)]
    ev += [(a[306] + x, "mclick", .3) for x in (.3, 3.9, 7.7, 9.6)]
    ev += [(a[401] + 1.6, "mclick", .35)]
    ev += [(a[402] + 2.7, "stamp", .7), (a[402] + 2.7, "boom", .5)] + [(a[402] + x, "mclick", .3) for x in (1.0, 7.3, 9.3)]
    ev += [(a[501] + 3.8, "tick", .35)]
    ev += [(a[502] + x, "mclick", .35) for x in (.2, 2.4)]
    ev += [(a[503] + x, "mclick", .3) for x in (1.2, 3.5, 9.3)]
    for k in range(7):  # balls dropping into the crescent
        fr = 10 + k * 9 + 10; vt_ = 6.8 + (fr - 10) / 74 * 3.6
        ev.append((a[503] + vt_, "clink", .32))
    ev += [(a[504] + .3, "roll", .35), (a[504] + 2.9, "mclick", .4), (a[504] + 4.7, "clink", .35), (a[504] + 5.1, "tick", .35)]
    ev += [(a[505] + 3.0, "mclick", .5), (a[505] + 6.9, "mclick", .45)] + [(a[505] + x, "mclick", .3) for x in (.5, 4.9, 5.9)]
    ev += [(a[506] + 1.6, "mclick", .35), (a[506] + 6.4, "glitch", .3)]
    ev += [(a[601] + x, "clink", .3) for x in (0, 1.4, 2.2, 3.9)]
    typed_sfx(ev, a[602] + .2, ["SCHWEINFURT, 1883"]); ev += [(a[602] + 2.8, "tick", .4)]
    ev += [(a[603] + .2, "mclick", .4), (a[603] + 7.4, "mclick", .5), (a[603] + 8.7, "mclick", .5)]
    return ev

MUSIC = [(0, "emotional_piano", 0), (None, "industrial_drive", 0, 201), (None, "epic_empire", 0, 301), (None, "industrial_drive", 40, 401),
         (None, "suspense_pulse", 0, 501), (None, "industrial_drive", 70, 504), (None, "epic_empire", 30, 601)]

def music_bed(N, SR):
    def src(name):
        p = f"{D}/music/{name}.mp3" if os.path.exists(f"{D}/music/{name}.mp3") else f"{D}/../../assets/music/{name}.mp3"
        return I.load(p)
    cues = []
    for c in MUSIC:
        if c[0] == 0: cues.append((0.0, c[1], c[2]))
        else:
            n = c[3]; card = [s for s in segs if s[0] == f"card{CH[n][0]}"] if n in CH else []
            t0 = card[0][1] if card else vo_at[n] - .15
            cues.append((t0, c[1], c[2]))
    bed = np.zeros((N, 2), np.float32); XF = int(1.5 * SR)
    for i, (t0, name, off) in enumerate(cues):
        t1 = cues[i + 1][0] if i + 1 < len(cues) else N / SR
        a = int(t0 * SR); b = min(N, int(t1 * SR) + XF)
        tr = src(name)[int(off * SR):]; tr = np.concatenate([tr] * (2 + (b - a) // max(1, len(tr))))[: b - a].copy()
        r = min(XF, len(tr)); tr[:r] *= np.linspace(0, 1, r)[:, None]
        if i + 1 < len(cues): tr[-XF:] *= np.linspace(1, 0, XF)[:, None]
        g = {"emotional_piano": .9, "suspense_pulse": .9, "epic_empire": .75}.get(name, 1.0)
        bed[a:a + len(tr)] += tr * g
    return bed

def render_video(path):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    n = int(TOTAL * FPS)
    for i in range(n):
        p.stdin.write(frame(i / FPS).convert("RGB").tobytes())
        if i % 480 == 0: print("frame", i, "/", n, flush=True)
    p.stdin.close(); p.wait()

def mix(path):
    SR = I.SR; N = int((TOTAL + .3) * SR)
    voice = np.zeros((N, 2), np.float32)
    for n, at in vo_at.items():
        a = I.load(VO[n]); i = int(at * SR); voice[i:i + len(a)] += a[:N - i]
    ivo = np.zeros((int((I.TOTAL + .5) * SR), 2), np.float32)
    for v, at in I.vo_at.items():
        a = I.load(I.VO[v]); i = int(at * SR); ivo[i:i + len(a)] += a[:len(ivo) - i]
    ref = np.sqrt(np.mean(ivo ** 2)) * 4 + 1e-9  # same voice gain as intro
    voice *= .5 / ref
    music = music_bed(N, SR)
    vamp = np.abs(voice[:, 0]); k = int(.15 * SR); vs = np.convolve(vamp, np.ones(k) / k, mode="same")
    duck = 1 - .55 * np.clip(vs / (vs.max() * .25 + 1e-9), 0, 1)
    music *= duck[:, None] * .30
    end_f = int((TOTAL - 2.0) * SR); music[end_f:] *= np.linspace(1, 0, N - end_f)[:, None]
    fx = np.zeros((N, 2), np.float32)
    smap = json.loads(os.environ.get("SFX_MAP", "{}")); rot = smap.pop("_rotate", None); k_ = 0
    for at, name, g in sfx_events():
        if rot and name == "clink": name = rot[k_ % len(rot)]; k_ += 1
        else: name = smap.get(name, name)
        s = I.load(f"{D}/sfx/{name}.wav")
        if name.startswith("key"): g *= .75
        i = int(at * SR)
        if 0 <= i < N: fx[i:i + len(s)] += s[:N - i] * g
    out = np.tanh((voice + music + fx * .8) * 1.1) * .95
    import scipy.io.wavfile as wf
    wf.write(path, SR, (out * 32767).astype(np.int16))

def snippet(tag, t0=18.6, t1=25.8):
    mix(f"{D}/t3/aud_{tag}.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t0), "-to", str(t1), "-i", f"{D}/main_video.mp4", "-ss", str(t0), "-to", str(t1), "-i", f"{D}/t3/aud_{tag}.wav",
                    "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-c:a", "aac", "-b:a", "160k", f"{D}/out_Sound_{tag}.mp4"], check=True)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode == "still":
        os.makedirs(f"{D}/t3", exist_ok=True)
        for tt in map(float, sys.argv[2:]): frame(tt).save(f"{D}/t3/m_{tt:06.1f}.jpg", quality=80)
    elif mode == "snippet":
        snippet(sys.argv[2])
    elif mode == "times":
        for s in segs: print(s[0], round(s[1], 2), round(s[2], 2), round(vo_at.get(s[0], 0), 2))
    else:
        render_video(f"{D}/main_video.mp4"); mix(f"{D}/main_audio.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{D}/main_video.mp4", "-i", f"{D}/main_audio.wav", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{D}/main_part.mp4"], check=True)
        print("done")
