"""Meisterwerk 004 – Compositor. Aufruf: python3 main.py prep | part <name> <t0> <t1> | still <t> [out.png]
Bild: 3D-Clips (12 fps -> 24 fps interpoliert) + Overlays (Typenschild, Laser-Gravur, Bemaßung, Callout, Taktuhr, Makro-Zoom,
Schlag-Ruck, Funken, Dampf) + Zahnrad-Kapitelmarken + 2D-Stahlträger-Diagramme. Ton: mix.py."""
import os, sys, json, math, random, subprocess, glob
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from beats import B as BEATS
from shots import P
WK = "/home/claude/mw-work/004"
W, H, FPS = 1920, 1080, 24
T = json.load(open(WK + "/timeline.json")); SH = json.load(open(WK + "/shots.json"))
BL = {b["id"]: b for b in T["blocks"]}
FI = "/usr/share/fonts/opentype/inter/"
ORANGE = (255, 92, 12); GLUT = (255, 110, 20); WHITE = (245, 243, 238); INK = (24, 24, 28); STEELC = (150, 152, 158)
_f = {}
def font(n, s):
    k = (n, int(s))
    if k not in _f: _f[k] = ImageFont.truetype(FI + n, int(s))
    return _f[k]
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def eout(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ein(x): x = min(max(x, 0), 1); return x ** 3

# ---------------- Clips ----------------
def prep():
    os.makedirs(WK + "/c", exist_ok=True)
    for s in SH:
        if s["art"] != "3d": continue
        src = f"{WK}/r/{s['dir']}"; dst = f"{WK}/c/{s['dir']}.mp4"
        if os.path.exists(dst) or not os.path.exists(src + "/.done"): continue
        vf = "minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,scale=1920:1080:flags=lanczos"
        subprocess.run(f"ffmpeg -y -v error -framerate 12 -i {src}/f_%04d.png -vf \"{vf}\" -c:v libx264 -crf 14 -preset veryfast -pix_fmt yuv420p {dst}.tmp.mp4 && mv {dst}.tmp.mp4 {dst}", shell=True)
        print("prep", s["dir"], flush=True)

class Clip:
    def __init__(s): s.name = None; s.cap = None; s.pos = -1; s.last = None; s.n = 0
    def get(s, name, idx):
        if name != s.name:
            if s.cap: s.cap.release()
            s.cap = cv2.VideoCapture(f"{WK}/c/{name}.mp4"); s.name = name; s.pos = -1; s.last = None
            s.n = int(s.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        idx = max(0, min(idx, s.n - 1))
        if idx < s.pos:
            s.cap.set(cv2.CAP_PROP_POS_FRAMES, idx); s.pos = idx - 1
        while s.pos < idx:
            ok, fr = s.cap.read()
            if not ok: break
            s.last = fr; s.pos += 1
        return cv2.cvtColor(s.last, cv2.COLOR_BGR2RGB) if s.last is not None else np.zeros((H, W, 3), np.uint8)
CLIP = Clip()
_st = {}
def still(path):
    if path not in _st:
        im = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB); _st[path] = cv2.resize(im, (W, H), interpolation=cv2.INTER_LANCZOS4)
    return _st[path]
def zoomed(fr, z, cx=.5, cy=.5):
    if z <= 1.001: return fr
    M = np.float32([[z, 0, (1 - z) * W * cx], [0, z, (1 - z) * H * cy]])
    return cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
def bgdark():
    if "bgd" not in _st:
        b = still(f"{WK}/r/bg_dunkel/f_0001.png"); b = cv2.GaussianBlur(b, (0, 0), 18); _st["bgd"] = (b * 0.45).astype(np.uint8)
    return _st["bgd"]
def bglight():
    if "bgl" not in _st:
        b = still(f"{WK}/r/bg_hell/f_0001.png"); b = cv2.GaussianBlur(b, (0, 0), 14); _st["bgl"] = (b * 0.92).astype(np.uint8)
    return _st["bgl"]

# ---------------- Overlay-Bausteine ----------------
_plate = {}
def metal_tex(w, h, seed=1):
    k = (w, h, seed)
    if k not in _plate:
        rng = np.random.default_rng(seed)
        g = np.linspace(205, 150, h)[:, None] * np.ones((1, w))
        lines = rng.normal(0, 6, (1, w)).repeat(h, 0) * 0 + rng.normal(0, 5, (h, 1)).repeat(w, 1)
        a = np.clip(g + lines + rng.normal(0, 3, (h, w)), 0, 255)
        rgb = np.stack([a * 0.97, a * 0.98, a * 1.0], -1).astype(np.uint8)
        _plate[k] = Image.fromarray(rgb)
    return _plate[k]
def typenschild(im, t, t0, t1, big, sub, pos="bl"):
    """Metallschild mit Schrauben klappt auf (Typenschild statt big_number)"""
    if t < t0 or t > t1: return
    a = eout((t - t0) / .35) * (1 - ein((t - (t1 - .25)) / .25))
    fb = font("Inter-Black.otf", 92); fs = font("Inter-Bold.otf", 30)
    d0 = ImageDraw.Draw(im)
    wb = max(d0.textlength(big, font=fb), d0.textlength(sub, font=fs)) + 110; hb = 190
    x0 = 90 if pos == "bl" else W - 90 - wb if pos == "br" else (W - wb) / 2; y0 = H - 110 - hb
    sy = max(0.02, a)  # klappt vertikal auf
    pl = metal_tex(int(wb), hb).copy().convert("RGBA")
    pd = ImageDraw.Draw(pl)
    pd.rectangle((0, 0, wb - 1, hb - 1), outline=(90, 92, 98, 255), width=4); pd.rectangle((6, 6, wb - 7, hb - 7), outline=(230, 230, 232, 255), width=1)
    for sx, sy_ in ((22, 22), (wb - 22, 22), (22, hb - 22), (wb - 22, hb - 22)):
        pd.ellipse((sx - 9, sy_ - 9, sx + 9, sy_ + 9), fill=(120, 122, 128, 255), outline=(70, 70, 76, 255), width=2)
        pd.line((sx - 6, sy_ - 6, sx + 6, sy_ + 6), fill=(70, 70, 76, 255), width=2)
    pd.rectangle((0, hb - 58, wb, hb - 52), fill=ORANGE + (255,))
    # geprägte Schrift: heller Versatz + dunkle Schrift
    pd.text((wb / 2 + 2, 78), big, font=fb, fill=(235, 235, 238, 255), anchor="mm"); pd.text((wb / 2, 76), big, font=fb, fill=(28, 28, 32, 255), anchor="mm")
    pd.text((wb / 2, hb - 26), sub, font=fs, fill=(40, 40, 44, 255), anchor="mm")
    h2 = max(2, int(hb * sy)); pl = pl.resize((int(wb), h2))
    sh = Image.new("RGBA", (int(wb) + 40, h2 + 40), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle((20, 26, wb + 20, h2 + 26), fill=(0, 0, 0, int(140 * a)))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    yc = y0 + hb / 2 - h2 / 2
    im.alpha_composite(sh, (int(x0 - 20), int(yc - 20))); pl.putalpha(int(255 * min(1, a * 1.5))); im.alpha_composite(pl, (int(x0), int(yc)))
def laser(im, t, t0, t1, text, y=None, size=86):
    """Laser-Gravur: Text brennt sich Zeichen für Zeichen ein, Funken an der Spitze"""
    if t < t0 or t > t1: return
    f = font("Inter-Black.otf", size); d = ImageDraw.Draw(im)
    u = min(1, (t - t0) / max(.5, len(text) * .055)); n = int(round(len(text) * u))
    fade = 1 - ein((t - (t1 - .3)) / .3)
    y = y or H - 150; tw = d.textlength(text, font=f); x0 = (W - tw) / 2
    bx = Image.new("RGBA", (int(tw) + 120, size + 80), (0, 0, 0, 0)); bd = ImageDraw.Draw(bx)
    bd.rounded_rectangle((0, 0, tw + 119, size + 79), 10, fill=(14, 14, 16, int(170 * fade)))
    im.alpha_composite(bx, (int(x0 - 60), int(y - size / 2 - 40)))
    cool = min(1, max(0, (t - t0 - len(text) * .055) / 1.2))
    col = tuple(int(a + (b - a) * cool) for a, b in zip((255, 200, 140), (255, 140, 60)))
    gl = Image.new("RGBA", (int(tw) + 80, size + 60), (0, 0, 0, 0)); gd = ImageDraw.Draw(gl)
    gd.text((40, 30 + size / 2), text[:n], font=f, fill=GLUT + (int(255 * fade * (1 - .5 * cool)),), anchor="lm")
    gl = gl.filter(ImageFilter.GaussianBlur(9)); im.alpha_composite(gl, (int(x0 - 40), int(y - size / 2 - 30)))
    d = ImageDraw.Draw(im); d.text((x0, y), text[:n], font=f, fill=col + (int(255 * fade),), anchor="lm")
    if u < 1:
        tip = x0 + d.textlength(text[:n], font=f); r = random.Random(int(t * 97))
        for _ in range(16):
            an = r.uniform(-2.9, -0.2); L = r.uniform(12, 70)
            d.line((tip, y, tip + L * math.cos(an), y + L * math.sin(an)), fill=(255, 210, 120, 230), width=3)
        d.ellipse((tip - 8, y - 8, tip + 8, y + 8), fill=(255, 240, 210, 255))
def callout(im, t, t0, t1, xy, text, side=1):
    if t < t0 or t > t1: return
    a = 1 - ein((t - (t1 - .25)) / .25); p = eout((t - t0) / .35); d = ImageDraw.Draw(im)
    x, y = xy; L = 230 * p; ex = x + side * L; ey = y - 90 * p
    d.ellipse((x - 11, y - 11, x + 11, y + 11), outline=ORANGE + (int(255 * a),), width=4); d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=ORANGE + (int(255 * a),))
    d.line((x, y, x + side * 60 * p, ey), fill=ORANGE + (int(255 * a),), width=4); d.line((x + side * 60 * p, ey, ex, ey), fill=ORANGE + (int(255 * a),), width=4)
    if p > .6:
        q = eout((p - .6) / .4); f = font("Inter-Bold.otf", 44); tw = d.textlength(text, font=f)
        tx = ex + 18 if side > 0 else ex - 18 - tw * q
        bx = Image.new("RGBA", (int(tw * q) + 36, 76), (245, 243, 238, int(235 * a)))
        ImageDraw.Draw(bx).rectangle((0, 0, 6, 76), fill=ORANGE + (255,))
        im.alpha_composite(bx, (int(tx - 18), int(ey - 38)))
        cr = Image.new("RGBA", (int(tw * q) + 2, 70), (0, 0, 0, 0)); ImageDraw.Draw(cr).text((0, 35), text, font=f, fill=INK + (int(255 * a),), anchor="lm")
        im.alpha_composite(cr, (int(tx), int(ey - 35)))
def bemassung(im, t, t0, t1, box, label):
    if t < t0 or t > t1: return
    a = 1 - ein((t - (t1 - .25)) / .25); p = eout((t - t0) / .5); d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = box; xm = x0 + (x1 - x0) * p
    c = WHITE + (int(255 * a),)
    for xx in (x0, x1 if p > .98 else None):
        if xx is not None: d.line((xx, y0 - 26, xx, y0 + 26), fill=c, width=4)
    d.line((x0, y0, xm, y0), fill=c, width=4)
    for xx, sgn in ((x0, 1), (xm, -1)):
        d.polygon([(xx, y0), (xx + sgn * 22, y0 - 9), (xx + sgn * 22, y0 + 9)], fill=c)
    if p > .9:
        f = font("Inter-Bold.otf", 42); tw = d.textlength(label, font=f); cx = (x0 + x1) / 2
        bx = Image.new("RGBA", (int(tw) + 40, 64), (20, 20, 24, int(200 * a))); im.alpha_composite(bx, (int(cx - tw / 2 - 20), int(y0 - 92)))
        ImageDraw.Draw(im).text((cx, y0 - 60), label, font=f, fill=(255, 170, 90, int(255 * a)), anchor="mm")
def taktuhr(im, t, t0, t1, v, fmt, label):
    if t < t0 or t > t1: return
    a = eout((t - t0) / .3) * (1 - ein((t - (t1 - .25)) / .25)); p = 1 - (1 - min(1, (t - t0) / 1.4)) ** 2.2
    val = fmt.format(v * p).replace(",", ".")
    f = font("Inter-Black.otf", 96); fl = font("Inter-Bold.otf", 30); d = ImageDraw.Draw(im)
    tw = max(d.textlength(fmt.format(v).replace(",", "."), font=f), d.textlength(label, font=fl)) + 90
    x0, y0 = W - 90 - tw, 90
    bx = Image.new("RGBA", (int(tw), 190), (16, 16, 18, int(215 * a))); bd = ImageDraw.Draw(bx)
    bd.rectangle((0, 0, tw - 1, 189), outline=(80, 82, 88, int(255 * a)), width=3); bd.rectangle((0, 182, tw * p, 189), fill=ORANGE + (int(255 * a),))
    im.alpha_composite(bx, (int(x0), y0)); d = ImageDraw.Draw(im)
    d.text((x0 + tw / 2, y0 + 78), val, font=f, fill=(255, 150, 70, int(255 * a)), anchor="mm")
    d.text((x0 + tw / 2, y0 + 150), label, font=fl, fill=(200, 200, 205, int(255 * a)), anchor="mm")
def funken(im, t, t0, t1, xy, n=70, seed=3):
    if t < t0 or t > t1 + .6: return
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); r = random.Random(seed)
    for i in range(n * 3):
        born = t0 + r.random() * (t1 - t0); age = t - born
        if age < 0 or age > .5: continue
        an = r.uniform(-3.0, -0.15); v = 900 * r.uniform(.4, 1.3)
        x = xy[0] + math.cos(an) * v * age; y = xy[1] + math.sin(an) * v * age + 1600 * age * age
        d.line((x - math.cos(an) * 20, y - math.sin(an) * 20 - 30 * age, x, y), fill=(255, 190, 80, int(255 * (1 - age / .5))), width=3)
    g = ov.filter(ImageFilter.GaussianBlur(5)); im.alpha_composite(g); im.alpha_composite(ov)
def dampf(im, t, t0, t1, seed=5):
    if t < t0 or t > t1: return
    ov = Image.new("RGBA", (W // 4, H // 4), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); r = random.Random(seed)
    for i in range(40):
        born = t0 + r.random() * (t1 - t0) * .7; age = t - born
        if age < 0 or age > 2.4: continue
        x = r.uniform(.2, .8) * W / 4 + 20 * math.sin(age * 2 + i); y = H / 4 * .75 - age * 90 - r.random() * 10
        rad = 10 + age * 26; al = int(120 * (1 - age / 2.4) * min(1, age * 4))
        d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=(235, 235, 240, al))
    ov = ov.filter(ImageFilter.GaussianBlur(8)).resize((W, H), Image.BILINEAR); im.alpha_composite(ov)
def hinweis(im, text):
    d = ImageDraw.Draw(im); f = font("Inter-Bold.otf", 26)
    d.text((40, H - 46), text, font=f, fill=(255, 255, 255, 170))
def brand(im):
    d = ImageDraw.Draw(im); d.text((W - 70, 52), "MEISTERWERK", font=font("Inter-Black.otf", 26), fill=(255, 255, 255, 120), anchor="rm")
    d.rectangle((W - 70 - 46, 70, W - 70, 74), fill=ORANGE + (150,))

# ---------------- Zahnrad-Kapitelmarke ----------------
def gear(d, cx, cy, r, teeth, ang, fill):
    pts = []
    for i in range(teeth * 4):
        a = ang + i * 2 * math.pi / (teeth * 4); rr = r if (i % 4) in (0, 1) else r * .82
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill); d.ellipse((cx - r * .42, cy - r * .42, cx + r * .42, cy + r * .42), fill=(18, 18, 20, 255))
def card(t, kind, num, title, sub=None):
    base = Image.fromarray(bgdark()).convert("RGBA"); d = ImageDraw.Draw(base)
    p = eout(t / .7); ang = -2.2 * (1 - p) + t * .25
    cx = W / 2 - 520 + 0 * p; cy = H / 2
    r = 150 * (.6 + .4 * p)
    gear(d, cx - 300 * (1 - p), cy, r, 12, ang, ORANGE + (255,))
    a = eout((t - .35) / .4)
    if kind == "chapter":
        d.text((cx + 230, cy - 95), f"KAPITEL {num}", font=font("Inter-Bold.otf", 44), fill=(200, 200, 205, int(255 * a)), anchor="lm")
        fs_ = 110
        while d.textlength(title.upper(), font=font("Inter-Black.otf", fs_)) > W - (cx + 230) - 90: fs_ -= 4
        d.text((cx + 230 - 40 * (1 - a), cy + 10), title.upper(), font=font("Inter-Black.otf", fs_), fill=WHITE + (int(255 * a),), anchor="lm")
        d.rectangle((cx + 232, cy + 92, cx + 232 + 300 * a, cy + 104), fill=ORANGE + (255,))
    else:
        d.text((cx + 230 - 40 * (1 - a), cy - 30), "DER KOLBEN", font=font("Inter-Black.otf", 150), fill=WHITE + (int(255 * a),), anchor="lm")
        d.text((cx + 236, cy + 85), "Warum er absichtlich nicht rund ist", font=font("Inter-Bold.otf", 50), fill=(255, 170, 90, int(255 * eout((t - .8) / .4))), anchor="lm")
    return base

# ---------------- 2D-Szenen: Stahlträger-Diagramm usw. ----------------
def ibeam(im, x, y, w, h, label, val, a=1.0, hot=False):
    """Stahlträger (Doppel-T) als Balken; w animierbar"""
    if w < 4: return
    d = ImageDraw.Draw(im)
    top = (120, 124, 132) if not hot else (255, 120, 40)
    g = metal_tex(int(w), int(h), 7).convert("RGBA"); g.putalpha(int(255 * a))
    im.alpha_composite(g, (int(x), int(y)))
    d.rectangle((x, y, x + w, y + h * .2), fill=top + (int(255 * a),)); d.rectangle((x, y + h * .8, x + w, y + h), fill=top + (int(255 * a),))
    for k in range(int(w // 60)): d.ellipse((x + 30 + k * 60 - 5, y + h * .5 - 5, x + 30 + k * 60 + 5, y + h * .5 + 5), fill=(70, 70, 76, int(255 * a)))
    d.text((x - 24, y + h / 2), label, font=font("Inter-Bold.otf", 40), fill=WHITE + (int(255 * a),), anchor="rm")
    d.text((x + w + 24, y + h / 2), val, font=font("Inter-Black.otf", 56 if len(val) < 14 else 40), fill=(255, 160, 80, int(255 * a)), anchor="lm")
def crane_beam(im, t, t0, x, y, wfull, h, label, val, dur=1.0):
    """Ein Kran senkt den Träger von oben ab"""
    if t < t0: return
    p = eout((t - t0) / dur); yy = y - (1 - p) * 520
    d = ImageDraw.Draw(im)
    if p < 1:
        d.line((x + wfull / 2, -10, x + wfull / 2, yy), fill=(40, 40, 44, 255), width=6)
        d.line((x + wfull / 2, yy, x + 20, yy - 1), fill=(40, 40, 44, 255), width=3); d.line((x + wfull / 2, yy, x + wfull - 20, yy - 1), fill=(40, 40, 44, 255), width=3)
    ibeam(im, x, yy, wfull, h, label, val if p > .95 else "")
def head(im, text, a=1):
    d = ImageDraw.Draw(im); d.text((W / 2, 120), text, font=font("Inter-Black.otf", 62), fill=WHITE + (int(255 * a),), anchor="mm")
    d.rectangle((W / 2 - 120, 165, W / 2 + 120, 173), fill=ORANGE + (int(255 * a),))
def scene2d(var, t, T0, T1):
    u = (t - T0) / (T1 - T0); fr = zoomed(bgdark(), 1 + .05 * u)
    im = Image.fromarray(fr).convert("RGBA"); d = ImageDraw.Draw(im); a = eout((t - T0) / .4)
    sp = T1 - T0; at = lambda f: T0 + f * sp
    if var == "druck":
        head(im, "SPITZENDRUCK IM ZYLINDER", a)
        crane_beam(im, t, at(0), 520, 300, 120 * 4, 80, "Benziner", "> 120 bar")
        crane_beam(im, t, at(.3), 520, 430, 200 * 4, 80, "Diesel", "> 200 bar")
        if t > at(.62):
            p = eout((t - at(.62)) / .6)
            d.text((W / 2, 680), "Kraft auf einen Kolben (Ø 86 mm):", font=font("Inter-Bold.otf", 44), fill=(220, 220, 225, int(255 * p)), anchor="mm")
            crane_beam(im, t, at(.66), 420, 760, 7 * 52, 70, "", "≈ 7 t", .8)
            crane_beam(im, t, at(.74), 420, 860, 12 * 52, 70, "", "≈ 12 t (so viel wiegt ein leerer Linienbus)", .8)
    elif var == "vergleich":
        head(im, "STAHL GEGEN ALUMINIUM", a)
        d.text((W / 2, 290), "Dichte (g/cm³)", font=font("Inter-Bold.otf", 44), fill=(220, 220, 225, int(255 * a)), anchor="mm")
        crane_beam(im, t, at(.02), 560, 340, 7.8 * 90, 70, "Stahl", "7,8"); crane_beam(im, t, at(.15), 560, 430, 2.7 * 90, 70, "Alu", "2,7")
        if t > at(.5):
            d.text((W / 2, 610), "Wärmeleitung (W/mK)", font=font("Inter-Bold.otf", 44), fill=(220, 220, 225, int(255 * eout((t - at(.5)) / .4))), anchor="mm")
            crane_beam(im, t, at(.52), 560, 660, 45 * 4.5, 70, "Stahl", "< 45"); crane_beam(im, t, at(.64), 560, 750, 130 * 4.5, 70, "Alu", "130")
        hinweis(im, "Quelle: MAHLE (Workshop Heroes)")
    elif var == "legierung":
        head(im, "DAS REZEPT: KOLBENLEGIERUNG", a)
        crane_beam(im, t, at(.02), 620, 300, 85 * 9, 80, "Aluminium", "Rest (≈ 85 %)")
        crane_beam(im, t, at(.18), 620, 410, 12 * 9 * 3, 80, "Silizium", "≈ 12 %")
        for k, (n, v) in enumerate((("Kupfer", "≈ 1 %"), ("Nickel", "≈ 1 %"), ("Magnesium", "≈ 1 %"))):
            crane_beam(im, t, at(.5 + k * .1), 620, 520 + k * 100, 1 * 9 * 3, 70, n, v, .8)
        hinweis(im, "Typische Legierung AlSi12CuNiMg, Balken Silizium und Spuren 3× vergrößert")
    elif var == "gefuege":
        head(im, "IM GEFÜGE: AUSHÄRTEN", a)
        r = random.Random(4); cx, cy, R = W / 2 - 200, H / 2 + 60, 330
        z = 1 + .3 * eout(u / .4)
        d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(185, 188, 195, 255), outline=(80, 80, 86, 255), width=6)
        for i in range(26):  # Körner
            x, y = cx + r.uniform(-.8, .8) * R, cy + r.uniform(-.8, .8) * R
            if (x - cx) ** 2 + (y - cy) ** 2 > (R * .85) ** 2: continue
            d.polygon([(x + 60 * z * math.cos(k * 1.1 + i), y + 60 * z * math.sin(k * 1.1 + i)) for k in range(6)], outline=(120, 122, 130, 255))
        pp = eout((u - .4) / .5)
        for i in range(int(260 * pp)):
            x, y = cx + r.uniform(-.85, .85) * R, cy + r.uniform(-.85, .85) * R
            if (x - cx) ** 2 + (y - cy) ** 2 > (R * .92) ** 2: continue
            d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(255, 120, 40, 255))
        # Uhr: Stunden
        ux, uy, ur = W / 2 + 420, H / 2 + 40, 150
        d.ellipse((ux - ur, uy - ur, ux + ur, uy + ur), fill=(30, 30, 34, 255), outline=(200, 200, 205, 255), width=6)
        hh = 6 * u
        d.line((ux, uy, ux + ur * .5 * math.sin(hh * 2 * math.pi / 12), uy - ur * .5 * math.cos(hh * 2 * math.pi / 12)), fill=WHITE, width=10)
        d.line((ux, uy, ux + ur * .85 * math.sin(hh * 2 * math.pi), uy - ur * .85 * math.cos(hh * 2 * math.pi)), fill=ORANGE, width=6)
        d.text((ux, uy + ur + 50), "STUNDEN BEI ≈ 200 °C", font=font("Inter-Bold.otf", 40), fill=WHITE, anchor="mm")
        if pp > .2: d.text((cx, cy + R + 50), "winzige Teilchen (schematisch)", font=font("Inter-Bold.otf", 36), fill=(255, 160, 80, 255), anchor="mm")
    elif var == "haar":
        head(im, "MAKRO: BOLZEN IN DER BOHRUNG", a)
        cx, cy = W / 2 - 330, H / 2 + 60; R = 260
        d.ellipse((cx - R - 30, cy - R - 30, cx + R + 30, cy + R + 30), fill=(170, 172, 178, 255))
        d.ellipse((cx - R - 2, cy - R - 2, cx + R + 2, cy + R + 2), fill=(10, 10, 12, 255))
        d.ellipse((cx - R + 2, cy - R + 2, cx + R - 2, cy + R - 2), fill=(120, 124, 132, 255)); d.ellipse((cx - R * .55, cy - R * .55, cx + R * .55, cy + R * .55), fill=(40, 40, 44, 255))
        d.text((cx, cy + R + 80), "Spalt: 0,002–0,005 mm", font=font("Inter-Black.otf", 48), fill=(255, 160, 80, 255), anchor="mm")
        if u > .5:
            p = eout((u - .5) / .3); hx = W / 2 + 380
            d.ellipse((hx - 90 * p, cy - 90 * p, hx + 90 * p, cy + 90 * p), fill=(70, 45, 25, 255), outline=(150, 110, 70, 255), width=4)
            d.text((hx, cy + 160), "Menschliches Haar", font=font("Inter-Bold.otf", 40), fill=WHITE, anchor="mm")
            d.text((hx, cy + 215), "≈ 20 × dicker als der Spalt", font=font("Inter-Bold.otf", 36), fill=(255, 160, 80, 255), anchor="mm")
        hinweis(im, "Schema, nicht maßstäblich")
    elif var == "formel":
        pl = metal_tex(1500, 520, 3).convert("RGBA"); im.alpha_composite(pl, (210, 280))
        d = ImageDraw.Draw(im); d.rectangle((210, 280, 1710, 800), outline=(80, 82, 88, 255), width=6)
        laser(im, t, at(0), T1, "86 mm × 200 K", y=400, size=80)
        laser(im, t, at(.45), T1, "× 0,00002 /K", y=540, size=80)
        laser(im, t, at(.75), T1, "≈ 0,34 mm", y=690, size=100)
        hinweis(im, "Wärmedehnung Aluminium-Kolbenlegierung ≈ 20·10⁻⁶ /K")
    elif var == "spalt":
        head(im, "MAKRO: KOLBEN UND ZYLINDERWAND", a)
        z = 1 + .6 * ease(u / .8); cx = W / 2; gw = 10 * z
        kol = metal_tex(700, 560, 5).convert("RGBA"); im.alpha_composite(kol, (int(cx - gw / 2 - 700), 300))
        wd = Image.new("RGBA", (700, 560), (70, 72, 78, 255)); im.alpha_composite(wd, (int(cx + gw / 2), 300))
        d = ImageDraw.Draw(im)
        gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).rectangle((cx - gw / 2, 300, cx + gw / 2, 860), fill=(255, 140, 40, 255))
        im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(6))); d = ImageDraw.Draw(im)
        d.text((cx - 380, 580), "Kolben", font=font("Inter-Black.otf", 60), fill=INK, anchor="mm")
        d.text((cx + 380, 580), "Zylinderwand", font=font("Inter-Black.otf", 60), fill=WHITE, anchor="mm")
        bemassung(im, t, at(.15), T1, (cx - gw / 2 - 60, 282, cx + gw / 2 + 60, 282), "0,03–0,04 mm")
        hinweis(im, "Schema, nicht maßstäblich (Einbauspiel Benziner)")
    elif var == "balken":
        head(im, "WACHSTUM GEGEN PLATZ", a)
        crane_beam(im, t, at(.02), 560, 380, 0.34 * 2400, 90, "Kolben wächst", "≈ 0,34 mm")
        crane_beam(im, t, at(.25), 560, 540, 0.035 * 2400, 90, "Spalt", "≈ 0,035 mm")
    elif var == "schicht":
        head(im, "GLEITSCHICHT IM QUERSCHLIFF", a)
        x0, x1 = 360, 1560
        d.rectangle((x0, 640, x1, 860), fill=(150, 152, 160, 255)); d.text((x0 + 30, 750), "Aluminium-Schaft", font=font("Inter-Bold.otf", 40), fill=INK, anchor="lm")
        p = eout((u - .05) / .4); d.rectangle((x0, 640 - 120 * p, x1, 640), fill=(55, 55, 60, 255))
        if p > .9:
            d.text((x0 + 30, 580), "Graphit-Schicht 0,01–0,04 mm", font=font("Inter-Bold.otf", 40), fill=WHITE, anchor="lm")
        if u > .5:
            q = eout((u - .5) / .3); d.rectangle((x0 + 700, 420, x1, 420 + 6 * q), fill=(220, 220, 228, 255))
            d.text((x0 + 700, 380), "Zinn: ≈ 0,001 mm", font=font("Inter-Bold.otf", 40), fill=(255, 160, 80, 255), anchor="lm")
        hinweis(im, "Schema, nicht maßstäblich")
    return im

def endcard(t, T0, T1, second):
    fr = zoomed(bgdark(), 1.05 + .04 * (t - T0) / 12)
    im = Image.fromarray(fr).convert("RGBA"); d = ImageDraw.Draw(im)
    a = eout((t - T0) / .5)
    # Kommentar-Feld
    bx, by = 260, 300
    d.rounded_rectangle((bx, by, bx + 900, by + 220), 18, fill=(245, 243, 238, int(240 * a)))
    d.ellipse((bx + 30, by + 30, bx + 100, by + 100), fill=ORANGE + (int(255 * a),))
    txt = "Welches Bauteil als Nächstes?"; n = int(len(txt) * min(1, max(0, (t - T0 - .4) / 1.6)))
    d.text((bx + 125, by + 65), txt[:n], font=font("Inter-Bold.otf", 46), fill=INK + (int(255 * a),), anchor="lm")
    d.text((bx + 125, by + 150), "Schreib es in die Kommentare", font=font("Inter-Bold.otf", 34), fill=(110, 110, 116, int(255 * a)), anchor="lm")
    if second or t > T0 + 3:
        b = eout((t - (T0 + (0 if second else 3))) / .4)
        sx, sy = 1260, 330
        d.rounded_rectangle((sx, sy, sx + 420, sy + 120), 60, fill=ORANGE + (int(255 * b),))
        d.text((sx + 210, sy + 60), "ABONNIEREN", font=font("Inter-Black.otf", 48), fill=(255, 255, 255, int(255 * b)), anchor="mm")
        # Glocke wackelt
        gx, gy = sx + 210, sy + 250; w_ = math.sin((t - T0) * 14) * 0.35 * max(0, 1 - ((t - T0) % 2.5) / 1.2)
        bell = Image.new("RGBA", (160, 160), (0, 0, 0, 0)); bd = ImageDraw.Draw(bell)
        bd.pieslice((20, 10, 140, 130), 180, 360, fill=(255, 255, 255, int(255 * b))); bd.rectangle((20, 70, 140, 110), fill=(255, 255, 255, int(255 * b)))
        bd.rectangle((10, 108, 150, 118), fill=(255, 255, 255, int(255 * b))); bd.ellipse((66, 118, 94, 146), fill=(255, 255, 255, int(255 * b)))
        bell = bell.rotate(math.degrees(w_), resample=Image.BICUBIC, center=(80, 10)); im.alpha_composite(bell, (int(gx - 80), int(gy - 80)))
    d.text((W / 2, 900), "MEISTERWERK", font=font("Inter-Black.otf", 54), fill=(255, 255, 255, int(200 * a)), anchor="mm")
    d.text((W / 2, 955), "Wie die Dinge wirklich gebaut werden", font=font("Inter-Bold.otf", 32), fill=(200, 200, 205, int(200 * a)), anchor="mm")
    return im

# ---------------- Frame ----------------
EXAG = {"oval3d", "konus3d", "dehnung"}
def beats_abs():
    out = []
    starts = sorted([b["t0"] for b in T["blocks"]] + [c["t0"] for c in T["cards"]] + [T["end"]])
    for b in T["blocks"]:
        t1 = min(x for x in starts if x > b["t0"] + 1e-6); sp = t1 - b["t0"]
        bl = sorted(BEATS.get(b["id"], []), key=lambda x: x[0])
        for j, (fr, kind, prm) in enumerate(bl):
            ta = b["t0"] + fr * sp
            nxt = [b["t0"] + x[0] * sp for x in bl[j + 1:] if x[1] in ("plate", "laser", "count", "call", "dim")]
            te = min([ta + 3.4, t1 - .05] + ([nxt[0] - .02] if nxt and kind in ("plate", "laser", "count", "call", "dim") else []))
            if kind in ("ruck",): te = ta + .45
            if kind == "funken": te = ta + 1.2
            if kind == "dampf": te = ta + 4.0
            if kind == "zoom": te = t1
            out.append((ta, max(te, ta + 1.2), kind, prm, b["id"]))
    return out
BA = beats_abs()
def frame(t):
    for c in T["cards"]:
        if c["t0"] <= t < c["t1"]:
            im = card(t - c["t0"], c["kind"], c.get("num"), c.get("title"))
            return np.array(im.convert("RGB"))
    s = next((x for x in SH if x["t0"] <= t < x["t1"]), SH[0] if t < SH[0]["t0"] else SH[-1])
    T0, T1 = s["t0"], s["t1"]; u = (t - T0) / max(T1 - T0, .01)
    z, cx, cy = 1.0, .5, .5
    for ta, te, kind, prm, bid in BA:
        if kind == "zoom" and ta <= t < te and T0 <= ta < T1:
            z = 1 + (prm["z"] - 1) * ease((t - ta) / max(te - ta, .5)); cx, cy = prm["cx"], prm["cy"]
    if s["scene"] == "endkarte":
        im = endcard(t, T0, T1, s["var"] == "b")
    elif s["art"] == "2d":
        im = scene2d(s["var"], t, T0, T1)
    elif s["art"] == "st":
        fr = still(f"{WK}/r/{s['dir']}/f_0001.png"); fr = zoomed(fr, 1.02 + .08 * ease(u), .45 + .1 * u, .5)
        im = Image.fromarray(fr).convert("RGBA")
    else:
        fr = CLIP.get(s["dir"], int(round((t - T0) * FPS)))
        fr = zoomed(fr, z, cx, cy)
        for ta, te, kind, prm, bid in BA:
            if kind == "ruck" and ta <= t < te:
                x = t - ta; amp = 26 * (1 - x / .45); M = np.float32([[1, 0, amp * math.sin(x * 90)], [0, 1, amp * math.cos(x * 70)]])
                fr = cv2.warpAffine(fr, M, (W, H), borderMode=cv2.BORDER_REFLECT)
        im = Image.fromarray(fr).convert("RGBA")
        if s["scene"] in EXAG or (s["scene"] == "profil" and s["var"] != "geist") or (s["scene"] == "drehbank" and s["var"] == "oszi") or (s["scene"] == "messuhr" and s["var"] != "heiss"):
            hinweis(im, "Schema – Bewegung bzw. Formabweichung stark übertrieben dargestellt")
    for ta, te, kind, prm, bid in BA:
        if not (ta - .01 <= t <= te): continue
        if kind == "plate":
            typenschild(im, t, ta, te, prm["big"], prm["sub"], prm.get("pos", "bl"))
            if "*" in prm["sub"]: ImageDraw.Draw(im).text((W - 40, H - 40), "* nach Herstellerangaben (MAHLE)", font=font("Inter-Bold.otf", 26), fill=(255, 255, 255, 190), anchor="rm")
        elif kind == "laser": laser(im, t, ta, te, prm["text"])
        elif kind == "call" and s["scene"] != "endkarte": callout(im, t, ta, te, prm["xy"], prm["text"], prm.get("side", 1))
        elif kind == "dim": bemassung(im, t, ta, te, prm["box"], prm["label"])
        elif kind == "count": taktuhr(im, t, ta, te, prm["v"], prm["fmt"], prm["label"])
        elif kind == "funken": funken(im, t, ta, te, prm["xy"])
        elif kind == "dampf": dampf(im, t, ta, te)
    if s["scene"] != "endkarte": brand(im)
    return np.array(im.convert("RGB"))

def part(name, t0, t1):
    out = f"{WK}/parts/{name}.mp4"; os.makedirs(WK + "/parts", exist_ok=True)
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", out + ".tmp.mp4"], stdin=subprocess.PIPE)
    n0, n1 = int(round(t0 * FPS)), int(round(t1 * FPS))
    for n in range(n0, n1):
        p.stdin.write(frame(n / FPS).tobytes())
    p.stdin.close(); p.wait(); os.replace(out + ".tmp.mp4", out); print("part", name, "ok", flush=True)

if __name__ == "__main__":
    if sys.argv[1] == "prep": prep()
    elif sys.argv[1] == "part": part(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]))
    elif sys.argv[1] == "still":
        t = float(sys.argv[2]); Image.fromarray(frame(t)).save(sys.argv[3] if len(sys.argv) > 3 else f"{WK}/st_{t:.1f}.jpg", quality=88)
