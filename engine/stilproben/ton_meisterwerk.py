"""Ton fuer die Meisterwerk-Stilprobe. Sound-Plan: echte Werkstatt-Geraeusche an jeder sichtbaren Bewegung.
Masslinie fertig (Holz-Tick) | Lager loest sich (Hebel + Whoosh) | Kugeln landen aussen (2x Klirren)
Zusammenfahren (Whoosh) | Einrasten (Musik setzt kurz aus, dumpfer Schlag + Klirren) | Gluehen (Zischen) | Laser (Schleifen/Funken)"""
import sys; sys.path.insert(0, "/home/claude/stilproben")
from mixer import mix
S = "/home/claude/repos/Meisterwerk-/assets/sfx/"; M = "/home/claude/repos/Meisterwerk-/assets/music/"
f = lambda n: S + n + ".wav"
ev = [(1.05, f("woodtick"), 0.4),
      (1.15, f("whoosh"), 0.4), (2.9, f("clink"), 0.3), (3.3, f("clink"), 0.25),
      (6.2, f("whoosh"), 0.35), (8.1, f("thud"), 1.3), (8.1, f("sub_drop"), 0.6), (8.12, f("clink"), 0.35),
      (8.5, f("hiss"), 0.2)]
music = [(M + "coldopen_tension.mp3", 0.3, 0.0, 0.8, 1.5, [(7.85, -18, 0.3), (8.8, 2, 1.0)]),
         (f("lever"), 0.45, 0.95, 0.02, 0.2, [], 0.0, 1.6), (f("grind"), 0.14, 8.65, 0.1, 0.3, [], 0.5, 10.0)]
print(mix("/home/claude/stilproben/stilprobe_meisterwerk.mp4", "/home/claude/stilproben/ton_meisterwerk.mp4", ev, 11.37, music))
