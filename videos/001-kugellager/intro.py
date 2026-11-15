"""Meisterwerk pilot intro compositor (1920x1080, 24 fps).
Builds frames with PIL, pipes them to ffmpeg, then mixes VO + music + SFX.
"""
import os, math, random, subprocess, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import scipy.io.wavfile as wf

D = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1920, 1080, 24
F = "/usr/share/fonts/opentype/inter/"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
ORANGE = (255, 92, 12); INK = (28, 28, 32); GREY = (110, 110, 116); PAPER = (244, 241, 236)
random.seed(7)
_fc = {}
def font(p, s):
    k = (p, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(p, int(s))
    return _fc[k]
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def eout(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def dur(f): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))

# ---------------- background ----------------
def make_bg():
    bg = Image.new("RGB", (W, H), (226, 222, 216))
    g = Image.new("L", (W, H), 0); ImageDraw.Draw(g).ellipse((W * .15, -H * .1, W * .85, H * 1.1), fill=255)
    bg = Image.composite(Image.new("RGB", (W, H), PAPER), bg, g.filter(ImageFilter.GaussianBlur(240)))
    return bg
BG = make_bg()
SHADOW = Image.new("L", (W, H), 0)
ImageDraw.Draw(SHADOW).ellipse((W / 2 - 300, H * .9 - 34, W / 2 + 300, H * .9 + 34), fill=255)
SHADOW = SHADOW.filter(ImageFilter.GaussianBlur(40)).point(lambda v: v * .35)

# ---------------- media ----------------
_img = {}
def img(name):
    if name not in _img: _img[name] = Image.open(f"{D}/img/{name}.png").convert("RGB")
    return _img[name]
def kenburns(im, t, T, z0=1.0, z1=1.12, cx0=.5, cy0=.5, cx1=.5, cy1=.5):
    x_ = min(max(t / T, 0), 1); p = ease(x_) * .85 + x_ * .15
    z = z0 + (z1 - z0) * p; cx = cx0 + (cx1 - cx0) * p; cy = cy0 + (cy1 - cy0) * p
    s = max(W / im.width, H / im.height) * z
    w, h = im.width * s, im.height * s
    l = (w - W) * cx; tp = (h - H) * cy
    box = (l / s, tp / s, (l + W) / s, (tp + H) / s)
    return im.resize((W, H), Image.BICUBIC, box=box)

_frm = {}
def bframe(clip, idx):
    n = {"kugel": 72, "lager": 120}[clip]
    idx = int(min(max(idx, 1), n))
    k = (clip, idx)
    if k not in _frm:
        if len(_frm) > 60: _frm.clear()
        _frm[k] = Image.open(f"{D}/r_{clip}/f_{idx:04d}.png").convert("RGBA").resize((W, H), Image.LANCZOS)
    return _frm[k]
def blender(clip, pos, zoom=1.0, shadow=True):
    """pos = fractional frame index (blended)"""
    a = bframe(clip, math.floor(pos)); b = bframe(clip, math.floor(pos) + 1); f = pos - math.floor(pos)
    fr = Image.blend(a, b, f) if f > .05 else a
    im = BG.copy()
    if shadow: im = Image.composite(Image.new("RGB", (W, H), (150, 145, 138)), im, SHADOW)
    if zoom > 1.0:
        s = zoom; w, h = int(W * s), int(H * s)
        fr = fr.resize((w, h), Image.BICUBIC).crop(((w - W) // 2, (h - H) // 2, (w - W) // 2 + W, (h - H) // 2 + H))
    elif zoom < 1.0:
        w, h = int(W * zoom), int(H * zoom); small = fr.resize((w, h), Image.BICUBIC)
        fr = Image.new("RGBA", (W, H), (0, 0, 0, 0)); fr.paste(small, ((W - w) // 2, (H - h) // 2 + int(H * .04)))
    im.paste(fr, (0, 0), fr)
    return im
VIELE = None
def viele(t, T):
    global VIELE
    if VIELE is None:
        fr = Image.open(f"{D}/r_viele/f_0001.png").convert("RGBA")
        VIELE = BG.copy(); VIELE.paste(fr, (0, 0), fr)
    return kenburns(VIELE, t, T, 1.05, 1.25, .2, .3, .7, .6)

# ---------------- overlays ----------------
def typed(im, t, t0, lines, xy, size=46, cps=16):
    if t < t0: return
    d = ImageDraw.Draw(im); f = font(MONO, size); x, y = xy; n = int((t - t0) * cps); k = 0
    maxw = max(d.textlength(l, font=f) for l in lines)
    a = eout((t - t0) / .2)
    box = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(box)
    bd.rounded_rectangle((x - 26, y - 20, x - 26 + (maxw + 80) * a, y + len(lines) * (size + 16) + 8), 14, fill=(255, 255, 255, 235))
    bd.rectangle((x - 26, y - 20, x - 20, y + len(lines) * (size + 16) + 8), fill=ORANGE + (255,))
    im.paste(box, (0, 0), box)
    for li, line in enumerate(lines):
        vis = line[:max(0, min(len(line), n - k))]
        d.text((x, y + li * (size + 16)), vis, font=f, fill=INK)
        if 0 <= n - k <= len(line) and int(t * 2.5) % 2 == 0:
            cx = x + d.textlength(vis, font=f) + 4
            d.rectangle((cx, y + li * (size + 16) + 6, cx + size * .5, y + li * (size + 16) + size), fill=ORANGE)
        k += len(line) + 4
def typed_sfx(ev, t0, lines, cps=16, gain=.45):
    k = 0
    for line in lines:
        for ch in line:
            if ch != " ": ev.append((t0 + k / cps, f"key{random.randint(0, 7)}", gain))
            k += 1
        k += 4

def big_number(im, t, t0, value, fmt, xy, size=230, color=ORANGE, sub=None, dur_c=1.2, anchor="mm", panel=False):
    if t < t0: return
    p = eout((t - t0) / dur_c); v = value * p
    txt = fmt(v); d = ImageDraw.Draw(im)
    if panel:
        a = eout((t - t0) / .25); pw = max(d.textlength(fmt(value), font=font(F + "InterDisplay-Black.otf", size)) / 2 + 70, 380)
        bx = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(bx).rounded_rectangle((xy[0] - pw, xy[1] - size * .62, xy[0] + pw, xy[1] + size * .62 + (80 if sub else 0)), 30, fill=(255, 255, 255, int(225 * a)))
        im.paste(bx, (0, 0), bx)
    s = .85 + .15 * eout((t - t0) / .25)
    f = font(F + "InterDisplay-Black.otf", size * s)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((xy[0] + 6, xy[1] + 10), txt, font=f, fill=(0, 0, 0, 70), anchor=anchor)
    im.paste(sh.filter(ImageFilter.GaussianBlur(14)), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)))
    d.text(xy, txt, font=f, fill=color, anchor=anchor)
    if sub:
        a = ease((t - t0 - .3) / .3)
        if a > 0:
            col = tuple(int(c * a + 240 * (1 - a)) for c in INK)
            d.text((xy[0], xy[1] + size * .66), sub, font=font(F + "Inter-SemiBold.otf", 50), fill=col, anchor="mm")

def pill(im, t, t0, text, xy, size=54, t1=None, strike_at=None, color=INK):
    if t < t0 or (t1 and t > t1): return
    a = eout((t - t0) / .18); d = ImageDraw.Draw(im); f = font(F + "InterDisplay-Black.otf", size)
    x, y = xy; y += (1 - a) * 30
    tw = d.textlength(text, font=f)
    box = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle((x - 28, y - 18, x + tw + 28, y + size + 22), 18, fill=(255, 255, 255, int(235 * a)))
    im.paste(box, (0, 0), box)
    d.text((x, y), text, font=f, fill=color)
    if strike_at and t > strike_at:
        p = eout((t - strike_at) / .22)
        d.line((x - 10, y + size * .58, x - 10 + (tw + 20) * p, y + size * .58), fill=ORANGE, width=9)

def brand(im):
    d = ImageDraw.Draw(im)
    d.text((W - 300, H - 70), "MEISTERWERK", font=font(F + "InterDisplay-Black.otf", 26), fill=(70, 70, 74))
    d.rectangle((W - 300, H - 36, W - 250, H - 32), fill=ORANGE)

def measure(im, t, t0, c=(W / 2, H / 2 - 20), r=480):
    if t < t0: return
    p = eout((t - t0) / .9)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    d.arc((c[0] - r, c[1] - r, c[0] + r, c[1] + r), -90, -90 + 360 * p, fill=ORANGE + (255,), width=5)
    if p > .6:
        q = eout((t - t0 - .6) / .5)
        for ang in range(0, 360, 15):
            a = math.radians(ang); r1, r2 = r + 10, r + (30 if ang % 45 == 0 else 20)
            if ang / 360 < p:
                d.line((c[0] + r1 * math.cos(a), c[1] + r1 * math.sin(a), c[0] + r2 * math.cos(a), c[1] + r2 * math.sin(a)), fill=ORANGE + (200,), width=3)
    im.paste(ov, (0, 0), ov)

def hair_compare(im, t, t0):
    if t < t0: return
    a = ease((t - t0) / .4); d = ImageDraw.Draw(im)
    x0, y0 = 120, 690
    box = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle((x0 - 30, y0 - 40, x0 + 620, y0 + 270), 22, fill=(255, 255, 255, int(235 * a)))
    im.paste(box, (0, 0), box)
    f = font(F + "Inter-SemiBold.otf", 36)
    d.text((x0, y0 - 10), "Menschliches Haar", font=f, fill=INK)
    w1 = int(560 * eout((t - t0 - .2) / .6))
    d.rounded_rectangle((x0, y0 + 50, x0 + max(w1, 2), y0 + 50 + 44), 8, fill=(120, 96, 70))
    d.text((x0, y0 + 120), "Erlaubte Abweichung", font=f, fill=INK)
    w2 = int(560 * eout((t - t0 - .9) / .6))
    if w2 > 0: d.rectangle((x0, y0 + 182, x0 + w2, y0 + 182 + 1), fill=ORANGE)
    if t > t0 + 1.4:
        d.text((x0 + 380, y0 + 196), "≈ 1/700", font=font(F + "Inter-Bold.otf", 34), fill=ORANGE)

def vignette_punch(im, t, t_start):
    """quick 6-frame punch-in at each cut"""
    x = (t - t_start)
    if 0 <= x < .25:
        z = 1 + .06 * (1 - eout(x / .25))
        w, h = int(W * z), int(H * z)
        im = im.resize((w, h), Image.BILINEAR).crop(((w - W) // 2, (h - H) // 2, (w - W) // 2 + W, (h - H) // 2 + H))
    return im

def title_card(t):
    im = BG.copy(); d = ImageDraw.Draw(im)
    a = eout(t / .35); s = .9 + .1 * a
    f = font(F + "InterDisplay-Black.otf", 190 * s)
    d.text((W / 2, H / 2 - 40), "DAS KUGELLAGER", font=f, fill=INK, anchor="mm")
    d.rounded_rectangle((W / 2 - 160 * a, H / 2 + 95, W / 2 + 160 * a, H / 2 + 109), 7, fill=ORANGE)
    if t > .5:
        b = ease((t - .5) / .4); col = tuple(int(c * b + 244 * (1 - b)) for c in GREY)
        d.text((W / 2, H / 2 + 175), "Wie die Dinge wirklich gebaut werden", font=font(F + "Inter-SemiBold.otf", 52), fill=col, anchor="mm")
    if t > .9:
        b = ease((t - .9) / .4); col = tuple(int(c * b + 244 * (1 - b)) for c in (70, 70, 74))
        d.text((W / 2, 140), "MEISTERWERK", font=font(F + "InterDisplay-Black.otf", 44), fill=col, anchor="mm")
    return im

# ---------------- timeline ----------------
VO = {i: f"{D}/vo/{i}.mp3" for i in range(1, 11)}
L = {i: dur(VO[i]) for i in VO}
# (scene, lead, vo index, tail)
PLAN = [(1, .5, 1, .3), (2, .1, 2, 1.4), (3, .2, 3, .1), (4, .7, 4, 1.0), (5, .1, 5, .2), (6, .1, 6, .3),
        (7, .1, 7, .1), (8, .1, 8, .2), (9, .1, 9, .3), (10, .2, 10, .3), (11, 0, None, 4.2)]
starts = {}; t = 0; vo_at = {}
for s, lead, v, tail in PLAN:
    starts[s] = t
    if v: vo_at[v] = t + lead
    t += lead + (L[v] if v else 0) + tail
TOTAL = t
S = lambda n: starts[n]
DUR = {s: (starts[s + 1] if s + 1 in starts else TOTAL) - starts[s] for s in starts}
print("total", round(TOTAL, 2), {k: round(v, 2) for k, v in starts.items()}, {k: round(v, 2) for k, v in vo_at.items()})

def frame(t):
    sc = max(s for s in starts if starts[s] <= t); lt = t - starts[sc]; T = DUR[sc]; v = vo_at.get(sc, starts[sc]); vt = t - v
    if sc == 1:
        im = kenburns(img("bomber_town"), lt, T, 1.0, 1.16, .5, .3, .55, .55)
        typed(im, t, starts[1] + .6, ["14.10.1943", "291 BOMBER"], (120, 120))
    elif sc == 2:
        im = kenburns(img("bomber_sky"), lt, T, 1.08, 1.2, .3, .5, .6, .45)
        big_number(im, t, v + .9, 60, lambda x: f"{int(round(x))}", (W / 2, H / 2 - 40), sub="kehren nicht zurück", dur_c=.9, panel=True)
    elif sc == 3:
        im = kenburns(img("map"), lt, T, 1.0, 1.35, .5, .5, .6, .62)
        pill(im, t, v + .4, "WAFFENFABRIK", (120, 150), strike_at=v + 1.7)
        pill(im, t, v + 2.35, "FLUGHAFEN", (120, 270), strike_at=v + 3.0)
        pill(im, t, v + 3.55, "GROSSSTADT", (120, 390), strike_at=v + 4.3)
        typed(im, t, v + 5.1, ["ZIEL: SCHWEINFURT"], (1180, 820))
    elif sc == 4:
        im = blender("kugel", 1 + lt * 24 * .9, zoom=1.0)
    elif sc == 5:
        if vt < 3.0:
            im = blender("kugel", min(72, 1 + (lt + DUR[4]) * 24 * .9), zoom=1 + .03 * vt)
        else:
            x = vt - 3.0
            im = blender("lager", 1 + x * 24 * .85, zoom=.8 + .2 * ease(x / 3.0))
            for i, (w_, at) in enumerate([("MOTOR", 6.9), ("PROPELLER", 7.8), ("PANZERKETTE", 8.9)]):
                pill(im, t, v + at - .2, w_, (130, 200 + i * 120), size=58)
    elif sc == 6:
        im = viele(lt, T)
        big_number(im, t, v + 2.0, 30, lambda x: f"≈ {int(round(x))} MILLIARDEN", (W / 2, H / 2 - 60), size=150, sub="Wälzlager pro Jahr – allein in China", dur_c=1.6, panel=True)
    elif sc == 7:
        cuts = [(0, "car", "AUTO"), (vt and 1.5, "washer", "WASCHMASCHINE"), (2.9, "bike", "FAHRRAD")]
        if vt < 4.4:
            k = 0 if vt < 1.6 else (1 if vt < 3.1 else 2)
            name = ["car", "washer", "bike"][k]; c0 = [0, 1.6, 3.1][k]
            im = kenburns(img(name), vt - c0, 1.6, 1.0, 1.1)
            im = vignette_punch(im, vt, c0)
            pill(im, t, v + c0 + .1, ["AUTO", "WASCHMASCHINE", "FAHRRAD"][k], (120, 120), size=52)
        else:
            x = vt - 4.4
            im = blender("lager", 120 - x * 24 * .7, zoom=1.0)
            im = vignette_punch(im, vt, 4.4)
    elif sc == 8:
        im = blender("kugel", 72 - lt * 24 * .45, zoom=1.0)
        if vt > 2.2:
            pill(im, t, v + 2.3, "MILLIONENFACH", (120, 150), size=54)
            pill(im, t, v + 3.6, "JEDE EXAKT GLEICH", (120, 270), size=54)
    elif sc == 9:
        im = blender("kugel", 40, zoom=1.0)
        measure(im, t, v + .3)
        big_number(im, t, v + 3.0, 1, lambda x: "< 0,0001 mm", (W / 2, 110), size=96, dur_c=.3, panel=True)
        hair_compare(im, t, v + 5.9)
    elif sc == 10:
        if vt < 4.8:
            im = blender("lager", 60 - vt * 24 * .5, zoom=1 - .2 * ease(vt / 4.8))
        else:
            im = kenburns(img("map"), vt - 4.8, T - 4.8, 1.2, 1.5, .55, .6, .62, .65)
            im = vignette_punch(im, vt, 4.8)
            typed(im, t, v + 5.2, ["SCHWEINFURT, 1883", "FRIEDRICH FISCHER"], (1100, 780))
    else:
        im = title_card(lt)
    if sc != 11:
        if sc not in (7, 10): im = vignette_punch(im, lt, 0)
        brand(im)
    return im

def sfx_events():
    ev = []
    typed_sfx(ev, S(1) + .6, ["14.10.1943", "291 BOMBER"])
    ev += [(vo_at[2] + .9, "boom", .55), (vo_at[2] + .9, "sub_drop", .5)]
    for at, st in [(.4, 1.7), (2.35, 3.0), (3.55, 4.3)]:
        ev += [(vo_at[3] + at, "mclick", .35), (vo_at[3] + st, "slap", .25)]
    typed_sfx(ev, vo_at[3] + 5.1, ["ZIEL: SCHWEINFURT"])
    ev += [(S(4), "braam", .6), (S(4) + .05, "clink", .55), (S(4) + .4, "clink", .25)]
    ev += [(vo_at[5] + 3.0, "roll", .5), (vo_at[5] + 5.0, "clink", .35), (vo_at[5] + 5.3, "mclick", .4)]
    for at in (6.7, 7.6, 8.7): ev.append((vo_at[5] + at, "mclick", .45))
    ev += [(vo_at[6] + 2.0, "tick", .35), (vo_at[6] + 2.0, "whoosh", .25)]
    for c in (0, 1.6, 3.1): ev += [(vo_at[7] + c, "clink", .3), (vo_at[7] + c + .1, "mclick", .3)]
    ev += [(vo_at[7] + 4.4, "clink", .2)]
    ev += [(vo_at[8] + 2.3, "mclick", .4), (vo_at[8] + 3.6, "mclick", .4)]
    ev += [(vo_at[9] + 3.0, "tick", .45), (vo_at[9] + 5.9, "mclick", .35)]
    ev += [(vo_at[10] + .2, "hiss", .3), (vo_at[10] + 4.8, "clink", .3)]
    typed_sfx(ev, vo_at[10] + 5.2, ["SCHWEINFURT, 1883", "FRIEDRICH FISCHER"])
    ev += [(S(11) - 1.6, "riser", .5), (S(11), "braam", .7), (S(11), "boom", .4)]
    return ev

def render_video(path):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    n = int(TOTAL * FPS)
    for i in range(n):
        p.stdin.write(frame(i / FPS).convert("RGB").tobytes())
        if i % 240 == 0: print("frame", i, "/", n, flush=True)
    p.stdin.close(); p.wait()

SR = 48000
def load(path):
    tmp = "/tmp/_a.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-ar", str(SR), "-ac", "2", tmp], check=True)
    return wf.read(tmp)[1].astype(np.float32) / 32768

def mix(path):
    N = int((TOTAL + .5) * SR)
    voice = np.zeros((N, 2), np.float32)
    for v, at in vo_at.items():
        a = load(VO[v]); i = int(at * SR); voice[i:i + len(a)] += a[:N - i]
    # loudness-ish normalise voice
    voice *= .5 / (np.sqrt(np.mean(voice ** 2)) * 4 + 1e-9)
    music = np.zeros((N, 2), np.float32)
    cold = load(f"{D}/music/coldopen_tension.mp3"); drive = load(f"{D}/music/industrial_drive.mp3")
    a, b = 0, int(S(4) * SR); seg = cold[:b - a]; music[a:a + len(seg)] += seg
    fo = int(.4 * SR); music[b - fo:b] *= np.linspace(1, 0, fo)[:, None]
    seg = drive[:N - b]; seg = seg.copy(); seg[:int(.05 * SR)] *= np.linspace(0, 1, int(.05 * SR))[:, None]; music[b:b + len(seg)] += seg
    env = np.ones(N, np.float32)
    # dip after "60 kehren nicht zurück" (beat) and before the title
    for d0, d1 in [(vo_at[2] + L[2] + .1, S(4))]:
        i0, i1 = int(d0 * SR), int(d1 * SR); env[i0:i1] = .15; r = int(.3 * SR); env[i0 - r:i0] = np.minimum(env[i0 - r:i0], np.linspace(1, .15, r))
    i0 = int((S(11) - .3) * SR); env[i0:] = 1.25
    # sidechain-ish ducking under the voice
    vamp = np.abs(voice[:, 0]); k = int(.15 * SR)
    vs = np.convolve(vamp, np.ones(k) / k, mode="same")
    duck = 1 - .55 * np.clip(vs / (vs.max() * .25 + 1e-9), 0, 1)
    music *= (env * duck)[:, None] * .32
    end_f = int((TOTAL - 1.2) * SR); music[end_f:] *= np.linspace(1, 0, N - end_f)[:, None]
    fx = np.zeros((N, 2), np.float32)
    for at, name, g in sfx_events():
        s = load(f"{D}/sfx/{name}.wav") if not name.startswith("key") else load(f"{D}/sfx/{name}.wav")
        if name.startswith("key"): g *= .75
        i = int(at * SR)
        if i < 0 or i >= N: continue
        fx[i:i + len(s)] += s[:N - i] * g
    out = voice + music + fx * .8
    out = np.tanh(out * 1.1) * .95
    wf.write(path, SR, (out * 32767).astype(np.int16))

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode == "still":
        for tt in map(float, sys.argv[2:]):
            frame(tt).save(f"{D}/t/still_{tt:05.1f}.jpg", quality=85)
    else:
        render_video(f"{D}/build_video.mp4"); mix(f"{D}/build_audio.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{D}/build_video.mp4", "-i", f"{D}/build_audio.wav", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-shortest", f"{D}/Meisterwerk_Pilot_Intro.mp4"], check=True)
        print("done")
