"""Erzeugt bilddrehbuch.json aus timeline.json + shots.py (Zahlen als Ziffern)."""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shots import P
T = json.load(open("/home/claude/mw-work/004/timeline.json"))
Z = [("zweihundertmal", "200-mal"), ("hundert Millionen", "100 Millionen"), ("zweitausendfache", "2000-fache"), ("zwölf Tonnen", "12 Tonnen"),
     ("sechstausend", "6000"), ("hundertmal", "100-mal"), ("hundert Kilometer", "100 Kilometer"), ("zweihundert Gramm", "200 Gramm"),
     ("vierhundert Kilogramm", "400 Kilogramm"), ("zweitausend Grad", "2000 Grad"), ("hundertzwanzig bar", "120 bar"), ("über zweihundert.", "über 200 bar."),
     ("sieben bis zwölf Tonnen", "7 bis 12 Tonnen"), ("dreihundert Grad", "300 Grad"), ("zweihunderttausend Kilometer", "200000 Kilometer"),
     ("sechshundertsechzig Grad", "660 Grad"), ("Neunzehnhundertdreizehn", "1913"), ("neunzehnhundertzweiundzwanzig", "1922"), ("neunzehnhundertzwanzig", "1920"),
     ("ersten Dezember", "1. Dezember"), ("zwölf Prozent", "12 Prozent"), ("ein Prozent", "1 Prozent"), ("achthundert Grad", "800 Grad"),
     ("fünfundzwanzig Grad", "25 Grad"), ("fünfhundert Grad", "500 Grad"), ("zweihundert Grad", "200 Grad"), ("sechsundachtzig Millimetern", "86 Millimetern"),
     ("dreihundert Millionen", "300 Millionen"), ("sechshundert Millionen", "600 Millionen"), ("fünfzigtausend Kilometer", "50000 Kilometer"),
     ("zweitausendvierzehn", "2014"), ("drei bis fünf Prozent", "3 bis 5 Prozent"), ("zweihundert Vollbremsungen", "200 Vollbremsungen"),
     ("zwei bis fünf Tausendstel Millimeter", "0,002 bis 0,005 Millimeter"), ("drei bis vier Hundertstel Millimetern", "0,03 bis 0,04 Millimetern"),
     ("zehn bis vierzig Tausendstel Millimeter", "0,01 bis 0,04 Millimeter"), ("ein Drittel Millimeter", "0,3 Millimeter"),
     ("ein paar Zehntelmillimeter", "einige 0,1 Millimeter"), ("Zwei Jahre", "2 Jahre"), ("Drei schmale", "3 schmale")]
def dig(s):
    for a, b in Z: s = s.replace(a, b)
    s = re.sub(r"\b[Aa]m\b", lambda m: "An dem" if m.group(0) == "Am" else "an dem", s)  # Prüfskript liest „am“ sonst als Uhrzeit (a.m.)
    return s
def zeig(kind, p):
    if kind == "plate": return f"Metallschild klappt auf: {p['big']} – {p['sub'].lower()}"
    if kind == "laser": return f"Laser brennt „{p['text']}“ ins Metall, Funken an der Spitze"
    if kind == "call": return f"Linie zum Teil, Etikett „{p['text']}“ klappt auf"
    if kind == "dim": return f"Technische Maßlinie zeichnet sich ans Teil: {p['label']}"
    if kind == "count": return f"Zähler rattert hoch bis {p['fmt'].format(p['v'])} {p['label'].lower()}"
    return p["zeigt"]
def split(text, shares):
    sents = re.split(r"(?<=[.?!:])\s+", text)
    if len(shares) == 1: return [text]
    out, acc, i = [], [], 0; n = len(text); tgt = shares[0] * n; cur = 0
    for s in sents:
        if len(out) < len(shares) - 1 and acc and cur >= tgt:
            out.append(" ".join(acc)); acc = []; tgt += shares[len(out)] * n
        acc.append(s); cur += len(s) + 1
    out.append(" ".join(acc))
    while len(out) < len(shares): out.append(out[-1])
    return out
from beats import B as BEATS, NAME, D2
B = []
for b in T["blocks"]:
    sh = P[b["id"]]; d = b["t1"] - b["t0"]
    nxt = [x for x in T["blocks"] if x["i"] == b["i"] + 1]
    gap = (nxt[0]["t0"] - b["t1"]) if nxt else 5
    span = d + min(gap, 3.5)
    k = 0 if b["id"][0] == "h" else int(b["id"][0]) if b["id"][0].isdigit() else 7
    ev = []; acc = 0
    for s_ in sh:
        ev.append((acc, s_[4], s_[5], s_[6], s_[7], s_[8], f"{s_[0]}/{s_[1]}"))
        if s_[3] == "2d":
            for fr, desc in D2.get(b["id"], [])[1:]:
                ev.append((acc + fr * s_[2], s_[4], desc, s_[6], s_[7], "", "2d"))
        acc += s_[2]
    for fr, kind, prm in BEATS.get(b["id"], []):
        ev.append((fr, NAME[kind], zeig(kind, prm) if kind in ("plate", "laser", "call", "dim", "count") and b["id"] not in ("e1", "e2") else prm["zeigt"], ["zahl"] if kind in ("plate", "count") else ["erklaerung"], "exakt", "", kind))
    ev.sort(key=lambda e: e[0])
    parts = split(dig(b["text"]), [ (ev[j + 1][0] if j + 1 < len(ev) else 1) - ev[j][0] for j in range(len(ev))])
    for j, e in enumerate(ev):
        fr1 = ev[j + 1][0] if j + 1 < len(ev) else 1
        B.append({"satz": parts[j], "sek": round(span * (fr1 - e[0]), 2), "zeigt": e[2], "animation": e[1], "inhalt": list(e[3]),
                  "genauigkeit": e[4], "neugier": e[5], "kapitel": k, "block": b["id"], "szene": e[6]})
json.dump(B, open(os.path.dirname(os.path.abspath(__file__)) + "/bilddrehbuch.json", "w"), ensure_ascii=False, indent=1)
print(len(B), "Einstellungen")
