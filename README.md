# Meisterwerk-Pipeline

Automatisierte Produktion für den YouTube-Kanal **Meisterwerk** (@meisterwerktv): „Wie die Dinge wirklich gebaut werden“. Deutsch, 3D-Erklärvideos (Blender), ~7 Minuten.

Zuerst immer `LESSONS.md` lesen – dort stehen Laurins feste Regeln.

## Aufbau
- `setup.sh` – installiert Blender (bpy) und lädt die Tastatursounds.
- `assets/sfx`, `assets/music`, `assets/brand` – Sounds, Musik, Banner/Profilbild.
- `engine/thumbscene.py` + `engine/thumb3.py` – dunkle Thumbnail-Szenen (Blender) + Text.
- `engine/banner.py` – Kanalbanner.
- `videos/001-kugellager/` – vollständiges Referenzvideo:
  - `script.json` (Intro) und `main_script.json` (Hauptteil, Kapitel per Nummernblock 1xx–6xx)
  - `bearing.py`, `scenes2.py` – Blender-Szenen (Hilfsfunktionen: `lathe`, `ring_profile`, `ball`, `cyl`, `box`, `cage_half`, `studio`, `camera`, Keyframes, `vis`)
  - `intro.py` – Compositor Intro (Overlays: `typed`, `pill`, `big_number`, `measure`, Endmix)
  - `main.py` – Compositor Hauptteil (Clips, `sparks`, `shake`, `callout`, `waveform`, `chapter_card`, Musik je Kapitel, `sfx_events`)

## Echte Geräusche und Assets (seit 16.11.2026, 0 Credits)
- `engine/clip_sounds.py`: Geräusche in der Blender-Szene an Frames hängen (`CS.sound("hammer", 48)`, `CS.save(OUT)`), im Compositor `ev += CS.events("r2/<clip>", t_start, speed)`. Bibliothek: `assets/sfx/SOUNDS.md`.
- `engine/assets.py` (Poly Haven, CC0): `A.texture("metal_plate")`, `A.model("metal_tool_chest", loc, rot_z, scale)`, `A.hdri("studio_kontrast_01")` für echtes Studio-Licht. Bewährte Slugs: `GOOD["meisterwerk_*"]`. Downloads von dl.polyhaven.org (freigegeben), Cache ~/.cache/polyhaven.
- Bewusst NICHT übernommen (Goldsmith-Handschrift): Tilt-Shift, Staub, Earth Zoom, Polaroid-Zoom.

## Ablauf für ein neues Video
1. Thema wählen (vidIQ-Outliers), recherchieren, jede Zahl mit Quelle.
2. Skript schreiben (Intro mit Hook + 4–6 Kapitel + Endkarte mit Kommentar-Frage und Glocke).
3. Stimme (Harrison, elevenlabs_v4) → `vo/`, `vo2/`; Pausen per `silencedetect` für Einblendungs-Timing.
4. Blender-Szenen aus den Helfern in `scenes2.py` bauen (Bauteile mit Poly-Haven-Metalltexturen, Licht per Studio-HDRI, Geräusche per clip_sounds), je Szene 1 Testframe prüfen, dann alle im Hintergrund rendern (`r2/<szene>/f_####.png`).
5. Compositor (Kopie von intro.py/main.py anpassen) → Stills prüfen → rendern → zusammenfügen + loudnorm.
6. Thumbnail (dunkel, glühend, 2 Zeilen), 3–4 Titel scoren, Beschreibung mit Kapiteln + Quellen.
7. YouTube-Entwurf über vidIQ, veröffentlichen erst nach Laurins „ja“.
