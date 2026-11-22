"""Meisterwerk 004 – Ton („Doku-Mix“): Stimme + Musik je Kapitel (ein Track, Ducking, Swells, Pausen vor großen Momenten)
+ Effekte nur an sichtbaren Ereignissen (Sound-Plan unten). Aufruf: python3 mix.py [video_in video_out]"""
import os, sys, json, math, subprocess
import numpy as np
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from beats import B as BEATS
WK = "/home/claude/mw-work/004"; SFX = WK + "/sfx"; ASF = "/home/claude/mw/assets/sfx"; MUS = "/home/claude/mw/assets/music"
SR = 48000
T = json.load(open(WK + "/timeline.json")); SH = json.load(open(WK + "/shots.json"))
DUR = T["end"]; N = int(DUR * SR) + SR

def load(p, sr=SR):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", "2", "-ar", str(sr), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
_c = {}
def snd(name):
    if name not in _c:
        for p in (f"{SFX}/{name}.wav", f"{ASF}/{name}.wav", f"/home/claude/mw-work/sfx/{name}.wav"):
            if os.path.exists(p):
                a = load(p); pk = np.abs(a).max() + 1e-9; _c[name] = a / pk * 0.5; break
        else: raise FileNotFoundError(name)
    return _c[name]
def place(buf, a, t, g=1.0, dur=None, fi=0.01, fo=0.08):
    a = a.copy()
    if dur: a = a[:int(dur * SR)]
    n = len(a)
    if n == 0: return
    k = min(n, int(fi * SR)); a[:k] *= np.linspace(0, 1, k)[:, None]
    k = min(n, int(fo * SR)); a[n - k:] *= np.linspace(1, 0, k)[:, None]
    i = int(t * SR)
    if i < 0: a = a[-i:]; i = 0
    if i >= len(buf): return
    a = a[:len(buf) - i]; buf[i:i + len(a)] += a * g
def wav(p, a):
    import wave
    with wave.open(p, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype("<i2").tobytes())
def lufs(p):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, "-af", "loudnorm=print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(o[o.rindex("{"):o.rindex("}") + 1]); return float(j["input_i"]), float(j["input_tp"])
def ffx(a, af, name):
    wav(f"/tmp/claude-0/{name}_in.wav", a)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", f"/tmp/claude-0/{name}_in.wav", "-af", af, "-ar", str(SR), "-ac", "2", f"/tmp/claude-0/{name}_out.wav"], check=True)
    b = load(f"/tmp/claude-0/{name}_out.wav"); return b[:len(a)] if len(b) >= len(a) else np.pad(b, ((0, len(a) - len(b)), (0, 0)))
os.makedirs("/tmp/claude-0", exist_ok=True)

# ---------- Stimme ----------
voice = np.zeros((N, 2), np.float32)
for b in T["blocks"]:
    a = load(f"{WK}/vo/a{b['i']:02d}.wav"); place(voice, a, b["t0"], 1.0, fi=0.005, fo=0.03)
voice = ffx(voice, "highpass=f=70,deesser=i=0.25:m=0.5:f=0.5,equalizer=f=2600:t=q:w=1.2:g=1.5,equalizer=f=75:t=q:w=1:g=1.5,acompressor=threshold=-18dB:ratio=1.8:attack=10:release=150:makeup=1", "voice")
# Sprach-Aktivität (für Ducking)
env = np.abs(voice).mean(1); win = int(0.05 * SR)
env = np.convolve(env, np.ones(win) / win, "same")
act = (env > 0.01).astype(np.float32)
# Hüllkurve: schnell runter (Attack 60 ms), langsam hoch (Release 400 ms)
sm = np.zeros_like(act); a_up, a_dn = 1 - math.exp(-1 / (0.06 * SR)), 1 - math.exp(-1 / (0.4 * SR)); v = 0.0
for i in range(0, len(act), 240):
    x = act[i:i + 240].max(); v += (x - v) * (1 - (1 - (a_up if x > v else a_dn)) ** 240); sm[i:i + 240] = v

# ---------- Musik: ein Track je Kapitel ----------
cards = {c.get("num", 0) if c["kind"] == "chapter" else "title": c for c in T["cards"]}
segs = [("coldopen_tension", 0.0, cards["title"]["t1"], 0.0)]
plan = {1: ("praezision_ticken", 0), 2: ("werkhalle_puls", 0), 3: ("aufbau_zeitraffer", 0), 4: ("praezision_ticken", 48), 5: ("coldopen_tension", 0), 6: ("werkhalle_puls", 40)}
for n in range(1, 7):
    t0 = cards[n]["t0"]; t1 = cards[n + 1]["t0"] if n < 6 else DUR
    segs.append((plan[n][0], t0, t1, plan[n][1]))
music = np.zeros((N, 2), np.float32)
EQ = {"praezision_ticken": "highshelf=f=4500:g=-4", "aufbau_zeitraffer": "equalizer=f=1800:t=q:w=1:g=-3.5", "werkhalle_puls": "equalizer=f=2500:t=q:w=1:g=-2", "coldopen_tension": "equalizer=f=2500:t=q:w=1:g=-2"}
for name, t0, t1, off in segs:
    tr = load(f"{MUS}/{name}.mp3"); L = int((t1 - t0 + 2.5) * SR)
    seg = tr[int(off * SR):]
    while len(seg) < L:   # zu kurz (coldopen 45 s): sauber mit Überblendung verlängern
        x = tr[int(5 * SR):]; ov = int(2 * SR)
        seg = np.concatenate([seg[:-ov], seg[-ov:] * np.linspace(1, 0, ov)[:, None] + x[:ov] * np.linspace(0, 1, ov)[:, None], x[ov:]])
    seg = ffx(seg[:L], EQ[name], "eq")
    place(music, seg, t0, 1.0, fi=0.4, fo=2.0)

# Gain-Hüllkurve der Musik (dB): Grundpegel, Ducking unter Stimme, Swells, Pausen
tt = np.arange(N) / SR
gdb = np.full(N, -6.0, np.float32)            # in Sprechpausen
gdb -= 9.0 * sm                                # Ducking ~9 dB unter der Stimme
BL = {b["id"]: b for b in T["blocks"]}
def swell(tend, db=5.0, d=2.5):
    m = (tt > tend - d) & (tt < tend + 0.8); x = np.clip((tt[m] - (tend - d)) / d, 0, 1); x[tt[m] > tend] = np.clip(1 - (tt[m][tt[m] > tend] - tend) / 0.8, 0, 1)
    gdb[m] += db * x
def rest(t, d=0.9):
    m = (tt > t - d) & (tt < t + 0.15); gdb[m] = -40
    m2 = (tt >= t + 0.15) & (tt < t + 1.2); gdb[m2] += np.linspace(4, 0, m2.sum())
for bid in ("h2", "104", "307", "408", "508", "607"):
    swell(BL[bid]["t1"], 7.0)
for c in T["cards"]:                           # vor Kapitelkarten absenken, Karte selbst trägt den Kapitel-Sound
    m = (tt > c["t0"] - 1.6) & (tt < c["t0"]); gdb[m] = np.minimum(gdb[m], -6 - 14 * np.clip((tt[m] - (c["t0"] - 1.6)) / 1.6, 0, 1))
    m = (tt >= c["t0"]) & (tt < c["t1"]); gdb[m] = -6.0
RESTS = [("505", 0.0), ("511", 0.0)]
hits = []
for bid, off in RESTS: rest(BL[bid]["t0"] + off); hits.append(BL[bid]["t0"] + off)
# Einrasten im Zusammenbau (605): Musik setzt aus, dann Treffer
s605 = next(s for s in SH if s["block"] == "605"); tsnap = s605["t0"] + 0.65 * (s605["t1"] - s605["t0"])
rest(tsnap, 0.7)
gl = 10 ** (np.convolve(gdb, np.ones(int(.08 * SR)) / int(.08 * SR), "same") / 20)
music *= gl[:, None]

# ---------- Effekte (Sound-Plan) ----------
fx = np.zeros((N, 2), np.float32); atmo = np.zeros((N, 2), np.float32); hit = np.zeros((N, 2), np.float32)
HITS = ("Schlag-Ruck", "Enthüllung", "Einrasten", "Kapitelkarte", "Motor blockiert", "Block schlägt ein", "Zündung")
last = {}
LOG = []
def ev(t, name, g, dur=None, gap=6.0, fi=0.01, fo=0.08, bus=None, why=""):
    if t - last.get(name, -99) < gap: return
    last[name] = t; place(bus if bus is not None else (hit if why in HITS else fx), snd(name), t, g, dur, fi, fo); LOG.append((round(t, 2), name, why))
starts = sorted([b["t0"] for b in T["blocks"]] + [c["t0"] for c in T["cards"]] + [T["end"]])
for b in T["blocks"]:
    t1 = min(x for x in starts if x > b["t0"] + 1e-6); sp = t1 - b["t0"]
    for fr, kind, prm in BEATS.get(b["id"], []):
        ta = b["t0"] + fr * sp
        if kind == "plate": ev(ta + .05, "text_click", .55, gap=11, why="Typenschild")
        elif kind == "call": pass  # Callouts ohne Ton (Effektdichte ~6/min)
        elif kind == "dim": ev(ta + .48, "woodtick", .5, gap=30, why="Bemaßung fertig")
        elif kind == "laser": ev(ta, "stone_mill_grinding_01", .16, dur=min(1.6, len(prm["text"]) * .055 + .2), gap=12, fi=.05, fo=.2, why="Laser-Gravur")
        elif kind == "count":
            for k in range(12):
                x = 1 - (1 - (k + 1) / 12) ** 0.5; place(fx, snd("tick"), ta + x * 1.4, .2 * (1 - k / 16))
            LOG.append((round(ta, 2), "tick-Folge", "Taktuhr"))
        elif kind == "ruck": ev(ta, "thud", 1.0, gap=3, why="Schlag-Ruck"); ev(ta, "sub_drop", .45, gap=3, why="Schlag-Ruck")
        elif kind == "funken": ev(ta, "sparkler_01", .3, dur=1.4, gap=6, fo=.4, why="Funken")
        elif kind == "dampf": ev(ta, "fs_quench", .7, dur=4.0, gap=6, fo=1.0, why="Dampf")
for c in T["cards"]:
    ev(c["t0"], "industrial_electromagnetic_launcher_01", .55, dur=2.6, gap=1, fo=.6, why="Kapitelkarte")
for t in hits: ev(t, "reveal_impact_01", .8, gap=1, why="Enthüllung"); ev(t, "sub_drop", .4, gap=1, why="Enthüllung")
ev(tsnap, "thud", 1.0, gap=1, why="Einrasten"); ev(tsnap, "clink", .45, gap=1, why="Einrasten"); ev(tsnap, "sub_drop", .4, gap=1, why="Einrasten")
# Szenen-Geräusche (an sichtbare Bewegung gebunden)
for s in SH:
    a, e = s["t0"], s["t1"]; d = e - a; sc, v = s["scene"], s["var"]
    at = lambda u: a + u * d
    if sc == "motor":
        if v in ("wide", "tacho", "laeuft", "laeuft2", "finale", "fast"): place(atmo, snd("mechanical_engine_39"), a, .5, d, .4, .6)
        if v in ("zuend", "zuend2"): ev(at(.1), "fs_ignition", .9, dur=1.6, gap=2, fo=.4, why="Zündung")
    elif sc == "band": place(atmo, snd("factory_machinery_ambience_01"), a, .55, d, .5, .6)
    elif sc == "gewicht": ev(at(.5), "thud", 1.0, gap=2, why="Block schlägt ein"); ev(at(.5), "step_metal", .6, gap=2, why="Haken")
    elif sc in ("glut", "ofen") and v != "abschrecken": place(atmo, snd("fs_furnace"), a, .45, d, .5, .6)
    elif sc == "alt": ev(at(.15), "lever", .35, dur=1.2, gap=4, why="Waage kippt")
    elif sc in ("schmelze", "alfin"): place(atmo, snd("fs_furnace"), a, .35, d, .5, .6); ev(at(.35), "fs_pour", .5, dur=2.5, gap=4, fo=.6, why="Material taucht in Schmelze")
    elif sc == "dehnung": place(atmo, snd("air_hiss_01"), a, .18, d, .5, .6)
    elif sc == "kokille":
        if v == "zu": ev(at(.5), "step_metal", .6, gap=1, why="Formhälfte"); ev(at(.62), "clink", .35, gap=1, why="Formhälfte")
        else: ev(at(.1), "pneumatic_hiss", .35, dur=1.2, gap=3, why="Greifer"); ev(at(.55), "clink", .4, gap=1, why="Ring eingesetzt")
    elif sc == "guss": place(atmo, snd("fs_pour"), at(.18), .7, d * .7, .2, .6); LOG.append((round(at(.18), 2), "fs_pour", "Gießen"))
    elif sc == "entformen": ev(at(.05), "pneumatic_hiss", .45, dur=1.5, gap=2, why="Form öffnet"); ev(at(.5), "step_metal", .5, gap=2, why="Rohlinge")
    elif sc == "spuelen": place(atmo, snd("fs_wj1"), a, .6, d, .2, .5)
    elif sc == "kanal" and v == "oel": place(atmo, snd("water_stream_39"), a, .22, d, .5, .6)
    elif sc == "drehbank":
        if v == "bohren": place(atmo, snd("fs_lathe"), a, .4, d, .3, .5)
        elif v == "roh": place(atmo, snd("factory_machinery_ambience_01"), a, .4, d, .4, .5)
        else: place(atmo, snd("fs_lathe"), a, .55 if v != "teaser" else .3, d, .3, .5)
    elif sc == "ofen" and v == "abschrecken": ev(at(.12), "fs_quench", .8, dur=4.5, gap=1, fo=1.0, why="Abschrecken"); ev(at(.12), "hiss", .4, gap=1, why="Abschrecken")
    elif sc == "fresser":
        place(atmo, snd("mechanical_engine_39"), a, .5, d * .78, .3, .1); ev(at(.5), "steel_spike_scrape_01", .45, dur=2.2, gap=1, fo=.3, why="Fressen")
        ev(at(.78), "thud", 1.0, gap=1, why="Motor blockiert"); ev(at(.78), "sub_drop", .5, gap=1, why="Motor blockiert")
    elif sc == "explode" and v == "auf": ev(at(.15), "lever", .4, dur=1.2, gap=1, why="Explosionsansicht"); ev(at(.18), "whoosh", .3, gap=1, why="Explosionsansicht"); ev(at(.16), "thud", .7, gap=1, why="Explosionsansicht")
    elif sc == "explode" and v == "zu": ev(at(.15), "whoosh", .3, gap=1, why="Zusammenbau")
    elif sc == "siebdruck" and v == "a": ev(at(.12), "highlighter", .35, dur=d * .6, gap=1, why="Rakel")
    elif sc == "messen":
        for k in range(5): place(fx, snd("woodtick"), at((k + .5) / 5), .35)
        LOG.append((round(a, 2), "woodtick×5", "Messtaster"))
    elif sc == "endkarte" and v == "a": ev(at(0) + 3.0, "text_click", .45, gap=1, why="Abo-Knopf")
# Effekt-Bus: Höhen über 4,5 kHz -6 dB; Atmo weich, tiefpassgefiltert
fx = ffx(fx, "highshelf=f=4500:g=-6", "fx")
atmo = ffx(atmo, "lowpass=f=3500,highpass=f=60", "atmo")

# ---------- Pegel relativ zur Stimme ----------
def stem_lufs(a, name):
    wav(f"/tmp/claude-0/{name}.wav", a); return lufs(f"/tmp/claude-0/{name}.wav")[0]
Lv = stem_lufs(voice, "v")
def to(a, name, rel):
    L = stem_lufs(a, name); return a * 10 ** ((Lv + rel - L) / 20)
music = to(music, "m", -10.0)     # Musik ~11 dB unter der Stimme (Mittel; Ducking/Swells um diesen Wert)
cg = np.zeros(N, np.float32)       # Kapitelkarten: Musik-Akzent ohne Stimme (lauteste Momente, wie bei fern)
for c in T["cards"]:
    m = (tt >= c["t0"]) & (tt < c["t1"]); x = tt[m] - c["t0"]; cg[m] = 13.0 * np.clip(x / .3, 0, 1) * np.clip((c["t1"] - tt[m]) / .7, 0, 1)
music *= (10 ** (cg / 20))[:, None]
fx = to(fx, "fx", -16.0)          # Effekt-Bus 16 LU unter der Stimme
hit = to(hit, "hit", -6.0)        # Treffer (Enthüllung, Kapitel, Ruck) als dynamische Spitzen
atmo = to(atmo, "at", -28.0)      # Atmo 26–32 dB unter der Stimme
mix = voice + music + fx + atmo + hit
mix = mix[:int(DUR * SR)]
wav(WK + "/mix_raw.wav", mix)
for nm, a in (("stem_voice", voice), ("stem_music", music), ("stem_fx", fx + atmo + hit)): wav(f"{WK}/{nm}.wav", a[:int(DUR * SR)])
# Master: leichter Bass/Präsenz, Lautheit per Messung + Gain, Limiter (True Peak ~ -2 dB)
I, tp = lufs(WK + "/mix_raw.wav"); g = -14.0 - I
for _ in range(3):
    af = f"highpass=f=28,equalizer=f=50:t=q:w=1:g=2.5,highshelf=f=5000:g=-1.5,volume={g:.2f}dB,alimiter=limit=0.7:level=false:attack=1:release=80"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", WK + "/mix_raw.wav", "-af", af, "-ar", "48000", WK + "/mix_master.wav"], check=True)
    got, tpm = lufs(WK + "/mix_master.wav")
    if abs(got + 14) < 0.4: break
    g += -14 - got
json.dump(LOG, open(WK + "/sound_plan_log.json", "w"), ensure_ascii=False, indent=0)
print("Master LUFS", got, "TP", tpm, "Effekte", len(LOG), "≈", round(len(LOG) / (DUR / 60), 1), "/min")
if len(sys.argv) > 2:
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", sys.argv[1], "-i", WK + "/mix_master.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", sys.argv[2]], check=True)
    print("muxed", sys.argv[2])
