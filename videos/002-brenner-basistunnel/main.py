"""Meisterwerk 002 – Brenner-Basistunnel: full-video compositor.
usage: python3 main.py still t1 t2 ...   |  python3 main.py times  |  python3 main.py all
"""
import sys
from lib import *
from diagrams import *
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
from audio_ak import AK, ak_events, ak_music   # Ton-Regeln + Spannungskurve (audiokit)

S = json.load(open(f"{D}/script.json"))
TIM = json.load(open(f"{WORK}/timing.json"))
VO = {x["n"]: f"{WORK}/vo/{x['n']}.mp3" for x in S}
L = {n: TIM[str(n)]["d"] for n in VO}
CH = {x["n"]: x["ch"] for x in S if "ch" in x}
CHN = {n: i + 1 for i, n in enumerate(sorted(CH))}
PAD = {2: .5, 5: .6, 8: .7, 9: .2, 105: .4, 106: .5, 202: .5, 210: .4, 302: .4, 309: .5, 311: .4, 405: .5, 406: .4, 408: 1.2, 410: .5,
       503: .5, 506: .5, 604: .6, 701: .5, 702: .6, 703: 3.2}
segs = []; t = 0.0; vo_at = {}
for x in S:
    n = x["n"]
    if n in CH:
        segs.append((f"card{n}", t, 2.3)); t += 2.3
    lead = .5 if n == 1 else .15; vo_at[n] = t + lead
    d_ = lead + L[n] + PAD.get(n, .3)
    segs.append((n, t, d_)); t += d_
    if n == 9:
        segs.append(("title", t, 3.6)); t += 3.6
TOTAL = t
SEGSTART = {s[0]: s[1] for s in segs}
def seg_at(t):
    for s in reversed(segs):
        if s[1] <= t: return s
    return segs[0]
def ss(n, k):
    a = TIM[str(n)]["s"]; return a[k] if k < len(a) else a[-1] + .8 * (k - len(a) + 1)

BERG = anchors("berg")

def _frame(t):
    sid, s0, T = seg_at(t); lt = t - s0
    if isinstance(sid, str):
        if sid == "title": return title_card(lt, "BRENNER-BASISTUNNEL", "Wie die Dinge wirklich gebaut werden")
        n = int(sid[4:]); return chapter_card(lt, CHN[n], CH[n])
    v = vo_at[sid]; vt = t - v; P = lambda k: v + ss(sid, k); Pv = lambda k: ss(sid, k)
    im = None; nobrand = False
    # ---------------- INTRO ----------------
    if sid == 1:
        im = kenburns(img("pass"), lt, T, 1.0, 1.15, .5, .4, .5, .55)
        typed(im, t, v + .3, ["BRENNERPASS", "1.371 m ü. M."], (110, 110))
        pill(im, t, P(2) + .3, "ÖSTERREICH  |  ITALIEN", (110, 330), size=48)
    elif sid == 2:
        if vt < Pv(1):
            im = kenburns(img("pass"), lt + 7, 16, 1.0, 1.15, .5, .4, .5, .55)
        else:
            im = kenburns(img("stau"), vt - Pv(1), T - Pv(1), 1.05, 1.18, .6, .5, .5, .55); im = punch(im, vt - Pv(1))
        big_number(im, t, v + 1.6, 2.4, lambda x: f"{x:.1f}".replace(".", ",") + " MIO.", (W / 2, H / 2 - 80), size=190, sub="Lkw pro Jahr über den Brenner (2025)", dur_c=1.2)
        if vt > Pv(1): pill(im, t, P(1) + .8, "FAST 3× SO VIELE WIE ÜBER ALLE SCHWEIZER ALPENPÄSSE", (W / 2, 860), size=46, anchor="m", color=ORANGE)
    elif sid == 3:
        u = 0.0; im = clip("berg", u, zoom=1.0 + .25 * ease(vt / T), cx=.5, cy=.6)
        z = 1.0 + .25 * ease(vt / T)
        if vt > Pv(1) - .3 and BERG:
            d = ImageDraw.Draw(im)
            def scr(p):
                return (W / 2 + (p[0] * W - W / 2) * z, H * .6 + (p[1] * H - H * .6) * z)
            a_ = scr(BERG["pass"]); b_ = scr(BERG["tunnel"]); p = eout((vt - Pv(1) + .3) / .9)
            arrow(d, (a_[0], a_[1] + 20), (a_[0], lerp(a_[1] + 20, b_[1] - 10, p)), w=10, head=34)
            if p > .8: d.text((a_[0] + 40, (a_[1] + b_[1]) / 2), "≈ 1.400 m", font=font(BLACKF, 70), fill=ORANGE, anchor="lm")
        pill(im, t, P(1) + 1.2, "MITTEN IM FELS", (110, 150), size=52)
    elif sid == 4:
        BR = 56 / 120
        u = pw(vt, [(0, .05), (5.6, BR - .02), (6.2, BR + .12), (T, .75)])
        im = clip("durchschlag", u, zoom=1.08)
        im = flash(im, t, v + 5.75); im = shake(im, t, v + 5.75, amp=26, d=.6)
        dust(im, t, v + 5.8, (W * .62, H * .48))
        typed(im, t, v + .2, ["28.07.2026", "10:35 UHR"], (110, 110))
        pill(im, t, v + 5.9, "DIE LETZTE FELSWAND FÄLLT", (110, 330), size=52, color=ORANGE)
    elif sid == 5:
        im = clip("durchschlag", .75 + .25 * vt / T, zoom=1.08 + .05 * vt / T)
        pill(im, t, v + 1.0, "ÖSTERREICH ⟷ ITALIEN", (110, 150), size=56)
        pill(im, t, P(1) + .2, "UNTER DEM ALPENHAUPTKAMM", (110, 270), size=48, color=ORANGE)
    elif sid == 6:
        u = pw(vt, [(0, .2), (Pv(2), .75), (Pv(3), 1.0)])
        im = clip("berg", u, zoom=1.0)
        pill(im, t, v + .4, "BRENNER-BASISTUNNEL", (W / 2, 110), size=72, anchor="m", color=ORANGE)
        big_number(im, t, P(1) + .2, 55, lambda x: f"{int(round(x))} KM", (520, 860), size=120, sub="Innsbruck – Franzensfeste", dur_c=.8)
        big_number(im, t, P(2) + .2, 64, lambda x: f"{int(round(x))} KM", (1400, 860), size=120, sub="mit Umfahrung Innsbruck", dur_c=.8)
        if vt > Pv(3):
            im2 = im; pill(im2, t, P(3) + .1, "LÄNGSTE UNTERIRDISCHE BAHNVERBINDUNG DER WELT", (W / 2, 250), size=42, anchor="m")
    elif sid == 7:
        im = plan_view(t, stage=2, prog=pw(vt, [(0, 0), (Pv(1) + 2, 1)]), gal=pw(vt, [(0, 0), (Pv(1) + 2, 1)]))
        pill(im, t, v + .3, "NUR DIE FAHRRÖHRE …", (110, 150), size=50)
        big_number(im, t, P(1) + 2.2, 230, lambda x: f"≈ {int(round(x))} KM", (W / 2, 880), size=130, sub="Tunnel insgesamt – inkl. Stollen & Zufahrten", dur_c=1.0)
    elif sid == 8:
        im = clip("berg", 1.0, zoom=1.05)
        im = Image.blend(im, BG, .35)
        big_number(im, t, v + 1.3, 11.7, lambda x: f"≈ {x:.1f}".replace(".", ",") + " MRD. €", (W / 2, H / 2 - 40), size=170, sub="Kosten laut aktueller Schätzung (Okt. 2026)", dur_c=1.0)
    elif sid == 9:
        im = clip("tbm", vt / T * .9)
        pill(im, t, v + 1.2, "DAS LÄNGSTE TUNNELSYSTEM SEINER ART", (110, 150), size=48)
        pill(im, t, P(1) + .3, "DER BERG WEHRT SICH", (110, 270), size=52, color=ORANGE)
    # ---------------- KAPITEL 1: DAS PROBLEM ----------------
    elif sid == 101:
        im = kenburns(img("dampf"), lt, T + 13, 1.0, 1.25, .3, .5, .55, .5)
        typed(im, t, v + 2.4, ["19. JAHRHUNDERT"], (110, 110))
    elif sid == 102:
        im = kenburns(img("dampf"), lt + 5.6, T + 5.6, 1.0, 1.25, .3, .5, .55, .5)
        typed(im, t, v + .3, ["BAUZEIT 1864 – 1867", "INNSBRUCK → BOZEN"], (110, 110))
        pill(im, t, P(1) + .4, "MEISTERLEISTUNG IHRER ZEIT", (110, 330), size=46)
        pill(im, t, P(2) + .3, "EINFACH ÜBER DEN PASS", (110, 445), size=50, color=ORANGE)
    elif sid == 103:
        im, (xx, Y, old, tun) = profile(t, "old", p_old=eout(vt / 2.5))
        big_number(im, t, P(1) + 2.5, 25, lambda x: f"≈ {int(round(x))} ‰", (1380, 480), size=130, sub="Steigung auf vielen Abschnitten", dur_c=.6)
        if vt > Pv(2):
            d = ImageDraw.Draw(im); x0_, y0_ = 260, 300; p = eout((vt - Pv(2)) / .6)
            panel(im, (x0_ - 40, y0_ - 120, x0_ + 520, y0_ + 110), p); d = ImageDraw.Draw(im)
            d.polygon([(x0_, y0_ + 60), (x0_ + 440 * p, y0_ + 60), (x0_ + 440 * p, y0_ + 60 - 70 * p)], fill=ORANGE)
            d.text((x0_ + 220, y0_ + 75), "100 m", font=font(BOLD, 34), fill=INK, anchor="mt")
            if p > .9: d.text((x0_ + 455, y0_ + 25), "2,5 m", font=font(BOLD, 34), fill=INK, anchor="lm"); d.text((x0_, y0_ - 95), "SO STEIL (ÜBERHÖHT)", font=font(BOLD, 30), fill=GREY)
    elif sid == 104:
        im = kenburns(img("dampf"), lt, T, 1.3, 1.5, .7, .5, .75, .45)
        pills(im, t, [(v + .3, "BRUTAL FÜR JEDEN ZUG", ORANGE), (P(1) + .6, "+ ZUSÄTZLICHE LOKS"), (P(2) + .2, "LANGSAM"), (P(3) + .2, "WENIGER LAST")])
    elif sid == 105:
        im = kenburns(img("stau"), lt, T, 1.0, 1.2, .4, .5, .6, .55)
        typed(im, t, P(2) + 2.2, ["INNTAL · WIPPTAL"], (1180, 120), size=42)
        big_number(im, t, P(1) + 1.0, 75, lambda x: f"≈ {int(round(x))} %", (W / 2, 720), size=160, sub="des Güterverkehrs rollt auf der Straße", dur_c=.9)
        pills(im, t, [(P(2) + .5, "STAU"), (P(2) + 1.0, "LÄRM"), (P(2) + 1.5, "ABGASE")], y0=150)
    elif sid == 106:
        im = clip("berg", pw(vt, [(0, 0), (Pv(2), .1), (T, .7)]), zoom=1.0)
        pills(im, t, [(P(1) + .2, "NICHT ÜBER DEN BERG …"), (P(2) + .1, "… SONDERN UNTEN DURCH", ORANGE), (P(4) + .1, "AN DER BASIS")], y0=110, step=110, size=46)
    # ---------------- KAPITEL 2: DER PLAN ----------------
    elif sid == 201:
        im = clip("berg", .7 + .3 * vt / T, zoom=1.0 + .08 * vt / T)
        pill(im, t, v + .8, "BASIS-TUNNEL", (W / 2, 110), size=70, anchor="m", color=ORANGE)
        pill(im, t, P(1) + 1.6, "FAST FLACH", (W / 2, 250), size=52, anchor="m")
    elif sid == 202:
        im, (xx, Y, old, tun) = profile(t, "both", 1.0, eout(vt / 3.5))
        d = ImageDraw.Draw(im)
        big_number(im, t, v + 2.8, 794, lambda x: f"{int(round(x))} m", (1250, 880), size=90, sub="höchster Punkt im Tunnel", dur_c=.8)
        if vt > Pv(1):
            p = eout((vt - Pv(1)) / .6); xm = xx(.5)
            dim_v(d, xm + 30, Y(1371), lerp(Y(1371), Y(794), p), "≈ 580 m" if p > .9 else "", size=48)
        if vt > Pv(2):
            pills(im, t, [(P(2) + .8, "TUNNEL: MAX. ≈ 7 ‰", ORANGE), (P(2) + 1.4, "BERGSTRECKE: ≈ 25 ‰")], x=110, y0=110, step=105, size=42)
        pill(im, t, P(4) + .3, "FAST 4× FLACHER", (1300, 110), size=54, color=ORANGE)
    elif sid == 203:
        im = clip("zug", vt / T)
        pill(im, t, v + .5, "LÄNGERE & SCHWERERE GÜTERZÜGE", (110, 150), size=46)
        big_number(im, t, P(1) + 2.3, 250, lambda x: f"{int(round(x))} KM/H", (W / 2, 860), size=130, sub="Personenzüge", dur_c=.8)
    elif sid == 204:
        im = plan_view(t, stage=1)
        pill(im, t, P(1) + .2, "EIN GANZES SYSTEM", (W / 2, 150), size=64, anchor="m", color=ORANGE)
        pill(im, t, v + .4, "NICHT NUR EIN LOCH", (W / 2, 820), size=48, anchor="m")
    elif sid == 205:
        im = cross_section(t, stage=1, t_stage=vt)
        pill(im, t, v + .4, "2 RÖHREN", (110, 150), size=56, color=ORANGE)
        pill(im, t, P(1) + .2, "1 PRO RICHTUNG", (110, 270), size=46)
    elif sid == 206:
        if vt < Pv(1) - .2:
            im = plan_view(t, stage=2, prog=eout(vt / 3.0))
        else:
            x_ = vt - Pv(1) + .2
            im = plan_view(t, stage=2, prog=1, train=.47, flee=x_ / 1.2); im = punch(im, x_)
        pill(im, t, v + .4, "ALLE 333 m: QUERSCHLAG", (110, 150), size=50, color=ORANGE)
    elif sid == 207:
        im = cross_section(t, stage=2 if vt > Pv(1) else 1, t_stage=(vt - Pv(1)) if vt > Pv(1) else 9)
        pill(im, t, P(3) + .1, "DER ERKUNDUNGSSTOLLEN", (110, 150), size=52, color=ORANGE)
        pill(im, t, v + .8, "KAUM EIN ANDERER TUNNEL HAT DAS", (W / 2, 1000), size=40, anchor="m")
    elif sid == 208:
        im = plan_view(t, stage=1, gal=pw(vt, [(0, .1), (Pv(2) + 2, .65), (T, .7)]))
        pills(im, t, [(v + .2, "ZUERST GEBAUT", ORANGE), (P(1) + .2, "DER SPÄHER"), (P(2) + 1.0, "GESTEIN ERKUNDEN")], y0=110, size=44, step=100)
        pill(im, t, P(4) + .3, "SPÄTER: ENTWÄSSERUNG & SERVICE", (110, 840), size=44)
    elif sid == 209:
        im = longsection(t, show_stops=pw(vt, [(0, 0), (Pv(1), 1.0)]) if vt > .3 else 0, show_access=pw(vt, [(Pv(2), 0), (Pv(3), 1)]))
        pill(im, t, v + .3, "3 NOTHALTESTELLEN", (110, 110), size=46, color=ORANGE)
        pill(im, t, P(2) + .1, "4 ZUFAHRTSTUNNEL", (110, 220), size=46)
        pill(im, t, P(3) + .2, "MENSCHEN · MATERIAL · MASCHINEN", (W / 2, 900), size=42, anchor="m")
    elif sid == 210:
        if vt < Pv(2):
            im = longsection(t, show_stops=1, show_access=1, attack=eout(vt / 1.0))
        else:
            im = kenburns(img("mineure"), vt - Pv(2), T - Pv(2), 1.0, 1.12); im = punch(im, vt - Pv(2))
        pill(im, t, v + .5, "VIELE BAUSTELLEN GLEICHZEITIG", (110, 110), size=46, color=ORANGE)
    # ---------------- KAPITEL 3: DIE MASCHINEN ----------------
    elif sid == 301:
        im = clip("tbm", vt / T * .5, zoom=1.0)
        big_number(im, t, v + 1.2, 70, lambda x: f"≈ {int(round(x))} %", (W / 2, 850), size=120, sub="per Tunnelbohrmaschine", dur_c=.8)
        typed(im, t, P(2) + .9, ['TBM „FLAVIA“'], (110, 110), size=50)
    elif sid == 302:
        im = clip("tbm", .5 + .5 * vt / T, zoom=.85, cy=.0)
        x0_, y0_ = 110, 50; a = eout((vt - .2) / .4)
        panel(im, (x0_ - 30, y0_ - 30, x0_ + 1700, y0_ + 235), a); d = ImageDraw.Draw(im)
        if a > .5: d.text((x0_, y0_), "FLAVIA", font=font(BLACKF, 64), fill=ORANGE)
        for i, (lab, at) in enumerate((("≈ 200 m lang", .4), ("≈ 2.750 Tonnen", 2.6), ("≈ 80.000 Einzelteile", Pv(1) + .6), ("≈ 170 Transporte", Pv(1) + 3.6))):
            if vt > at:
                b = eout((vt - at) / .25); d.text((x0_ + 30 * (1 - b) + (i % 2) * 820, y0_ + 90 + (i // 2) * 60), lab, font=font(BOLD, 46), fill=INK)
    elif sid == 303:
        im = clip("kopf", .5 * vt / T, zoom=1.0)
        pill(im, t, v + .2, "DER BOHRKOPF", (110, 150), size=56, color=ORANGE)
        big_number(im, t, P(1) + .4, 10.7, lambda x: f"Ø {x:.1f} m".replace(".", ","), (W / 2, 880), size=120, dur_c=.6)
        pill(im, t, P(2) + .8, "ALLEIN 260 TONNEN", (110, 270), size=48)
    elif sid == 304:
        im = clip("kopf", .5 + .5 * vt / T, zoom=1.0)
        callout(im, t, v + .8, (W * .52, H * .40), "ROLLENMEISSEL", side=-1, length=220)
        pill(im, t, P(1) + .2, "GEHÄRTETE STAHLSCHEIBEN", (110, 150), size=46)
        pill(im, t, P(2) + 2.5, "HYDRAULIK PRESST GEGEN DEN FELS", (110, 270), size=46, color=ORANGE)
    elif sid == 305:
        im = clip("bohrkopf", .2 + .8 * vt / T, zoom=1.2, cx=.7, cy=.45)
        sparks(im, t, v, v + T, (W * .58, H * .5), seed=7, n=40)
        pills(im, t, [(v + .3, "KEIN SCHNEIDEN …"), (P(1) + .3, "… SONDERN DRÜCKEN", ORANGE), (P(2) + .2, "STÜCK FÜR STÜCK")], y0=150)
    elif sid == 306:
        im = clip("foerderband", vt / T)
        pill(im, t, P(1) + .4, "FÖRDERBAND", (110, 150), size=56, color=ORANGE)
        pill(im, t, P(2) + .1, "KILOMETERWEIT AUS DEM BERG", (110, 270), size=46)
    elif sid == 307:
        im = clip("tuebbing", pw(vt, [(0, 0), (T, .62)]))
        pills(im, t, [(P(1) + .3, "DER ERECTOR", ORANGE), (P(3) + .2, "TÜBBINGE = BETONFERTIGTEILE"), (P(4) + .3, "GESCHLOSSENER RING")], y0=150, size=46)
    elif sid == 308:
        if vt < Pv(1) + .8:
            im = clip("tuebbing", pw(vt, [(0, .62), (Pv(1) + .8, .95)]))
        else:
            im = clip("tbm", .3 + .2 * (vt - Pv(1)) / T); im = punch(im, vt - Pv(1) - .8)
            if vt > Pv(1) + 1.2:
                d = ImageDraw.Draw(im); ph = (vt * .8) % 1
                for k in range(3): arrow(d, (700 + 120 * k + 60 * ph, 330), (780 + 120 * k + 60 * ph, 330), w=10, head=28)
        pill(im, t, v + .2, "RING FÜR RING", (110, 150), size=56, color=ORANGE)
        pill(im, t, P(1) + 1.2, "ABSTOSSEN · VORSCHIEBEN", (110, 270), size=46)
    elif sid == 309:
        im = longsection(t, show_stops=0, show_access=0, flavia=pw(vt, [(0, 0), (Pv(1), 1.0)]))
        big_number(im, t, v + 2.8, 14.3, lambda x: f"{x:.1f} KM".replace(".", ","), (W / 2, 870), size=120, sub="westliche Hauptröhre, Italien", dur_c=1.2)
        typed(im, t, P(1) + 1.3, ["FRÜHJAHR 2025", "STAATSGRENZE ERREICHT"], (110, 110), size=40)
    elif sid == 310:
        BL = 70 / 120; tb = Pv(3) + .7
        u = pw(vt, [(0, 0), (Pv(1), .1), (tb, BL - .01), (tb + .2, BL + .03), (T, .82)])
        im = clip("sprengen", u, zoom=1.05)
        im = flash(im, t, v + tb, d=.3); im = shake(im, t, v + tb, amp=30, d=.6)
        dust(im, t, v + tb, (W * .72, H * .5), n=50)
        pills(im, t, [(v + .3, "SPRENGVORTRIEB", ORANGE), (P(1) + .4, "DUTZENDE BOHRLÖCHER"), (P(2) + .3, "SPRENGSTOFF"), (P(3) + .2, "ZÜNDUNG IN REIHENFOLGE")], y0=110, step=105, size=42)
    elif sid == 311:
        if vt < Pv(1):
            im = clip("sprengen", .82 + .18 * vt / max(Pv(1), .1), zoom=1.05)
        else:
            im = kenburns(img("mineure"), vt - Pv(1), T - Pv(1), 1.1, 1.25, .3, .5, .45, .5); im = punch(im, vt - Pv(1))
        pills(im, t, [(v + .2, "ABTRANSPORT"), (P(1) + .2, "SPRITZBETON"), (P(2) + .2, "VON VORNE"), (P(3) + .2, "LANGSAMER – ABER FLEXIBLER", ORANGE)], y0=110, step=105, size=44)
    # ---------------- KAPITEL 4: DER BERG WEHRT SICH ----------------
    elif sid == 401:
        z = 1.0 + .25 * ease(vt / T); im = clip("berg", 1.0, zoom=z, cx=.5, cy=.6)
        pill(im, t, v + .2, "ROUTINE?", (110, 150), size=56, strike_at=v + 1.3)
        if vt > Pv(2) and BERG:
            d = ImageDraw.Draw(im)
            scr = lambda p: (W / 2 + (p[0] * W - W / 2) * z, H * .6 + (p[1] * H - H * .6) * z)
            a_ = scr(BERG["pass"]); b_ = scr(BERG["tunnel"]); p = eout((vt - Pv(2)) / .9)
            arrow(d, (a_[0] - 260, a_[1] + 10), (a_[0] - 260, lerp(a_[1] + 10, b_[1] - 10, p)), w=10, head=34)
        big_number(im, t, P(2) + 3.0, 1720, lambda x: f"{int(round(x)):,} m".replace(",", "."), (1380, 200), size=120, sub="Fels über dem Tunnel (max.)", dur_c=1.0)
    elif sid == 402:
        im = cross_section(t, stage=1, t_stage=9, press=1.0 if vt < Pv(1) + 1 else .0)
        if vt > Pv(1):
            big_number(im, t, P(2) + 1.8, 30, lambda x: f"≈ {int(round(x))} °C", (W / 2, 860), size=130, color=(220, 40, 20), sub="Felstemperatur an der Ortsbrust", dur_c=.8)
        pill(im, t, v + .3, "DRUCK VON ALLEN SEITEN", (110, 110), size=46, color=ORANGE)
    elif sid == 403:
        im = geology(t, p=eout(vt / T))
        pill(im, t, P(2) + .2, "STÖRUNGSZONE", (W / 2, 30), size=50, anchor="m", color=ORANGE)
        pill(im, t, P(3) + 2.5, "ZERRIEBEN & ZERBROCHEN", (W / 2, 150), size=40, anchor="m")
    elif sid == 404:
        im = clip("ueberbruch", pw(vt, [(0, 0), (T, .45)]), zoom=1.05)
        typed(im, t, v + .3, ["APRIL 2023"], (110, 110), size=50)
        pill(im, t, v + 3.0, "STÖRUNGSZONE ≈ 3,5 KM VOR DEM BRENNER", (110, 250), size=46)
        pill(im, t, P(1) + .3, "> 1.200 m FELS DARÜBER", (110, 365), size=46, color=ORANGE)
    elif sid == 405:
        im = clip("ueberbruch", .45 + .55 * vt / T, zoom=1.05 + .1 * vt / T, tint=((40, 10, 0), .08))
        pill(im, t, v + .2, "STILLSTAND", (110, 150), size=60, color=(200, 30, 20))
        big_number(im, t, P(1) + .2, 7, lambda x: f"≈ {int(round(x))} MONATE", (W / 2, 860), size=120, dur_c=.6)
        pill(im, t, P(2) + .5, "FELS AUFWENDIG GESICHERT", (110, 270), size=46)
    elif sid == 406:
        im = clip("ueberbruch", .7 + .3 * vt / T, zoom=1.15, cx=.55, cy=.35)
        big_number(im, t, P(2) + 1.0, 10, lambda x: f"{int(round(x))} ÜBERBRÜCHE", (W / 2, 860), size=110, dur_c=.7)
        pill(im, t, P(1) + .4, "ERKUNDUNGSSTOLLEN, ÖSTERREICH", (110, 150), size=44)
        pill(im, t, P(3) + .2, "GESTEIN BRICHT NACH", (110, 260), size=44)
        pill(im, t, P(5) + .3, "„IRIS“: ≈ 5.500 m³", (110, 370), size=52, color=ORANGE)
    elif sid == 407:
        im = kenburns(img("dorf"), lt, T, 1.0, 1.18, .3, .5, .2, .55)
        pills(im, t, [(v + .3, "WASSER", ORANGE), (P(2) + .5, "QUELLEN SCHÜTZEN")], y0=150)
        big_number(im, t, P(3) + 2.8, 1300, lambda x: f"> {int(round(x)):,}".replace(",", "."), (W / 2, 840), size=130, sub="Messstellen", dur_c=.9)
    elif sid == 408:
        im = kenburns(img("mineure"), lt, T, 1.15, 1.2, .5, .5, .5, .5)
        g = im.convert("L").convert("RGB"); im = Image.blend(g, Image.new("RGB", (W, H), (20, 20, 22)), .45)
        if vt > Pv(1) + .3:
            a = ease((vt - Pv(1) - .3) / .8); d = ImageDraw.Draw(im)
            d.text((W / 2, H / 2), "2024: ZWEI TÖDLICHE UNFÄLLE", font=font(BLACKF, 80), fill=tuple(int(240 * a + 20 * (1 - a)) for _ in range(3)), anchor="mm")
        nobrand = True
    elif sid == 409:
        if vt < Pv(3):
            im = clip("foerderband", .3 + .7 * vt / Pv(3))
            big_number(im, t, P(1) + 1.5, 21, lambda x: f"≈ {int(round(x))} MIO. m³", (W / 2, 860), size=120, sub="Fels insgesamt ausgebrochen", dur_c=.9)
        elif vt < Pv(5):
            im = clip("tuebbing", .85 + .15 * (vt - Pv(3)) / 6, zoom=1.0); im = punch(im, vt - Pv(3))
            pills(im, t, [(P(3) + .3, "≈ 1/3 WIEDERVERWERTET", ORANGE), (P(4) + .3, "ZUSCHLAG FÜR DEN BETON")], y0=150)
        else:
            im = clip("tuebbing", 1.0, zoom=1.0 + .1 * (vt - Pv(5)) / 3); im = punch(im, vt - Pv(5))
            pill(im, t, P(5) + .2, "DER BERG BAUT SEINEN TUNNEL", (W / 2, 150), size=52, anchor="m", color=ORANGE)
    elif sid == 410:
        im = kenburns(img("deponie"), lt, T, 1.0, 1.15, .5, .5, .55, .6)
        typed(im, t, P(1) + .6, ["DEPONIE PADASTERTAL"], (110, 110), size=44)
        big_number(im, t, P(1) + 3.0, 7.7, lambda x: f"≈ {x:.1f}".replace(".", ",") + " MIO. m³", (W / 2, 860), size=120, dur_c=.8)
    # ---------------- KAPITEL 5: DER DURCHSCHLAG ----------------
    elif sid == 501:
        BR = 56 / 120; tb = Pv(2) + 1.6
        u = pw(vt, [(0, .1), (tb, BR - .02), (tb + .6, BR + .12), (T, .7)])
        im = clip("durchschlag", u, zoom=1.1)
        im = flash(im, t, v + tb + .1); im = shake(im, t, v + tb + .1, amp=24, d=.5)
        typed(im, t, v + .3, ["18.09.2025"], (110, 110), size=52)
        pill(im, t, P(1) + .4, "≈ 1.400 m UNTER DER GRENZE", (110, 250), size=46)
        pill(im, t, P(2) + .2, "ERKUNDUNGSSTOLLEN", (110, 365), size=50, color=ORANGE)
    elif sid == 502:
        if vt < Pv(1):
            im = clip("durchschlag", .7 + .3 * vt / Pv(1), zoom=1.1)
        else:
            im = longsection(t, joined=(vt - Pv(1)) / 2.0); im = punch(im, vt - Pv(1))
        pill(im, t, v + .4, "DURCHGEHEND OFFEN", (110, 150), size=56, color=ORANGE)
        pill(im, t, P(2) + .3, "HISTORISCHER MOMENT", (110, 270), size=46)
    elif sid == 503:
        if vt < Pv(2):
            im = timeline(t, [(2025.71, ("18.09.2025", "Erkundungsstollen"), v + .3, False), (2026.57, ("28.07.2026", "Haupttunnelröhre"), v + Pv(1) + 1.5, True)], x0=500, x1=1420)
        else:
            im = BG.copy(); x_ = vt - Pv(2); p = eout(x_ / 2.0) * 220 / 230; d = ImageDraw.Draw(im); im = punch(im, x_); d = ImageDraw.Draw(im)
            cx, cy, r = W / 2, H / 2 + 20, 300
            d.arc((cx - r, cy - r, cx + r, cy + r), 0, 360, fill=LIGHT, width=50)
            d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * p, fill=ORANGE, width=50)
            d.text((cx, cy - 20), f"{int(round(p * 230))}", font=font(BLACKF, 170), fill=INK, anchor="mm")
            d.text((cx, cy + r + 70), "von 230 km ausgebrochen", font=font(SEMI, 44), fill=GREY, anchor="mm")
        pill(im, t, v + .3, "DER WICHTIGSTE MOMENT", (110, 110), size=46, color=ORANGE)
    elif sid == 504:
        im = clip("zug", vt / T * .8, zoom=1.0)
        pill(im, t, v + .2, "NOCH LANGE NICHT FERTIG", (110, 110), size=46, color=ORANGE)
        for i, (lab, at) in enumerate((("GLEISE", Pv(1) + .4), ("OBERLEITUNG", Pv(1) + 1.2), ("SIGNALTECHNIK", Pv(2) + .4), ("BELÜFTUNG", Pv(3) + .3), ("SICHERHEIT", Pv(3) + 1.3))):
            pill(im, t, v + at, lab + "  ✓", (1360, 110 + i * 105), size=44)
        pill(im, t, P(4) + .5, "EIN RIESIGER COMPUTER", (W / 2, 900), size=52, anchor="m")
    elif sid == 505:
        im = bars(t, [("2017", 7.8, (150, 150, 156), v + Pv(1) + .3), ("HEUTE", 11.7, ORANGE, v + Pv(2) + .3)], title="KOSTEN IN MRD. €", maxv=12.5, y0=430, step=200)
        pill(im, t, P(3) + .3, "EU: > 1 MRD. € FÖRDERUNG", (160, 870), size=46)
        pill(im, t, P(4) + .2, "REST: ÖSTERREICH + ITALIEN", (1000, 870), size=46)
    elif sid == 506:
        if vt < Pv(1):
            im = BG.copy(); big_number(im, t, v + 2.8, 2034, lambda x: f"{int(round(1990 + (x - 1990) * 1 if x > 1990 else 1990))}", (W / 2, H / 2), size=260, sub="geplante Eröffnung (Stand Okt. 2026)", dur_c=.8, panel_=False)
        else:
            im = bars(t, [("HEUTE", 80, (150, 150, 156), v + Pv(1) + .3), ("MIT BBT", 25, ORANGE, v + Pv(1) + 1.6)], title="INNSBRUCK → FRANZENSFESTE (MIN.)", maxv=90, y0=430, step=200)
            im = punch(im, vt - Pv(1))
    # ---------------- KAPITEL 6: DER HAKEN ----------------
    elif sid == 601:
        im = map_diagram(t, "tunnel", 1.0)
        pill(im, t, P(1) + .2, "DEUTSCHLAND", (1250, 50), size=60, color=(200, 30, 30))
    elif sid == 602:
        im = map_diagram(t, "zulauf" if vt < Pv(2) else "de")
        pill(im, t, P(2) + .3, "SÜDZULAUF: IM BAU", (1250, 760), size=44)
        pill(im, t, P(3) + .6, "NORDZULAUF: IN PLANUNG", (1250, 50), size=44, color=(200, 30, 30))
    elif sid == 603:
        im = timeline(t, [(2034, ("2034", "Tunnel"), v + 1.0, False), (2043, ("2043", "Nordzulauf"), v + 2.6, True)], x0=520, x1=1400)
        big_number(im, t, P(1) + .3, 9, lambda x: f"+ {int(round(x))} JAHRE", (W / 2, 900), size=110, color=(200, 30, 30), dur_c=.6)
    elif sid == 604:
        im = kenburns(img("dampf"), lt, T, 1.1, 1.25, .5, .5, .4, .5)
        pill(im, t, v + 3.6, "STRECKE AUS DEM 19. JAHRHUNDERT", (110, 150), size=48, color=ORANGE)
    # ---------------- SCHLUSS ----------------
    elif sid == 701:
        cuts = [(-9, "berg"), (Pv(1), "sprengen"), (Pv(2), "tuebbing"), (Pv(3), "zug")]
        k = max(i for i, (c, _) in enumerate(cuts) if vt >= c); c0, nm = cuts[k]
        u = {"berg": 1.0, "sprengen": .62, "tuebbing": .9, "zug": .3}[nm] + .1 * (vt - c0) / 5
        im = clip(nm, min(u, 1.0)); im = punch(im, vt - c0)
        pills(im, t, [(v + .2, "230 KM TUNNEL"), (P(1) + .2, "21 MIO. m³ FELS"), (P(2) + .2, "> 25 JAHRE"), (P(3) + .4, "FAST FLACH", ORANGE)], y0=150)
    elif sid == 702:
        im = clip("berg", 1.0, zoom=1.0 + .05 * vt / T)
        pill(im, t, P(3) + .4, "EIN MEISTERWERK", (W / 2, 150), size=64, anchor="m", color=ORANGE)
    elif sid == 703:
        im = endcard(vt, t_sub=Pv(2) + .3, t_bell=Pv(2) + 2.4); nobrand = True
    if im is None: im = BG.copy()
    im = _drift(im, lt, T)
    if not nobrand: brand(im)
    return im

def frame(t):
    """slow push-in on every segment so no shot is ever a freeze frame (QA rule: Bewegung statt Standbild)"""
    sid, s0, T = seg_at(t); lt = t - s0
    return _frame(t)
def _drift(im, lt, T):
    z = 1.0 + .045 * min(max(lt / max(T, .1), 0), 1)
    w, h = int(W * z), int(H * z)
    return im.resize((w, h), Image.BILINEAR).crop(((w - W) // 2, (h - H) // 2, (w - W) // 2 + W, (h - H) // 2 + H))

# ---------------- SFX ----------------
def sfx_events():
    ev = []; a = vo_at; P = lambda n, k: a[n] + ss(n, k)
    for sid, s0, T in segs:
        if isinstance(sid, str) and sid.startswith("card"): ev += [(s0 + .05, "boom", .45), (s0 + .05, "shutter", .3)]
    ev += [(SEGSTART["title"] - 1.4, "riser", .5), (SEGSTART["title"], "braam", .7), (SEGSTART["title"], "boom", .4)]
    clicks = {1: [P(1, 2) + .3], 2: [a[2] + 1.6, P(2, 1) + .8], 3: [P(3, 1) + 1.2], 5: [a[5] + 1.0, P(5, 1) + .2], 6: [a[6] + .4, P(6, 1) + .2, P(6, 2) + .2, P(6, 3) + .1],
              7: [a[7] + .3, P(7, 1) + 2.2], 8: [a[8] + 1.3], 9: [a[9] + 1.2, P(9, 1) + .3], 102: [P(102, 1) + .4, P(102, 2) + .3], 103: [P(103, 1) + 2.5, P(103, 2)],
              104: [a[104] + .3, P(104, 1) + .6, P(104, 2) + .2, P(104, 3) + .2], 105: [P(105, 1) + 1.0, P(105, 2) + .5, P(105, 2) + 1.0, P(105, 2) + 1.5],
              106: [P(106, 1) + .2, P(106, 2) + .1, P(106, 4) + .1], 201: [a[201] + .8, P(201, 1) + 1.6], 202: [a[202] + 2.8, P(202, 1), P(202, 2) + .8, P(202, 2) + 1.4, P(202, 4) + .3],
              203: [a[203] + .5, P(203, 1) + 2.3], 204: [a[204] + .4, P(204, 1) + .2], 205: [a[205] + .4, P(205, 1) + .2], 206: [a[206] + .4], 207: [P(207, 3) + .1, a[207] + .8, P(207, 1) + .7],
              208: [a[208] + .2, P(208, 1) + .2, P(208, 2) + 1.0, P(208, 4) + .3], 209: [a[209] + .3, P(209, 2) + .1, P(209, 3) + .2], 210: [a[210] + .5, P(210, 2)],
              301: [a[301] + 1.2], 302: [a[302] + .4, a[302] + 2.6, P(302, 1) + .6, P(302, 1) + 3.6], 303: [a[303] + .2, P(303, 1) + .4, P(303, 2) + .8],
              304: [a[304] + .8, P(304, 1) + .2, P(304, 2) + 2.5], 305: [a[305] + .3, P(305, 1) + .3, P(305, 2) + .2], 306: [P(306, 1) + .4, P(306, 2) + .1],
              307: [P(307, 1) + .3, P(307, 3) + .2, P(307, 4) + .3], 308: [a[308] + .2, P(308, 1) + 1.2], 309: [a[309] + 2.8],
              310: [a[310] + .3, P(310, 1) + .4, P(310, 2) + .3, P(310, 3) + .2], 311: [a[311] + .2, P(311, 1) + .2, P(311, 2) + .2, P(311, 3) + .2],
              401: [a[401] + .2, P(401, 2) + 3.0], 402: [a[402] + .3, P(402, 2) + 1.8], 403: [P(403, 2) + .2, P(403, 3) + 2.5], 404: [a[404] + 3.0, P(404, 1) + .3],
              405: [a[405] + .2, P(405, 1) + .2, P(405, 2) + .5], 406: [P(406, 1) + .4, P(406, 2) + 1.0, P(406, 3) + .2, P(406, 5) + .3], 407: [a[407] + .3, P(407, 2) + .5, P(407, 3) + 2.8],
              409: [P(409, 1) + 1.5, P(409, 3) + .3, P(409, 4) + .3, P(409, 5) + .2], 410: [P(410, 1) + 3.0], 501: [P(501, 1) + .4, P(501, 2) + .2],
              502: [a[502] + .4, P(502, 2) + .3], 503: [a[503] + .3, a[503] + .3, a[503] + ss(503, 1) + 1.5], 504: [a[504] + .2, P(504, 4) + .5] + [a[504] + x for x in (ss(504, 1) + .4, ss(504, 1) + 1.2, ss(504, 2) + .4, ss(504, 3) + .3, ss(504, 3) + 1.3)],
              505: [P(505, 1) + .3, P(505, 2) + .3, P(505, 3) + .3, P(505, 4) + .2], 506: [a[506] + 2.8, P(506, 1) + .3, P(506, 1) + 1.6], 601: [P(601, 1) + .2],
              602: [P(602, 2) + .3, P(602, 3) + .6], 603: [a[603] + 1.0, a[603] + 2.6, P(603, 1) + .3], 604: [a[604] + 3.6],
              701: [a[701] + .2, P(701, 1) + .2, P(701, 2) + .2, P(701, 3) + .4], 702: [P(702, 3) + .4], 703: [a[703] + .2, P(703, 2) + .3, P(703, 2) + 2.4]}
    for n, ts in clicks.items():
        for x in ts: ev.append((x, "shutter", .42))
    typed_sfx(ev, a[1] + .3, ["BRENNERPASS", "1.371 m ü. M."]); typed_sfx(ev, a[4] + .2, ["28.07.2026", "10:35 UHR"])
    typed_sfx(ev, a[101] + 2.4, ["19. JAHRHUNDERT"]); typed_sfx(ev, a[102] + .3, ["BAUZEIT 1864 – 1867", "INNSBRUCK → BOZEN"])
    typed_sfx(ev, P(105, 2) + 2.2, ["INNTAL · WIPPTAL"]); typed_sfx(ev, P(301, 2) + .9, ['TBM „FLAVIA“']); typed_sfx(ev, P(309, 1) + 1.3, ["FRÜHJAHR 2025", "STAATSGRENZE ERREICHT"])
    typed_sfx(ev, a[404] + .3, ["APRIL 2023"]); typed_sfx(ev, P(410, 1) + .6, ["DEPONIE PADASTERTAL"]); typed_sfx(ev, a[501] + .3, ["18.09.2025"])
    # impacts
    ev += [(a[4] + 5.75, "boom", .8), (a[4] + 5.75, "stamp", .5), (a[4] + 5.8, "sub_drop", .4), (a[2] + 1.6, "whoosh", .25)]
    tb = ss(310, 3) + .7; ev += [(a[310] + tb, "boom", .9), (a[310] + tb, "sub_drop", .5), (a[310] + tb + .05, "thud", .5)]
    tb = ss(501, 2) + 1.7; ev += [(a[501] + tb, "boom", .7), (a[501] + tb, "stamp", .4)]
    ev += [(a[8] + 1.3, "coins", .35), (P(505, 2) + .3, "coins", .3), (a[3] + ss(3, 1), "sub_drop", .35), (a[401] + ss(401, 2), "sub_drop", .35)]
    ev += [(a[405] + .2, "glitch", .3), (P(406, 2) + 1.0, "thud", .5), (a[303] + .2, "whir", .3), (a[9] + .2, "whir", .25), (a[306] + .2, "roll", .3), (a[409] + .2, "roll", .3)]
    for k in range(6): ev.append((a[307] + 0.0 + k * 1.7, "thud", .25))
    ev += [(a[203] + 1.0, "whoosh", .4), (a[702] + 1.0, "whoosh", .3), (P(206, 1), "heartbeat", .35)]
    # echte CC0-Geräusche für jede sichtbare Bewegung (Regel 16.11.2026)
    def loop(name, n, g, t0=None, t1=None):
        s0 = SEGSTART[n]; T = [x for x in segs if x[0] == n][0][2]
        t, e = (t0 if t0 is not None else s0), (t1 if t1 is not None else s0 + T); d = max(.3, dur(f"{SFX}/{name}.wav") * .9)
        while t < e - .2: ev.append((t, name, g)); t += d
    ev += [(a[2] + .2, "car_pass", .45), (P(2, 1) + .1, "car_pass", .35), (a[105] + .5, "car_pass", .3)]
    for n in (9, 301, 302, 308): loop("machine_engine", n, .28)
    for n in (303, 304): loop("grind", n, .35); loop("machine_engine", n, .18)
    loop("grind", 305, .4); ev += [(P(304, 2) + 2.3, "pneumatic_hiss", .45)]
    for n in (306, 409): loop("machine_engine", n, .25)
    for k in range(6): ev.append((a[307] + k * 1.7 - .3, "lever", .3)); ev.append((a[307] + k * 1.7 + .5, "pneumatic_hiss", .2))
    ev += [(P(308, 1) + .9, "pneumatic_hiss", .4)]
    for n in (404, 405, 406): loop("machine_engine", n, .15)
    rnd = random.Random(8)
    for n in (404, 406):
        for k in range(8): ev.append((SEGSTART[n] + rnd.uniform(1, 9), "thud", .18))
    loop("grind", 4, .3, a[4], a[4] + 5.7); loop("grind", 501, .3, a[501], a[501] + ss(501, 2) + 1.6)
    for k in range(6): ev.append((P(310, 1) + .3 + k * .45, "hammer", .25))
    return ev

MUSIC = [(0.0, "coldopen_tension", 0), ("title", "epic_empire", 0), ("card101", "emotional_piano", 0), ("card201", "industrial_drive", 0), ("card301", "industrial_drive", 60),
         ("card401", "suspense_pulse", 0), ("card501", "epic_empire", 20), ("card601", "suspense_pulse", 40), ("card701", "emotional_piano", 30)]
def music_bed(N):
    cues = [(SEGSTART[c] if isinstance(c, str) else c, nm, off) for c, nm, off in MUSIC]
    bed = np.zeros((N, 2), np.float32); XF = int(1.5 * SR); cache = {}
    for i, (t0, name, off) in enumerate(cues):
        t1 = cues[i + 1][0] if i + 1 < len(cues) else N / SR
        a_ = int(t0 * SR); b_ = min(N, int(t1 * SR) + XF)
        if name not in cache: cache[name] = load(f"{MUS}/{name}.mp3")
        tr = cache[name][int(off * SR):]; tr = np.concatenate([tr] * (2 + (b_ - a_) // max(1, len(tr))))[: b_ - a_].copy()
        r = min(XF, len(tr)); tr[:r] *= np.linspace(0, 1, r)[:, None]
        if i + 1 < len(cues): tr[-XF:] *= np.linspace(1, 0, XF)[:, None]
        g = {"emotional_piano": .9, "suspense_pulse": .9, "epic_empire": .75, "music_tension": .85}.get(name, 1.0)
        bed[a_:a_ + len(tr)] += tr * g
    return bed

def mix(path):
    import scipy.io.wavfile as wf
    N = int((TOTAL + .3) * SR); voice = np.zeros((N, 2), np.float32)
    for n, at in vo_at.items():
        a_ = load(VO[n]); i = int(at * SR); voice[i:i + len(a_)] += a_[:N - i]
    voice *= .5 / (np.sqrt(np.mean(voice[np.abs(voice[:, 0]) > 1e-4] ** 2)) * 4 + 1e-9) * .8
    if AK is not None:   # audiokit (18.11.2026): Spannungskurve statt 1 Track je Kapitel, Ducking + Pegel automatisch
        big = [(vo_at[4] + 5.75, "enthuellung", 4), (vo_at[310] + ss(310, 3) + .7, "enthuellung", 3), (vo_at[501] + ss(501, 2) + 1.7, "enthuellung", 3)]
        music = ak_music(N, voice, TOTAL, S, vo_at, L, CH, SEGSTART, MUSIC, MUS, big, stimuli=[s[1] for s in segs])
        end_f = int((TOTAL - 2.0) * SR); music[end_f:] *= np.linspace(1, 0, N - end_f)[:, None]
    else: music = None
    if music is None:
      music = music_bed(N)
      vamp = np.abs(voice[:, 0]); k = int(.15 * SR); vs = np.convolve(vamp, np.ones(k) / k, mode="same")
      duck = 1 - .55 * np.clip(vs / (np.percentile(vs, 99) * .25 + 1e-9), 0, 1)
      env = np.ones(N, np.float32)
      i0 = int((vo_at[408] - .5) * SR); i1 = int((vo_at[408] + L[408] + 1.0) * SR); env[i0:i1] = .35  # quiet moment
      music *= (duck * env)[:, None] * .30
      end_f = int((TOTAL - 2.0) * SR); music[end_f:] *= np.linspace(1, 0, N - end_f)[:, None]
    fx = np.zeros((N, 2), np.float32); cache = {}
    for at, name, g in ak_events(sfx_events(), SFX):
        if name not in cache: cache[name] = load(f"{SFX}/{name}.wav")
        s = cache[name]
        if name.startswith("key"): g *= .75
        i = int(at * SR)
        if 0 <= i < N: fx[i:i + len(s)] += s[:N - i] * g
    out = np.tanh((voice + music + fx * .8) * 1.1) * .95
    wf.write(path, SR, (out * 32767).astype(np.int16))
    if AK is not None:
        wf.write(path + ".v.wav", SR, voice.astype(np.float32)); wf.write(path + ".m.wav", SR, music.astype(np.float32))
        AK.LOG.append("Hinweis: Endlautheit wird erst nach loudnorm beim Zusammenfügen erreicht (Ziel −14 LUFS).")
        AK.final_check(path, path + ".v.wav", path + ".m.wav"); AK.write_report(f"{D}/ton_bericht.txt")

def render_video(path, t0=0.0, t1=None):
    t1 = t1 or TOTAL
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    n0, n1 = int(t0 * FPS), int(t1 * FPS)
    for i in range(n0, n1):
        p.stdin.write(frame(i / FPS).convert("RGB").tobytes())
        if i % 480 == 0: print("frame", i, "/", n1, flush=True)
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    OUTD = f"{WORK}/out"; os.makedirs(OUTD, exist_ok=True)
    if mode == "still":
        for tt in map(float, sys.argv[2:]): frame(tt).convert("RGB").save(f"{OUTD}/still_{tt:06.1f}.jpg", quality=80)
    elif mode == "times":
        print("TOTAL", round(TOTAL, 1))
        for s in segs: print(s[0], round(s[1], 2), round(s[2], 2))
    elif mode == "part":  # render a time range: part idx t0 t1
        render_video(f"{OUTD}/part_{sys.argv[2]}.mp4", float(sys.argv[3]), float(sys.argv[4]))
    elif mode == "audio":
        mix(f"{OUTD}/audio.wav")
    else:
        render_video(f"{OUTD}/video.mp4"); mix(f"{OUTD}/audio.wav")
        print("done")
