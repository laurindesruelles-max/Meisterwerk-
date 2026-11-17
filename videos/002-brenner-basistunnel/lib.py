"""Meisterwerk 002 – compositor helpers (based on 001 intro.py / main.py)."""
import os, math, random, subprocess, json, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = os.path.dirname(os.path.abspath(__file__))
WORK = os.environ.get("MW_WORK", "/home/claude/mw-work/002")
SFX = os.environ.get("MW_SFX", "/home/claude/mw-work/sfx")
MUS = os.environ.get("MW_MUSIC", "/home/claude/mw-work/music")
W, H, FPS = 1920, 1080, 24
F = "/usr/share/fonts/opentype/inter/"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
BLACKF = F + "InterDisplay-Black.otf"; BOLD = F + "Inter-Bold.otf"; SEMI = F + "Inter-SemiBold.otf"
ORANGE = (255, 92, 12); INK = (28, 28, 32); GREY = (110, 110, 116); PAPER = (244, 241, 236); LIGHT = (205, 200, 192)
ROCKC = (120, 108, 96); TUBE = (90, 92, 98)
_fc = {}
def font(p, s):
    k = (p, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(p, int(s))
    return _fc[k]
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def eout(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def lerp(a, b, t): return a + (b - a) * t
def dur(f): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))
def pw(vt, pts):
    if vt <= pts[0][0]: return pts[0][1]
    for (a, fa), (b, fb) in zip(pts, pts[1:]):
        if vt <= b: return fa + (fb - fa) * (vt - a) / (b - a)
    return pts[-1][1]

def make_bg():
    bg = Image.new("RGB", (W, H), (226, 222, 216))
    g = Image.new("L", (W, H), 0); ImageDraw.Draw(g).ellipse((W * .15, -H * .1, W * .85, H * 1.1), fill=255)
    return Image.composite(Image.new("RGB", (W, H), PAPER), bg, g.filter(ImageFilter.GaussianBlur(240)))
BG = make_bg()
SHADOW = Image.new("L", (W, H), 0)
ImageDraw.Draw(SHADOW).ellipse((W / 2 - 520, H * .86 - 40, W / 2 + 520, H * .86 + 40), fill=255)
SHADOW = SHADOW.filter(ImageFilter.GaussianBlur(50)).point(lambda v: v * .3)

# ---------- media ----------
_img = {}
def img(name):
    if name not in _img: _img[name] = Image.open(f"{WORK}/img/{name}.png").convert("RGB")
    return _img[name]
def kenburns(im, t, T, z0=1.0, z1=1.12, cx0=.5, cy0=.5, cx1=.5, cy1=.5):
    x_ = min(max(t / max(T, .01), 0), 1); p = ease(x_) * .85 + x_ * .15
    z = z0 + (z1 - z0) * p; cx = cx0 + (cx1 - cx0) * p; cy = cy0 + (cy1 - cy0) * p
    s = max(W / im.width, H / im.height) * z
    w, h = im.width * s, im.height * s
    l = (w - W) * cx; tp = (h - H) * cy
    return im.resize((W, H), Image.BICUBIC, box=(l / s, tp / s, (l + W) / s, (tp + H) / s))

_files = {}; _cache = {}
def frames(name):
    if name not in _files: _files[name] = sorted(glob.glob(f"{WORK}/r/{name}/f_*.png"))
    return _files[name]
def frame_rgba(name, i):
    fs = frames(name); i = int(min(max(i, 0), len(fs) - 1)); k = (name, i)
    if k not in _cache:
        if len(_cache) > 40: _cache.clear()
        _cache[k] = Image.open(fs[i]).convert("RGBA").resize((W, H), Image.LANCZOS)
    return _cache[k]
def clip(name, u, zoom=1.0, cx=.5, cy=.5, shadow=True, tint=None):
    """u = progress 0..1 through the rendered clip"""
    n = len(frames(name)); pos = min(max(u, 0), 1) * (n - 1)
    a = frame_rgba(name, math.floor(pos)); f = pos - math.floor(pos)
    if f > .05 and math.floor(pos) + 1 < n: a = Image.blend(a, frame_rgba(name, math.floor(pos) + 1), f)
    im = BG.copy()
    if shadow: im = Image.composite(Image.new("RGB", (W, H), (160, 154, 146)), im, SHADOW)
    if zoom > 1:
        w, h = int(W * zoom), int(H * zoom); l = int((w - W) * cx); t = int((h - H) * cy)
        a = a.resize((w, h), Image.BICUBIC).crop((l, t, l + W, t + H))
    elif zoom < 1:
        w, h = int(W * zoom), int(H * zoom); s = a.resize((w, h), Image.BICUBIC)
        a = Image.new("RGBA", (W, H), (0, 0, 0, 0)); a.paste(s, ((W - w) // 2, (H - h) // 2 + int(H * .04)))
    im.paste(a, (0, 0), a)
    if tint: im = Image.blend(im, Image.new("RGB", (W, H), tint[0]), tint[1])
    return im
def anchors(name):
    p = f"{WORK}/r/{name}/anchors.json"
    return json.load(open(p)) if os.path.exists(p) else {}

# ---------- overlays ----------
def panel(im, box, a=1.0, r=22, fill=(255, 255, 255), alpha=235):
    bx = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(bx).rounded_rectangle(box, r, fill=fill + (int(alpha * a),))
    im.paste(bx, (0, 0), bx)

def typed(im, t, t0, lines, xy, size=46, cps=16):
    if t < t0: return
    d = ImageDraw.Draw(im); f = font(MONO, size); x, y = xy; n = int((t - t0) * cps); k = 0
    maxw = max(d.textlength(l, font=f) for l in lines)
    a = eout((t - t0) / .2)
    panel(im, (x - 26, y - 20, x - 26 + (maxw + 80) * a, y + len(lines) * (size + 16) + 8), 1, 14)
    ImageDraw.Draw(im).rectangle((x - 26, y - 20, x - 20, y + len(lines) * (size + 16) + 8), fill=ORANGE)
    d = ImageDraw.Draw(im)
    for li, line in enumerate(lines):
        vis = line[:max(0, min(len(line), n - k))]
        d.text((x, y + li * (size + 16)), vis, font=f, fill=INK)
        if 0 <= n - k <= len(line) and int(t * 2.5) % 2 == 0:
            cx = x + d.textlength(vis, font=f) + 4
            d.rectangle((cx, y + li * (size + 16) + 6, cx + size * .5, y + li * (size + 16) + size), fill=ORANGE)
        k += len(line) + 4

def big_number(im, t, t0, value, fmt, xy, size=200, color=ORANGE, sub=None, dur_c=1.0, panel_=True):
    if t < t0: return
    p = eout((t - t0) / dur_c); txt = fmt(value * p); d = ImageDraw.Draw(im)
    if panel_:
        a = eout((t - t0) / .25); pw_ = max(d.textlength(fmt(value), font=font(BLACKF, size)) / 2 + 70, 380)
        if sub: pw_ = max(pw_, d.textlength(sub, font=font(SEMI, 50)) / 2 + 60)
        panel(im, (xy[0] - pw_, xy[1] - size * .62, xy[0] + pw_, xy[1] + size * .62 + (80 if sub else 0)), a, 30)
    s = .85 + .15 * eout((t - t0) / .25); f = font(BLACKF, size * s)
    d = ImageDraw.Draw(im); d.text(xy, txt, font=f, fill=color, anchor="mm")
    if sub:
        a = ease((t - t0 - .3) / .3)
        if a > 0:
            col = tuple(int(c * a + 240 * (1 - a)) for c in INK)
            d.text((xy[0], xy[1] + size * .66), sub, font=font(SEMI, 50), fill=col, anchor="mm")

def pill(im, t, t0, text, xy, size=54, t1=None, strike_at=None, color=INK, anchor="l"):
    if t < t0 or (t1 and t > t1): return
    a = eout((t - t0) / .18); d = ImageDraw.Draw(im); f = font(BLACKF, size)
    x, y = xy; y += (1 - a) * 30
    tw = d.textlength(text, font=f)
    if anchor == "m": x -= tw / 2
    elif anchor == "r": x -= tw
    panel(im, (x - 28, y - 18, x + tw + 28, y + size + 22), a, 18)
    d = ImageDraw.Draw(im); d.text((x, y), text, font=f, fill=color)
    if strike_at and t > strike_at:
        p = eout((t - strike_at) / .22)
        d.line((x - 10, y + size * .58, x - 10 + (tw + 20) * p, y + size * .58), fill=ORANGE, width=9)

def pills(im, t, items, x=110, y0=150, step=115, size=50):
    """items: list of (t0, text[, color])"""
    for i, it in enumerate(items):
        pill(im, t, it[0], it[1], (x, y0 + i * step), size=size, color=it[2] if len(it) > 2 else INK)

def callout(im, t, t0, xy, text, side=1, length=260, size=44):
    if t < t0: return
    p = eout((t - t0) / .35); d = ImageDraw.Draw(im)
    d.ellipse((xy[0] - 10, xy[1] - 10, xy[0] + 10, xy[1] + 10), fill=ORANGE)
    ex = xy[0] + side * length * p; d.line((xy[0], xy[1], ex, xy[1]), fill=ORANGE, width=5)
    if p > .7:
        f = font(BOLD, size); tw = d.textlength(text, font=f)
        tx = ex + 16 if side > 0 else ex - 16 - tw
        panel(im, (tx - 14, xy[1] - size * .75, tx + tw + 14, xy[1] + size * .75), 1, 12)
        ImageDraw.Draw(im).text((tx, xy[1]), text, font=f, fill=INK, anchor="lm")

def brand(im):
    d = ImageDraw.Draw(im)
    d.text((W - 300, H - 70), "MEISTERWERK", font=font(BLACKF, 26), fill=(70, 70, 74))
    d.rectangle((W - 300, H - 36, W - 250, H - 32), fill=ORANGE)

def punch(im, x, d=.25, amt=.06):
    if 0 <= x < d:
        z = 1 + amt * (1 - eout(x / d)); w, h = int(W * z), int(H * z)
        im = im.resize((w, h), Image.BILINEAR).crop(((w - W) // 2, (h - H) // 2, (w - W) // 2 + W, (h - H) // 2 + H))
    return im
def shake(im, t, t0, amp=22, d=.4):
    x = t - t0
    if 0 <= x < d:
        a = amp * (1 - x / d); dx = int(a * math.sin(x * 90)); dy = int(a * math.cos(x * 70))
        return im.transform(im.size, Image.AFFINE, (1, 0, dx, 0, 1, dy), resample=Image.BILINEAR, fillcolor=(236, 232, 226))
    return im
def flash(im, t, t0, d=.25, col=(255, 240, 220)):
    x = t - t0
    if 0 <= x < d: return Image.blend(im, Image.new("RGB", (W, H), col), .75 * (1 - x / d))
    return im
def sparks(im, t, t0, t1, xy, n=60, spread=(-2.6, -0.3), speed=900, seed=1, col=(255, 190, 70)):
    if t < t0 or t > t1 + .6: return
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); rnd = random.Random(seed)
    for i in range(n * 3):
        born = t0 + rnd.random() * (t1 - t0); age = t - born
        if age < 0 or age > .45: continue
        a = rnd.uniform(*spread); v = speed * rnd.uniform(.4, 1.2)
        x = xy[0] + math.cos(a) * v * age; y = xy[1] + math.sin(a) * v * age + 1400 * age * age
        d.line((x - math.cos(a) * 18, y - math.sin(a) * 18 - 30 * age, x, y), fill=col + (int(255 * (1 - age / .45)),), width=3)
    g = ov.filter(ImageFilter.GaussianBlur(4)); im.paste(g, (0, 0), g); im.paste(ov, (0, 0), ov)
def dust(im, t, t0, xy, n=40, seed=3, dur_=1.6):
    x_ = t - t0
    if x_ < 0 or x_ > dur_: return
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); rnd = random.Random(seed)
    for i in range(n):
        a = rnd.uniform(0, 2 * math.pi); v = rnd.uniform(80, 420); r = 30 + 90 * x_ * rnd.uniform(.5, 1.5)
        x = xy[0] + math.cos(a) * v * x_; y = xy[1] + math.sin(a) * v * x_ * .6
        al = int(120 * (1 - x_ / dur_))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(150, 140, 128, al))
    ov = ov.filter(ImageFilter.GaussianBlur(18)); im.paste(ov, (0, 0), ov)

def arrow(d, p0, p1, col=ORANGE, w=8, head=26):
    d.line((p0, p1), fill=col, width=w)
    a = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    d.polygon([p1, (p1[0] - head * math.cos(a - .45), p1[1] - head * math.sin(a - .45)), (p1[0] - head * math.cos(a + .45), p1[1] - head * math.sin(a + .45))], fill=col)
def dim_v(d, x, y0, y1, label, col=ORANGE, size=40, side=1):
    d.line((x, y0, x, y1), fill=col, width=4)
    for y in (y0, y1): d.line((x - 16, y, x + 16, y), fill=col, width=4)
    d.text((x + side * 26, (y0 + y1) / 2), label, font=font(BOLD, size), fill=col, anchor="lm" if side > 0 else "rm")
def dim_h(d, y, x0, x1, label, col=ORANGE, size=40, below=False):
    d.line((x0, y, x1, y), fill=col, width=4)
    for x in (x0, x1): d.line((x, y - 16, x, y + 16), fill=col, width=4)
    d.text(((x0 + x1) / 2, y + 22 if below else y - 22), label, font=font(BOLD, size), fill=col, anchor="mt" if below else "mb")

def chapter_card(t, num, title):
    im = BG.copy(); d = ImageDraw.Draw(im); a = eout(t / .4)
    d.text((W / 2, H / 2 - 120), f"KAPITEL {num}", font=font(BOLD, 44), fill=tuple(int(c * a + 244 * (1 - a)) for c in GREY), anchor="mm")
    d.text((W / 2, H / 2 + 10), title.upper(), font=font(BLACKF, 160 * (.92 + .08 * a)), fill=INK, anchor="mm")
    d.rounded_rectangle((W / 2 - 140 * a, H / 2 + 120, W / 2 + 140 * a, H / 2 + 134), 7, fill=ORANGE)
    return im

def title_card(t, title, sub):
    im = BG.copy(); d = ImageDraw.Draw(im)
    a = eout(t / .35); s = .9 + .1 * a
    d.text((W / 2, H / 2 - 40), title, font=font(BLACKF, 150 * s), fill=INK, anchor="mm")
    d.rounded_rectangle((W / 2 - 160 * a, H / 2 + 75, W / 2 + 160 * a, H / 2 + 89), 7, fill=ORANGE)
    if t > .5:
        b = ease((t - .5) / .4); col = tuple(int(c * b + 244 * (1 - b)) for c in GREY)
        d.text((W / 2, H / 2 + 160), sub, font=font(SEMI, 52), fill=col, anchor="mm")
    if t > .9:
        b = ease((t - .9) / .4); col = tuple(int(c * b + 244 * (1 - b)) for c in (70, 70, 74))
        d.text((W / 2, 140), "MEISTERWERK", font=font(BLACKF, 44), fill=col, anchor="mm")
    return im

# ---------- audio ----------
SR = 48000
def load(path):
    tmp = "/tmp/_mw_a.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-ar", str(SR), "-ac", "2", tmp], check=True)
    import scipy.io.wavfile as wf
    return wf.read(tmp)[1].astype(np.float32) / 32768
def typed_sfx(ev, t0, lines, cps=16, gain=.45, rnd=random.Random(5)):
    k = 0
    for line in lines:
        for ch in line:
            if ch != " ": ev.append((t0 + k / cps, f"key{rnd.randint(0, 7)}", gain))
            k += 1
        k += 4
