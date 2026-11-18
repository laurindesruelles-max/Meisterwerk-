"""Meisterwerk-Ton mit audiokit (Repo sound-mediathek/audiokit, setup.sh lädt es nach /home/claude/audiokit).

Im Compositor (videos/NNN/main.py) – siehe 002 als Vorlage:
    from audio_ak import AK, ak_events, ak_music
    for at, name, g in ak_events(sfx_events(), SFX): ...                 # aufgeräumte Sounds
    music = ak_music(N, voice, TOTAL, S, vo_at, L, CH, SEGSTART, MUSIC, MUS, extra_beats)   # Musik mit Spannungskurve

Regeln dahinter (Laurin 18.11.2026): Sounds nur passend zum Bild, gleich laut, nicht zu dicht; Kamera-Klick höchstens ~6×/Min.;
keine Dauerschleifen von Maschinen-/Schleifgeräuschen; Musik wechselt spätestens alle ~70 s und baut vor Enthüllungen Spannung auf.
"""
import os, sys
D = os.environ.get("AUDIOKIT", "/home/claude/audiokit")
AK = None
if os.path.exists(os.path.join(D, "adapter.py")):
    sys.path.insert(0, D); import adapter as AK
else: print("WARNUNG: audiokit fehlt – sh setup.sh ausführen (alter Ton-Weg wird benutzt)")

ALT = {"industrial_drive": "suspense_pulse", "suspense_pulse": "industrial_drive", "epic_empire": "industrial_drive",
       "emotional_piano": "suspense_pulse", "coldopen_tension": "suspense_pulse"}

def ak_events(ev, sfx_dir):
    return AK.clean_events(ev, "meisterwerk", sfx_dir, order="t,name,gain") if AK else ev

def ak_music(N, voice, total, S, vo_at, L, CH, SEGSTART, MUSIC, MUS, extra_beats=(), stimuli=None, SR=48000):
    """MUSIC: Liste (cue, track, offset) wie bisher – bestimmt den Haupttrack je Kapitel; der Rest kommt aus der Spannungskurve."""
    words = []
    for x in S:   # Wortzeiten gleichmäßig über die Satzdauer verteilt (Meisterwerk hat keine Wort-JSONs)
        ws = x["vo"].split(); n = x["n"]
        for i, w in enumerate(ws): words.append((vo_at[n] + L[n] * i / max(1, len(ws)), w))
    cues = sorted([((SEGSTART[c] if isinstance(c, str) else c), tr) for c, tr, _ in MUSIC])
    chapters = [(0.0, None)] + [(SEGSTART[f"card{n}"], CH[n]) for n in sorted(CH) if f"card{n}" in SEGSTART]
    def track_at(t):
        tr = cues[0][1]
        for ct, name in cues:
            if ct <= t + 0.5: tr = name
        return tr
    pools = []
    for t0, _ in chapters:
        tr = track_at(t0); pools.append([f"{MUS}/{tr}.mp3", f"{MUS}/{ALT.get(tr, 'suspense_pulse')}.mp3"])
    vm = voice.mean(1) if voice.ndim == 2 else voice
    return AK.music_bed("meisterwerk", N, SR, vm, total, chapters, words, pools, extra_beats, stimuli=stimuli)
