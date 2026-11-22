"""Zeitplan: Sprachblöcke + Pausen + Karten -> timeline.json"""
import json, subprocess, os
WORK = "/home/claude/mw-work/004"
S = json.load(open(os.path.dirname(os.path.abspath(__file__)) + "/script.json"))
def dur(f): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))
LONG = {"h2", "h4", "110", "210", "310", "411", "504", "508", "511", "513", "607", "610"}
CH = {1: "Die Hölle im Zylinder", 2: "Das Rezept", 3: "Der Guss", 4: "Härten und Drehen", 5: "Das Rätsel", 6: "Der letzte Schliff"}
t = 0.4; items = []; cards = []
prev_ch = "h"
for i, s in enumerate(S):
    ch = s["id"][0]
    if ch != prev_ch:
        if prev_ch == "h":
            cards.append({"kind": "title", "t0": t, "t1": t + 3.2}); t += 3.2
        if ch.isdigit():
            cards.append({"kind": "chapter", "num": int(ch), "title": CH[int(ch)], "t0": t, "t1": t + 3.2}); t += 3.2
        prev_ch = ch
    d = dur(f"{WORK}/vo/a{i:02d}.wav")
    items.append({"i": i, "id": s["id"], "t0": round(t, 3), "t1": round(t + d, 3), "text": s["text"]})
    t += d + (0.85 if s["id"] in LONG else 0.38)
end = t + 5.5
json.dump({"blocks": items, "cards": cards, "end": end}, open(WORK + "/timeline.json", "w"), ensure_ascii=False, indent=1)
print("Gesamt", round(end, 1), "s =", f"{int(end//60)}:{end%60:04.1f}")
