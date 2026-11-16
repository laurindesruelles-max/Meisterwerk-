"""Geräusche an Blender-Clips hängen – damit jede Bewegung genau ihr echtes Geräusch bekommt.

1) In der Blender-Szene (beim Animieren):
       import clip_sounds as CS
       CS.sound("hammer", 48)                 # bei Frame 48 schlägt die Presse zu
       CS.sound("machine_engine", 1, 120, loop=True, gain=0.4)   # Maschine läuft von Frame 1 bis 120
       ... nach dem Rendern:  CS.save(OUT)    # schreibt OUT/cues.json neben die Frames
2) Im Compositor (sfx_events):
       ev += CS.events("r2/stauchen", t_start=a[203], speed=.45, f_start=1)
   t_start = Zeitpunkt, an dem der Clip mit Frame f_start im Video beginnt; speed = Abspieltempo wie bei
   clip(name, 1 + vt*24*speed). Loops werden in kurze Wiederholungen der Datei zerlegt.
Namen = Dateien in assets/sfx (Liste: assets/sfx/SOUNDS.md). Nur echte Aufnahmen (CC0), nie selbst synthetisiert.
"""
import os, json, subprocess

_CUES = []
FPS = 24


def sound(name, f0, f1=None, gain=1.0, loop=False):
    _CUES.append({"name": name, "f0": f0, "f1": f1 if f1 is not None else f0, "gain": gain, "loop": loop})


def save(out):
    os.makedirs(out, exist_ok=True); json.dump({"fps": FPS, "cues": _CUES}, open(f"{out}/cues.json", "w"), indent=1)


def _dur(name, sfx="sfx"):
    p = f"{sfx}/{name}.wav"
    try: return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))
    except Exception: return 2.0


def events(clip_dir, t_start, speed=1.0, f_start=1, sfx="sfx"):
    p = f"{clip_dir}/cues.json"
    if not os.path.exists(p): return []
    m = json.load(open(p)); fps = m.get("fps", FPS); ev = []
    to_t = lambda f: t_start + (f - f_start)/(fps*speed)
    for c in m["cues"]:
        if c["f1"] < f_start: continue
        if not c["loop"]: ev.append((to_t(c["f0"]), c["name"], c["gain"])); continue
        d = max(0.3, _dur(c["name"], sfx)*0.9); t, t1 = to_t(max(c["f0"], f_start)), to_t(c["f1"])
        while t < t1 - 0.2: ev.append((t, c["name"], c["gain"])); t += d
    return ev
