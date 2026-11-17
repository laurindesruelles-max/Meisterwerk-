"""2D diagrams for Meisterwerk 002 (drawn with PIL in the channel look)."""
from lib import *

# ---------------- map ----------------
CITIES = {"München": (11.58, 48.14), "Rosenheim": (12.13, 47.86), "Kufstein": (12.17, 47.58), "Innsbruck": (11.40, 47.27),
          "Brenner": (11.51, 47.00), "Franzensfeste": (11.61, 46.79), "Bozen": (11.35, 46.50), "Verona": (10.99, 45.44)}
def mxy(lon, lat): return (430 + (lon - 10.9) * 700, 80 + (48.35 - lat) * 330)
_mapbase = None
def map_base():
    global _mapbase
    if _mapbase is None:
        im = BG.copy(); ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        rnd = random.Random(2)
        for i in range(140):  # alps as soft triangles
            lat = rnd.uniform(46.2, 47.45); lon = rnd.uniform(10.0, 13.6)
            x, y = mxy(lon, lat); s = rnd.uniform(26, 60)
            d.polygon([(x - s, y + s * .6), (x, y - s * .7), (x + s, y + s * .6)], fill=(178, 170, 160, 120))
            d.polygon([(x - s * .28, y - s * .7 * .5), (x, y - s * .7), (x + s * .28, y - s * .7 * .5)], fill=(250, 250, 250, 150))
        im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
        # borders (schematic)
        for pts, lab, lp in (([(10.2, 47.55), (11.2, 47.42), (12.0, 47.62), (12.25, 47.70), (13.0, 47.47)], "DEUTSCHLAND", (10.35, 47.95)),
                             ([(10.4, 46.85), (11.0, 46.80), (11.51, 47.00), (12.2, 46.95), (12.8, 46.65)], "ITALIEN", (10.35, 46.0))):
            P = [mxy(*p) for p in pts]
            for a_, b_ in zip(P, P[1:]):
                n = int(math.dist(a_, b_) / 18)
                for k in range(0, n, 2):
                    d.line((lerp(a_[0], b_[0], k / n), lerp(a_[1], b_[1], k / n), lerp(a_[0], b_[0], (k + 1) / n), lerp(a_[1], b_[1], (k + 1) / n)), fill=(150, 140, 130), width=4)
            d.text(mxy(*lp), lab, font=font(BOLD, 34), fill=(150, 140, 130))
        d.text(mxy(12.55, 47.25), "ÖSTERREICH", font=font(BOLD, 34), fill=(150, 140, 130))
        _mapbase = im
    return _mapbase.copy()

def map_diagram(t, mode="route", p=1.0):
    im = map_base(); d = ImageDraw.Draw(im)
    order = ["München", "Rosenheim", "Kufstein", "Innsbruck", "Brenner", "Franzensfeste", "Bozen", "Verona"]
    P = {k: mxy(*v) for k, v in CITIES.items()}
    for a_, b_ in zip(order, order[1:]):
        d.line((P[a_], P[b_]), fill=(120, 120, 126), width=7)
    if mode in ("tunnel", "zulauf", "de"):
        q = eout(p) if mode == "tunnel" else 1
        a_, b_ = P["Innsbruck"], P["Franzensfeste"]
        d.line((a_, (lerp(a_[0], b_[0], q), lerp(a_[1], b_[1], q))), fill=ORANGE, width=18)
    if mode in ("zulauf", "de"):
        # south feeder: under construction (solid orange-ish), north feeder: planned (dashed)
        a_, b_ = P["Franzensfeste"], P["Verona"]
        d.line((a_, P["Bozen"], b_), fill=(255, 160, 90), width=10)
        pts = [P["München"], P["Rosenheim"], P["Kufstein"], P["Innsbruck"]]
        blink = .5 + .5 * math.sin(t * 6) if mode == "de" else 1
        for a_, b_ in zip(pts, pts[1:]):
            n = int(math.dist(a_, b_) / 16)
            for k in range(0, n, 2):
                d.line((lerp(a_[0], b_[0], k / n), lerp(a_[1], b_[1], k / n), lerp(a_[0], b_[0], (k + 1) / n), lerp(a_[1], b_[1], (k + 1) / n)),
                       fill=tuple(int(lerp(200, c, blink)) for c in (200, 30, 30)), width=12)
    for k in order:
        x, y = P[k]; r = 13 if k not in ("Innsbruck", "Franzensfeste") else 17
        d.ellipse((x - r, y - r, x + r, y + r), fill=PAPER, outline=INK, width=5)
        side = -1 if k in ("Innsbruck", "Bozen", "Verona", "München") else 1
        d.text((x + side * 30, y), k.upper(), font=font(BOLD, 34), fill=INK, anchor="rm" if side < 0 else "lm")
    return im

# ---------------- elevation profile ----------------
def profile(t, stage="old", p_old=1.0, p_tun=0.0):
    im = BG.copy(); d = ImageDraw.Draw(im)
    x0, x1, yb = 180, 1740, 900
    def Y(h): return yb - (h - 400) * 0.62   # 400 m .. 1500 m
    def hill(x):
        u = (x - x0) / (x1 - x0)
        return 600 + 1500 * math.exp(-((u - .5) ** 2) / .05) + 60 * math.sin(u * 40)
    poly = [(x0, yb)] + [(x, Y(min(hill(x), 2600)) if Y(hill(x)) > 80 else 80) for x in range(x0, x1 + 1, 8)] + [(x1, yb)]
    d.polygon(poly, fill=(206, 199, 190)); d.line(poly[1:-1], fill=(170, 160, 150), width=3)
    # old line: Innsbruck 582 m -> pass 1371 -> Franzensfeste ~ 750 m
    def old(u): return 582 + (1371 - 582) * min(1, u / .5) if u < .5 else 1371 - (1371 - 750) * (u - .5) / .5
    def tun(u): return 600 + (794 - 600) * min(1, u / .58) if u < .58 else 794 - (794 - 750) * (u - .58) / .42
    def xx(u): return x0 + 40 + (x1 - x0 - 80) * u
    n = int(120 * p_old)
    if n > 1: d.line([(xx(i / 120), Y(old(i / 120))) for i in range(n + 1)], fill=INK, width=9)
    if stage in ("both",):
        n = int(120 * p_tun)
        if n > 1: d.line([(xx(i / 120), Y(tun(i / 120))) for i in range(n + 1)], fill=ORANGE, width=14)
    for lab, u in (("INNSBRUCK", 0), ("BRENNERPASS  1.371 m", .5), ("FRANZENSFESTE", 1)):
        y = Y(old(u)); x = xx(u)
        d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=PAPER, outline=INK, width=5)
        d.text((x, y - 34 if u == .5 else y + 60), lab, font=font(BOLD, 34), fill=INK, anchor="mb" if u == .5 else "mm")
    d.text((x0, yb + 40), "Höhenprofil, schematisch (überhöht)", font=font(SEMI, 28), fill=GREY)
    return im, (xx, Y, old, tun)

# ---------------- cross section ----------------
def cross_section(t, stage=1, t_stage=9.0, press=0.0):
    im = BG.copy(); ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    d.rounded_rectangle((260, 120, 1660, 1000), 40, fill=ROCKC + (90,))
    rnd = random.Random(4)
    for i in range(160):
        x, y = rnd.uniform(280, 1640), rnd.uniform(140, 980); r = rnd.uniform(4, 14)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(100, 90, 80, 70))
    im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
    cx, cy, R = W / 2, 420, 150
    for k, sx in enumerate((-1, 1)):
        a = eout(t_stage / .5) if stage >= 1 else 0
        if a <= 0: continue
        x = cx + sx * 330; r = R * (.6 + .4 * a)
        d.ellipse((x - r - 18, cy - r - 18, x + r + 18, cy + r + 18), fill=(150, 148, 144))
        d.ellipse((x - r, cy - r, x + r, cy + r), fill=PAPER)
        d.rectangle((x - r * .75, cy + r * .55, x + r * .75, cy + r * .62), fill=(90, 90, 96))
        d.text((x, cy - r - 60), "RICHTUNG ITALIEN" if sx < 0 else "RICHTUNG ÖSTERREICH", font=font(BOLD, 30), fill=GREY, anchor="mm")
    if stage >= 1 and t_stage > .6:
        dim_h(d, cy + R + 50, cx - 330 - R, cx - 330 + R, "8,1 m", size=44, below=True)
    if stage >= 2:
        a = eout(t_stage / .5)
        x, y = cx, cy + 270; r = 70 * a
        if r > 2:
            d.ellipse((x - r - 12, y - r - 12, x + r + 12, y + r + 12), fill=(150, 148, 144)); d.ellipse((x - r, y - r, x + r, y + r), fill=ORANGE)
        if t_stage > .7:
            dim_v(d, cx - 110, cy, y, "12 m TIEFER", size=40, side=-1)
            d.text((x, y + 120), "ERKUNDUNGSSTOLLEN", font=font(BLACKF, 44), fill=ORANGE, anchor="mm")
    if stage == 3:  # cross passage
        p = eout(t_stage / .6)
        d.rectangle((cx - 330 + R, cy - 40, cx - 330 + R + (660 - 2 * R) * p, cy + 40), fill=(255, 196, 60))
        if t_stage > .8: d.text((cx, cy - 80), "QUERSCHLAG", font=font(BLACKF, 44), fill=INK, anchor="mm")
    if press > 0:
        for k in range(10):
            a_ = k / 10 * 2 * math.pi; ph = (t * 1.2 + k * .1) % 1
            for sx in (-1, 1):
                x = cx + sx * 330; r0 = R + 150 - 70 * ph; r1 = r0 - 60
                arrow(d, (x + r0 * math.cos(a_), cy + r0 * math.sin(a_)), (x + r1 * math.cos(a_), cy + r1 * math.sin(a_)), w=6, head=20)
    return im

# ---------------- plan view (top) ----------------
def plan_view(t, stage=1, prog=1.0, train=None, flee=None, gal=0.0):
    im = BG.copy(); d = ImageDraw.Draw(im)
    x0, x1 = 120, 1800; ya, yb_, yg = 430, 650, 540
    d.text((x0, 730), "DRAUFSICHT, SCHEMATISCH", font=font(BOLD, 30), fill=GREY)
    for y in (ya, yb_):
        d.rounded_rectangle((x0, y - 34, x1, y + 34), 34, fill=(176, 176, 180)); d.rounded_rectangle((x0 + 6, y - 26, x1 - 6, y + 26), 28, fill=PAPER)
    if gal > 0:
        xe = x0 + (x1 - x0) * min(1, gal)
        d.line((x0, yg, xe, yg), fill=ORANGE, width=14)
        if gal < 1: d.ellipse((xe - 16, yg - 16, xe + 16, yg + 16), fill=ORANGE)
    if stage >= 2:
        n = 16
        for k in range(n):
            x = x0 + 60 + k * (x1 - x0 - 120) / (n - 1)
            if (x - x0) / (x1 - x0) <= prog:
                d.rectangle((x - 9, ya + 26, x + 9, yb_ - 26), fill=(255, 196, 60))
        if prog > .2:
            xa = x0 + 60; xb = x0 + 60 + (x1 - x0 - 120) / (n - 1)
            dim_h(d, ya - 70, xa, xb, "333 m", size=40)
    if train is not None:
        x = x0 + (x1 - x0) * train
        d.rounded_rectangle((x - 160, ya - 18, x + 160, ya + 18), 14, fill=INK); d.rectangle((x - 150, ya - 4, x + 150, ya + 4), fill=ORANGE)
    if flee is not None and flee > 0:
        x = x0 + 60 + 7 * (x1 - x0 - 120) / 15
        p = eout(flee)
        arrow(d, (x, ya + 10), (x, ya + 10 + (yb_ - ya - 20) * p), col=(40, 160, 70), w=10, head=30)
        d.text((x + 40, (ya + yb_) / 2), "FLUCHTWEG", font=font(BLACKF, 40), fill=(40, 160, 70), anchor="lm")
        if p > .3:
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            od.ellipse((x - 120, ya - 60, x + 120, ya + 60), fill=(255, 80, 20, int(110 + 60 * math.sin(t * 9))))
            ov = ov.filter(ImageFilter.GaussianBlur(20)); im.paste(ov, (0, 0), ov)
    return im

# ---------------- long section Innsbruck -> Franzensfeste ----------------
LS = {"x0": 160, "x1": 1760, "y": 560}
def lsx(km): return LS["x0"] + (LS["x1"] - LS["x0"]) * km / 64.0
def longsection(t, show_stops=0.0, show_access=0.0, attack=0.0, flavia=None, joined=0.0):
    im = BG.copy(); d = ImageDraw.Draw(im); y = LS["y"]
    d.rounded_rectangle((LS["x0"], y - 30, LS["x1"], y + 30), 30, fill=(176, 176, 180)); d.rounded_rectangle((LS["x0"] + 6, y - 22, LS["x1"] - 6, y + 22), 24, fill=PAPER)
    for lab, km, anc in (("INNSBRUCK", 0, "lm"), ("FRANZENSFESTE", 64, "rm")):
        d.text((lsx(km), y + 170), lab, font=font(BOLD, 36), fill=INK, anchor="lm" if km == 0 else "rm")
    bx = lsx(37); d.line((bx, y - 180, bx, y + 180), fill=GREY, width=3)
    d.text((bx, y - 200), "STAATSGRENZE / BRENNER", font=font(BOLD, 30), fill=GREY, anchor="mb")
    if show_stops > 0:
        for i, (lab, km) in enumerate((("INNSBRUCK", 12), ("ST. JODOK", 30), ("TRENS", 51))):
            a = eout((show_stops - i * .25) / .3)
            if a <= 0: continue
            x = lsx(km); d.rounded_rectangle((x - 70, y - 50 * a, x + 70, y + 50 * a), 14, fill=(255, 196, 60))
            d.text((x, y + 70), "NOTHALT", font=font(BOLD, 26), fill=INK, anchor="mm"); d.text((x, y + 104), lab, font=font(SEMI, 26), fill=GREY, anchor="mm")
    acc = (("AMPASS", 6), ("AHRENTAL", 14), ("WOLF", 24), ("MAULS", 49))
    if show_access > 0:
        for i, (lab, km) in enumerate(acc):
            a = eout((show_access - i * .2) / .3)
            if a <= 0: continue
            x = lsx(km); d.line((x, y - 30, x - 60, y - 30 - 200 * a), fill=INK, width=14)
            if a > .9: d.text((x - 60, y - 250), lab, font=font(BOLD, 30), fill=INK, anchor="mb")
    if attack > 0:
        for k, (lab, km) in enumerate(acc + (("", 0), ("", 64))):
            for s in (-1, 1):
                if (km == 0 and s < 0) or (km == 64 and s > 0): continue
                L = 70 + 60 * ((t * 1.3 + k * .2) % 1)
                x = lsx(km); arrow(d, (x, y), (x + s * L * min(1, attack), y), w=10, head=24)
    if flavia is not None:
        xa, xb = lsx(51), lsx(37); x = lerp(xa, xb, flavia)
        d.line((xa, y, x, y), fill=ORANGE, width=26)
        d.rounded_rectangle((x - 30, y - 24, x + 10, y + 24), 8, fill=INK); d.ellipse((x - 44, y - 24, x - 4 - 20, y + 24), fill=ORANGE)
    if joined > 0:
        p = eout(joined); d.line((lsx(0) + 20, y, lsx(0) + 20 + (lsx(64) - lsx(0) - 40) * p, y), fill=ORANGE, width=26)
    return im

# ---------------- bars ----------------
def bars(t, items, title=None, unit="", maxv=None, y0=360, step=190):
    im = BG.copy(); d = ImageDraw.Draw(im)
    if title: d.text((160, 200), title, font=font(BLACKF, 64), fill=INK)
    maxv = maxv or max(v for _, v, _, _ in items)
    for i, (lab, v, col, t0) in enumerate(items):
        if t < t0: continue
        p = eout((t - t0) / .9); y = y0 + i * step
        d.text((160, y), lab, font=font(BOLD, 44), fill=INK, anchor="lm")
        w = 1000 * v / maxv * p
        d.rounded_rectangle((620, y - 45, 620 + max(w, 10), y + 45), 20, fill=col)
        d.text((640 + w + 20, y), f"{v * p:.1f}".replace(".", ",") + unit if isinstance(v, float) and v % 1 else f"{int(round(v * p))}{unit}", font=font(BLACKF, 64), fill=col, anchor="lm")
    return im

# ---------------- geology ----------------
def geology(t, p=1.0):
    im = BG.copy(); d = ImageDraw.Draw(im)
    sh = 60 * eout(p)
    d.polygon([(100, 300), (900 + sh, 300), (860 + sh, 900), (100, 900)], fill=(170, 150, 128))
    d.polygon([(1820, 300), (1020 - sh, 300), (1060 - sh, 900), (1820, 900)], fill=(140, 132, 150))
    d.text((480, 600), "EUROPÄISCHE\nPLATTE", font=font(BLACKF, 56), fill=PAPER, anchor="mm", align="center")
    d.text((1440, 600), "AFRIKANISCHE\n(ADRIATISCHE) PLATTE", font=font(BLACKF, 50), fill=PAPER, anchor="mm", align="center")
    rnd = random.Random(int(t * 6))
    pts = [(960 + rnd.uniform(-90, 90), y) for y in range(300, 901, 30)]
    d.line(pts, fill=INK, width=8)
    for y in range(320, 900, 40):
        x = 960 + rnd.uniform(-70, 70); r = rnd.uniform(8, 22); d.ellipse((x - r, y - r, x + r, y + r), fill=(90, 84, 80))
    arrow(d, (200, 240), (420 + sh, 240), w=12, head=34); arrow(d, (1720, 240), (1500 - sh, 240), w=12, head=34)
    d.text((960, 980), "PERIADRIATISCHE NAHT", font=font(BLACKF, 56), fill=ORANGE, anchor="mm")
    return im

# ---------------- timeline ----------------
def timeline(t, items, y=560, x0=200, x1=1720, prog=1.0):
    im = BG.copy(); d = ImageDraw.Draw(im)
    d.line((x0, y, x0 + (x1 - x0) * eout(prog), y), fill=INK, width=8)
    years = [it[0] for it in items]; lo, hi = min(years), max(years)
    for i, (yr, lab, t0, hl) in enumerate(items):
        if t < t0: continue
        a = eout((t - t0) / .3); x = x0 + (x1 - x0) * (yr - lo) / (hi - lo); col = ORANGE if hl else INK
        d.ellipse((x - 20 * a, y - 20 * a, x + 20 * a, y + 20 * a), fill=col)
        up = i % 2 == 0
        d.text((x, y - 50 if up else y + 50), lab[0], font=font(BLACKF, 64), fill=col, anchor="mb" if up else "mt")
        d.text((x, y - 130 if up else y + 130), lab[1], font=font(SEMI, 34), fill=GREY, anchor="mb" if up else "mt")
    return im

# ---------------- end card ----------------
def endcard(vt, q="WELCHES MEGAPROJEKT ALS NÄCHSTES?", t_sub=5.0, t_bell=6.6):
    im = BG.copy(); d = ImageDraw.Draw(im)
    d.text((W / 2, 170), "MEISTERWERK", font=font(BLACKF, 110), fill=INK, anchor="mm")
    d.text((W / 2, 260), "Wie die Dinge wirklich gebaut werden", font=font(SEMI, 42), fill=GREY, anchor="mm")
    if vt > .2:
        a_ = eout((vt - .2) / .35); dy = 30 * (1 - a_)
        panel(im, (W / 2 - 620, 360 + dy, W / 2 + 620, 560 + dy), a_, 30, alpha=240); d = ImageDraw.Draw(im)
        d.text((W / 2, 420 + dy), q, font=font(BLACKF, 58), fill=INK, anchor="mm")
        cx, cy = W / 2 - 300, 505 + dy
        d.rounded_rectangle((cx - 34, cy - 24, cx + 34, cy + 20), 10, fill=ORANGE); d.polygon([(cx - 14, cy + 18), (cx - 26, cy + 36), (cx + 2, cy + 18)], fill=ORANGE)
        d.text((cx + 60, cy - 2), "Schreib es in die Kommentare", font=font(SEMI, 44), fill=GREY, anchor="lm")
    if vt > t_sub:
        b_ = eout((vt - t_sub) / .3); s_ = .8 + .2 * b_; bw, bh = 470 * s_, 120 * s_; x0 = W / 2 - 300
        d.rounded_rectangle((x0 - bw / 2, 680, x0 + bw / 2, 680 + bh), 60, fill=ORANGE)
        d.text((x0, 680 + bh / 2), "ABONNIEREN", font=font(BLACKF, 54 * s_), fill=(255, 255, 255), anchor="mm")
    if vt > t_bell:
        c_ = eout((vt - t_bell) / .3); x1, y1 = W / 2 + 200, 740
        sw = math.sin((vt - t_bell) * 14) * 18 * max(0, 1 - (vt - t_bell) / 1.6)
        bell = Image.new("RGBA", (220, 220), (0, 0, 0, 0)); bd = ImageDraw.Draw(bell)
        bd.pieslice((40, 30, 180, 170), 180, 360, fill=INK); bd.rectangle((40, 100, 180, 150), fill=INK)
        bd.polygon([(28, 160), (192, 160), (180, 140), (40, 140)], fill=INK); bd.ellipse((92, 160, 128, 192), fill=INK); bd.ellipse((100, 16, 120, 36), fill=INK)
        bell = bell.rotate(sw, resample=Image.BICUBIC, center=(110, 20)).resize((int(150 * c_) + 1, int(150 * c_) + 1))
        im.paste(bell, (int(x1 - bell.width / 2), int(y1 - bell.height / 2)), bell); d = ImageDraw.Draw(im)
        d.text((x1 + 110, y1), "Glocke aktivieren", font=font(BOLD, 44), fill=INK, anchor="lm")
    return im
