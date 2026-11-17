# Meisterwerk – Lernbuch (wird bei JEDEM Video gelesen und ergänzt)

Kanal: Meisterwerk (@meisterwerktv, Channel-ID UCscOIxeOlEDuGjAmtuxLFMw), deutsch.
Nische: „Wie die Dinge wirklich gebaut werden“ – Fertigung, Maschinen, Megaprojekte (Hochhäuser, Flugzeuge, Tunnel …) in 3D.

## Feste Regeln aus Laurins Feedback
- **LÄNGE: JEDES Video MUSS über 8 Minuten lang sein (ganz wichtig, Laurin 15.11.2026).** Ziel 8:30–10:00. Skript ≥ 1.250 Wörter; vor dem Rendern die Summe der Sprachdauern + Pausen prüfen und bei Bedarf Kapitel ergänzen.
- **Keine KI-Videoclips** (Higgsfield-Credits knapp). Alle bewegten Szenen in Blender (Cycles CPU). KI-Bilder (gpt_image_2_6, 0,25 Credits) sparsam für Stimmungsbilder/Geschichte erlaubt.
- **Stimme**: Harrison (voice_id 573e5163-59b3-4926-aab1-951ef2985f81) mit `elevenlabs_v4` (Parameter `dialogue`, `prompt` als Platzhalter). NICHT text2speech_v2 – spricht Deutsch falsch aus. Zahlen/Jahre im Sprechtext ausschreiben („neunzehnhundertdreiundvierzig“), Abkürzungen lautschriftlich („Hundert-C-R-Sechs“, „F A G“). Kosten ≈ 1,15 Credits pro 210 Zeichen.
- **Sounds**: Bei ALLEN Text-Einblendungen der Kamera-Klick (`shutter`; clink/mclick/tick/slap sind bereits auf shutter umgestellt). Daten/Orte als Tastatur-Typing (key0–7). Schläge (boom/stamp) bei Pressen/Stanzen, hiss beim Abschrecken. NIEMALS selbst synthetisierte Metall-/Surr-/Sirenen-Sounds. Seit 16.11.2026: Jede sichtbare Bewegung bekommt ihr echtes CC0-Geräusch (assets/sfx/SOUNDS.md, engine/clip_sounds.py), kein Rausch-/Wind-Teppich.
- **Look im Video**: helles Studio (warmgrau), Orange-Akzente (255,92,12), Inter-Schrift, weiße Pills mit Klick, große Zahlen mit Panel, Kapitelkarten „KAPITEL N“.
- **Thumbnail**: NICHT hell/brav. Stil der Nischen-Hits: dunkler Hintergrund, glühender Stahl/Funken/dramatisches Gegenlicht, EIN Motiv, 2 Zeilen, max. 3–4 Wörter, weiß + gelb mit dicker schwarzer Kontur, Schockzahl oder Frage („20 TONNEN / FÜR 1 KUGEL?!“). Render in Blender (engine/thumbscene.py) + engine/thumb3.py.
- **Titel**: Neugier/Geheimnis/Superlativ wie bei Goldsmith, nicht beschreibend. Laurin wählte „Ohne diese deutsche Erfindung würde die Welt stillstehen“ statt „20 Tonnen für eine Kugel: So entsteht ein Kugellager“. 3–4 Titel mit vidiq_score_title prüfen, Laurin wählen lassen.
- **Ende jedes Videos (Pflicht)**: Kommentar-Frage („Welches Bauteil sollen wir als Nächstes auseinandernehmen? Schreib es in die Kommentare.“) + „Abonniere Meisterwerk und aktiviere die Glocke“. Endkarte mit Kommentar-Feld, Abonnieren-Button, wackelnder Glocke.
- **Beschreibung**: Kapitel mit Zeitstempeln, Kommentar-Frage, Abo-Hinweis und IMMER eine Quellenliste (jede Zahl belegt).
- **Hook**: überraschender Einstieg aus Geschichte/Alltag (Bomber 1943 → „Und das hier.“ → Kugel), dann Titelkarte.

## Produktion (Erfahrungswerte 15.11.2026)
- 001 war nur 7:20 – zu kurz. Ab 002 mindestens 8:30 (Intro 80 s + 5–6 Kapitel, ~1.250–1.400 Wörter).
- Blender: 960×540, 4–6 Samples + Denoiser ≈ 5–7 s/Frame auf 2 Kernen. Clips 72–192 Frames. ~900 Frames ≈ 1,5 h → im Hintergrund mit nohup rendern, Fortschritt pollen, NIE parallel zwei Blender-Prozesse.
- Freigestellte Renders (film_transparent) werden im Compositor auf den Studio-Hintergrund gesetzt; Glühen beim Härten per Farbkorrektur im Compositor (clip „ofen“).
- Compositor (PIL → ffmpeg) ≈ 10 Min. für 6 Min. Video. Audio: Stimme + Musik je Kapitel (Ducking unter Stimme) + SFX, Endmix loudnorm −14 LUFS.
- Kanal ist (noch) nicht verifiziert → eigene Thumbnails werden abgelehnt, bis Laurin den Kanal mit einer zweiten Telefonnummer bestätigt (seine Nummer hat das Limit von 2 Kanälen/Jahr erreicht). Max. 15 Min. Videolänge bis dahin.
- Upload: Higgsfield media_upload (curl PUT) → cloudfront-URL → vidiq_video_upload / vidiq_upload_image (url) → vidiq_social_post_draft_create (YOUTUBE, categoryId 28) → erst nach Laurins „ja“ veröffentlichen. Upload-Links von mcp.vidiq.com sind vom Sandbox-Proxy blockiert, daher immer über Higgsfield-cloudfront.

## Video-Log
| # | Video | Datum | Ergebnis | Erkenntnis |
|---|---|---|---|---|
| 001 | Ohne diese deutsche Erfindung würde die Welt stillstehen (Kugellager) | 15.11.2026 (f3e_nM6sLgk) | (offen) | Pilot. Sounds mehrfach getauscht (Kamera-Klick), Stimme auf elevenlabs_v4 gewechselt, Thumbnail-Stil auf dunkel/dramatisch geändert, Endkarte mit Kommentar + Glocke ergänzt. |
- Musik (Laurin 17.11.2026): KEINE neuen Tracks pro Video erzeugen – nur die feste Bibliothek in assets/music nutzen. Neue Tracks nur auf ausdrücklichen Wunsch (kostet Credits).
- music_tension aus der Bibliothek gelöscht (Laurin 17.11.2026: zu anstrengend) – nicht mehr verwenden.
- BEWEGUNG statt Standbild (Laurin 17.11.2026): In Video 001 waren am Anfang die Flugzeuge nur Standbilder. Ab jetzt muss sich alles,
  was sich in echt bewegt, auch im Video bewegen (Flugzeuge fliegen, Maschinen laufen, Bänder fahren, Teile werden gepresst/gedreht) –
  als echte 3D-Animation in Blender, besonders im Hook/Cold Open. Viele animierte Szenen, kaum Stills.
  Echte Texturen/Modelle/HDRIs von Poly Haven (engine/assets.py, CC0, wie bei Goldsmith) für Rumpf, Metall, Hallenböden, Himmel.
  KI-Bilder höchstens als Ergänzung und dann mit Bewegung (2.5D-Parallaxe/Licht-Effekte aus goldsmith-pipeline engine/depth25d.py + cinemagraph.py).
  Schnell-Modus für mehr Animation: Cycles 4 Samples, 67 % Auflösung (≈4,4 s/Frame, kaum sichtbarer Unterschied).
