"""2D-Motion-Graphics fuer Meisterwerk (Remotion, engine/motion/) – Erweiterung aus der ANOM-Stilprobe (Laurin 23.11.2026:
"Genau so sollte ein Video aussehen" – vor allem die vielen 2D-Animationen). Ersetzt nichts aus EFFEKTE.md/ANIMATION.md
(3D-Werkhalle, Typenschild, Laser-Gravur, Bemaßung, Stahlträger ... bleiben), sondern ergänzt sie fuer Stellen, an denen
eine schnelle 2D-Grafik mehr erklärt als eine weitere 3D-Einstellung.

Look (engine/motion/src/theme.tsx): dunkle Studio-Werkhalle, gebürsteter Stahl, Glut-Orange, Inter Black,
Text wird per **Laser graviert** (kein Tippen – gehört Goldsmith), Beschriftung auf **Typenschildern**, Linien als Orange-Laser.

Bausteine (props wie bei Goldsmith, Sprache Deutsch, Zahlen mit deutschem Komma):
  map     Karte: Messpunkte + Laserlinien, optional Schwarm, Länder orange, Zähler. view "world"|"europe"|[lon, lat, scale]
          {"label": "LIEFERKETTE", "title": "EIN KOLBEN", "view": [10, 48, 2600], "pins": [{"lonlat": [9.18, 48.78], "label": "STUTTGART"}]}
  flow    Fertigungsablauf mit Fortschrittsbalken, Teil wandert von Station zu Station, Abzweig (Ausschuss)
          {"label": "FERTIGUNG", "steps": ["Gießen", "Drehen", "Prüfen"], "packet": "gear", "nodes": [{"label": "GIESSEREI", "icon": "factory"}, ...],
           "branch": {"after": 1, "label": "AUSSCHUSS", "icon": "doc", "text": "0,035 MM ZU VIEL"}}
  flip    Typenschild dreht sich um -> Auflösung des Rätsels. {"teaser": "Sieht rund aus …", "front": {"title": "RUND?", "icon": "gear"}, "back": {"title": "OVAL", "sub": "..."}, "at": 2.4}
  counter Große Zahl auf Stahlplatte, dahinter fallen Teile. {"label": "PRODUKTION", "value": 100, "suffix": " MIO.", "caption": "KOLBEN PRO JAHR", "items": "gear"|"none"}
  grid    Teile-Raster füllt sich (Takt, Stückzahl). {"label": "TAKT", "icon": "gear", "value": 1200, "caption": "TEILE PRO STUNDE"}
  bars    Vergleich als Stahl-/Glut-Balken. {"label": "VERGLEICH", "title": "DICHTE (G/CM³)", "unit": "", "bars": [["Stahl", 7.85, false], ["Aluminium", 2.7, true]]}
  stack   Konstruktionszeichnungen (Blaupausen) stapeln sich, Fragezeichen, Frage wird graviert.
  cipher  Text zerfällt in Zeichen (Patent, Betriebsgeheimnis).   phone  Handy mit Nachrichten (selten passend).
  Icons: phone server bank factory person ship money doc store lock eye gavel gear truck crane clock badge car

Im Compositor (main.py des Videos):
    import motion_mw as MO
    K = MO.clip("flow", {...}, len=5.0)       # beim Import registrieren (Länge = Shot-Länge, max ~7 s)
    MO.build(WK)                              # einmal: rendert fehlende Clips nach WK/motion/ (~10 s Rechenzeit je Clip-Sekunde, nicht parallel zu Blender)
    im = MO.frame(K, t - t0)                  # PIL-RGBA 1920x1080 zur lokalen Zeit; danach brand(im) wie gewohnt
    events += MO.sounds(K, t0)                # [(t, name, gain, dur)] – nur Meisterwerk-Sounds (Laser = Schleifgeräusch wie bei laser())
Fakten in props müssen belegt sein (Quelle im Skript), Schema-Darstellungen mit hinweis() kennzeichnen.
Einmalig: `cd engine/motion && npm install`. Faustregel ANOM: alle 2–4 s ein neues Bild; Meisterwerk-Takt 4–6 s bleibt für 3D-Shots.
"""
import os, json, hashlib, subprocess
import numpy as np, cv2
from PIL import Image

W, H, FPS = 1920, 1080, 30
HERE = os.path.dirname(os.path.abspath(__file__))
_JOBS = {}
_WK = {"dir": "."}


def clip(comp, props, len=5.0):
    j = json.dumps({"c": comp, "p": props, "l": float(len)}, sort_keys=True, ensure_ascii=False)
    k = hashlib.sha1(j.encode()).hexdigest()[:12]
    _JOBS[k] = {"comp": comp, "props": props, "len": float(len)}
    return k


def path(k): return os.path.join(_WK["dir"], "motion", f"{k}.mp4")


def build(wk="."):
    _WK["dir"] = wk; os.makedirs(os.path.join(wk, "motion"), exist_ok=True)
    todo = [dict(v, out=os.path.abspath(path(k))) for k, v in _JOBS.items() if not os.path.exists(path(k))]
    if not todo: return
    jf = os.path.abspath(os.path.join(wk, "motion", "jobs.json")); json.dump(todo, open(jf, "w"), ensure_ascii=False, indent=1)
    print(f"motion: {len(todo)} Clips rendern ...")
    subprocess.run(["node", os.path.join(HERE, "motion", "render.mjs"), jf], check=True)


_CAP = {}
def frame(k, lt):
    p = path(k); c = _CAP.get(p)
    if c is None:
        cap = cv2.VideoCapture(p); c = _CAP[p] = [cap, -1, None, int(cap.get(cv2.CAP_PROP_FRAME_COUNT))]
    i = max(0, min(int(lt * FPS), c[3] - 1))
    if i != c[1]:
        if i != c[1] + 1: c[0].set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, fr = c[0].read()
        if ok: c[1], c[2] = i, cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(c[2]).convert("RGBA")


def _laser(t, text): return [(t, "stone_mill_grinding_01", 0.16, min(1.6, len(text) * 0.045 + 0.2))]
def _ticks(t0, d, n=7, g=0.18): return [(t0 + d * (1 - (1 - i / (n - 1)) ** 2.2), "woodtick", g * (1 - 0.5 * i / (n - 1)), None) for i in range(n)]


def sounds(k, t0=0.0):
    """Ton-Ereignisse in Sekunden ab Clip-Start t0. Gleiche Zeitpunkte wie in engine/motion/src/comps.tsx."""
    j = _JOBS[k]; c, q, L = j["comp"], j["props"], j["len"]
    ev = [(0.0, "whoosh", 0.18, None)]
    if q.get("label"): ev += _laser(0.15, q["label"])
    if c == "map":
        for i, pn in enumerate(q.get("pins", [])):
            t = 0.45 + i * 0.55; ev += [(t, "clink", 0.35, None)]
            if pn.get("label"): ev += _laser(t + 0.15, pn["label"])
        if q.get("counter"): ev += _ticks(0.4, 1.2) + [(1.6, "text_click", 0.5, None)]
        if q.get("title"): ev += [(0.15, "text_click", 0.45, None)]
    elif c == "flow":
        n = len(q.get("nodes", []))
        ev += [(0.1 + i * 0.15, "clink", 0.3, None) for i in range(n)] + [(0.6 + 0.75 * i, "whir", 0.18, 0.6) for i in range(max(0, n - 1))]
        b = q.get("branch")
        if b:
            bt = 0.6 + 0.75 * (b["after"] + 0.5); ev += [(bt + 0.7, "thud", 0.7, None), (bt + 0.7, "sub_drop", 0.4, None)]
    elif c == "flip":
        at = q.get("at", 2.4)
        if q.get("teaser"): ev += _laser(0.25, q["teaser"])
        ev += [(at - 0.6, "glitch", 0.35, None), (at - 0.05, "whoosh", 0.45, None), (at + 0.12, "thud", 0.9, None), (at + 0.12, "sub_drop", 0.6, None)]
    elif c == "counter":
        ev += _ticks(0.1, 1.6, 10) + [(0.9, "text_click", 0.55, None)]
    elif c == "grid":
        ev += [(0.15 + r * 0.22, "clink", 0.12, None) for r in range(6)] + [(1.6, "text_click", 0.5, None)]
    elif c == "bars":
        ev += [(0.4 + i * 0.35, "lever", 0.35, None) for i in range(len(q.get("bars", [])))]
        if q.get("title"): ev += [(0.1, "text_click", 0.45, None)]
    elif c == "stack":
        ev += [(0.1 + i * 0.16, "paper", 0.3, None) for i in range(len(q.get("cards", [])))] + [(1.5, "thud", 0.8, None)]
        if q.get("question"): ev += _laser(0.6, q["question"])
    elif c == "cipher":
        ev += [(0.3, "glitch", 0.35, None), (0.9, "text_click", 0.5, None)]
    elif c == "phone":
        ev += [(0.15 + i * 0.4, "pop", 0.3, None) for i in range(len(q.get("messages", [])))]
    return [(t0 + t, n, g, d) for t, n, g, d in ev if t < L]
