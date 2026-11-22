"""Shot-Liste mit exakten Zeiten -> shots.json und render_queue.txt (Reihenfolge = Video-Reihenfolge)"""
import json, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shots import P
W = "/home/claude/mw-work/004"
T = json.load(open(W + "/timeline.json"))
blocks = T["blocks"]; cards = T["cards"]
starts = sorted([b["t0"] for b in blocks] + [c["t0"] for c in cards] + [T["end"]])
out = []
for b in blocks:
    t1 = min(x for x in starts if x > b["t0"] + 1e-6)
    span = t1 - b["t0"]; t = b["t0"]
    for k, s in enumerate(P[b["id"]]):
        d = span * s[2]
        out.append({"block": b["id"], "k": k, "scene": s[0], "var": s[1], "art": s[3], "t0": round(t, 3), "t1": round(t + d, 3),
                    "dir": f"{len(out):03d}_{s[0]}_{s[1]}", "frames": int(math.ceil(d * 12)) + 2})
        t += d
json.dump(out, open(W + "/shots.json", "w"), indent=1)
q = []
for s in out:
    if s["art"] == "3d": q.append(f"{s['scene']} {s['var']} {W}/r/{s['dir']} {s['frames']}")
    elif s["art"] == "st": q.append(f"{s['scene']} {s['var']} {W}/r/{s['dir']} 1 still")
for bg in ("dunkel", "hell"): q.insert(0, f"bg {bg} {W}/r/bg_{bg} 1 still")
open(W + "/render_queue.txt", "w").write("\n".join(q) + "\n")
print(len(out), "Shots,", len(q), "Render-Jobs,", sum(s["frames"] for s in out if s["art"] == "3d"), "Frames 3D")
