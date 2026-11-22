# Meisterwerk – Lernbuch (wird bei JEDEM Video gelesen und ergänzt)

> **Seit 20.11.2026 zuerst lesen:** `HANDWERK.md` (Regeln für alle Kanäle) und `EFFEKTE.md` (Handschrift und erlaubte Effekte dieses Kanals, von Laurin abgenommen). Bei Widerspruch gelten diese beiden Dateien.


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
- **Hook**: überraschender Einstieg aus Geschichte/Alltag (Bomber 1943 → „Und das hier.“ → Kugel), dann Titelkarte. Ab 19.11.2026 zusätzlich die „Hook-Regeln“ unten.

## Produktion (Erfahrungswerte 15.11.2026)
- 001 war nur 7:20 – zu kurz. Ab 002 mindestens 8:30 (Intro 80 s + 5–6 Kapitel, ~1.250–1.400 Wörter).
- Blender: 960×540, 4–6 Samples + Denoiser ≈ 5–7 s/Frame auf 2 Kernen. Clips 72–192 Frames. ~900 Frames ≈ 1,5 h → im Hintergrund mit nohup rendern, Fortschritt pollen, NIE parallel zwei Blender-Prozesse.
- Freigestellte Renders (film_transparent) werden im Compositor auf den Studio-Hintergrund gesetzt; Glühen beim Härten per Farbkorrektur im Compositor (clip „ofen“).
- Compositor (PIL → ffmpeg) ≈ 10 Min. für 6 Min. Video. Audio: Stimme + Musik je Kapitel (Ducking unter Stimme) + SFX, Endmix loudnorm −14 LUFS.
- Kanal ist (noch) nicht verifiziert → eigene Thumbnails werden abgelehnt, bis Laurin den Kanal mit einer zweiten Telefonnummer bestätigt (seine Nummer hat das Limit von 2 Kanälen/Jahr erreicht). Max. 15 Min. Videolänge bis dahin.
- Upload: Higgsfield media_upload (curl PUT) → cloudfront-URL → vidiq_video_upload / vidiq_upload_image (url) → vidiq_social_post_draft_create (YOUTUBE, categoryId 28) → erst nach Laurins „ja“ veröffentlichen. Upload-Links von mcp.vidiq.com sind vom Sandbox-Proxy blockiert, daher immer über Higgsfield-cloudfront.

## Produktion (Erfahrungswerte 17.11.2026, Video 002)
- Skript mit ~1.370 Wörtern (Zahlen ausgeschrieben) ergab 10:09 Sprechzeit, mit Kapitelkarten und Pausen 11:02. Für 8:30–10:00 reichen ~1.150–1.250 Wörter.
- Sprachdateien pro Satzblock (59 Stück) in 6er-Batches: jeder Batch dauert ~25 s. Satzanfänge per silencedetect → `timing.json`; Einblendungen hängen an „Satz k“ statt an festen Sekunden.
- Blender 5.x: `frame_step = 2` halbiert die Renderzeit, der Compositor blendet die Zwischenframes. ~4–6 s/Frame auf 2 Kernen, ~780 Frames ≈ 75 Min.
- Cutaway-Röhren (arc_seg um die X-Achse): offener Bogen muss zur Kamera zeigen (Kamera bei −y → Winkel −160°…100°). Zu helle Materialien wirken im AgX-Look weiß: Fels/Beton dunkler (0,1–0,4 linear), studio(k≈0,8).
- Ein Bohrkopf in einer Felswand ist von der Seite unsichtbar – für Erklärszenen eine eigene Frontansicht rendern (Szene „kopf“).
- Viele Inhalte (Profil, Querschnitt, Draufsicht, Karte, Zeitstrahl, Balken) als 2D-Diagramme in PIL (`diagrams.py`) – schneller und klarer als 3D.
- Container kann mitten im Lauf neu starten: Hintergrundjobs mit `setsid nohup`, Video in Teilen rendern (`main.py part X t0 t1`), danach per concat zusammensetzen.
- Thumbnails: Kamera-Keyframes aus übernommenen Szenen vorher mit `cam.animation_data_clear()` löschen.
- Vor dem Upload IMMER `git pull` (Laurin ändert Regeln auch während eines Laufs) und `engine/qa.py` laufen lassen. Diagramm-Standbilder fallen in der QA durch → leichter Push-in (+4,5 % pro Segment) auf jedem Bild.
- Separater Faktencheck-Agent fand 3 echte Fehler (Zusammenhänge, nicht Zahlen): Längenvergleich nur fürs System gültig, Vorfall falscher Störungszone zugeordnet, Teilzahl als Gesamtzahl. Kausal-/Vergleichssätze besonders prüfen.

## Video-Log
| # | Video | Datum | Ergebnis | Erkenntnis |
|---|---|---|---|---|
| 001 | Ohne diese deutsche Erfindung würde die Welt stillstehen (Kugellager) | 15.11.2026 (f3e_nM6sLgk) | (offen) | Pilot. Sounds mehrfach getauscht (Kamera-Klick), Stimme auf elevenlabs_v4 gewechselt, Thumbnail-Stil auf dunkel/dramatisch geändert, Endkarte mit Kommentar + Glocke ergänzt. |
| 002 | Warum Europa für 11,7 Milliarden ein Loch durch die Alpen bohrt (Brenner-Basistunnel) | geplant 18.11.2026 18:00 (BugCEN8HKO0) | (offen) | Megaprojekt-Format, 11:05. Laurin wählte Titel 4 (vidIQ 76, nicht den Top-Score 82) und Thumbnail 3 „11,7 MRD. € / FÜR EIN LOCH?!“ – Geld-Schockzahl + Frage schlägt Längenangabe. |
- Musik (Laurin 17.11.2026): KEINE neuen Tracks pro Video erzeugen – nur die feste Bibliothek in assets/music nutzen. Neue Tracks nur auf ausdrücklichen Wunsch (kostet Credits).
- music_tension aus der Bibliothek gelöscht (Laurin 17.11.2026: zu anstrengend) – nicht mehr verwenden.
- BEWEGUNG statt Standbild (Laurin 17.11.2026): In Video 001 waren am Anfang die Flugzeuge nur Standbilder. Ab jetzt muss sich alles,
  was sich in echt bewegt, auch im Video bewegen (Flugzeuge fliegen, Maschinen laufen, Bänder fahren, Teile werden gepresst/gedreht) –
  als echte 3D-Animation in Blender, besonders im Hook/Cold Open. Viele animierte Szenen, kaum Stills.
  Echte Texturen/Modelle/HDRIs von Poly Haven (engine/assets.py, CC0, wie bei Goldsmith) für Rumpf, Metall, Hallenböden, Himmel.
  KI-Bilder höchstens als Ergänzung und dann mit Bewegung (2.5D-Parallaxe/Licht-Effekte aus goldsmith-pipeline engine/depth25d.py + cinemagraph.py).
  Schnell-Modus für mehr Animation: Cycles 4 Samples, 67 % Auflösung (≈4,4 s/Frame, kaum sichtbarer Unterschied).

## Ton & Musik mit audiokit (Laurin 18.11.2026)
Problem: Soundeffekte oft unpassend/billig, Musik zu gleichförmig – Laurin schaut die eigenen Videos nicht zu Ende. vidIQ-Auswertung 18.11.: größter Absprung in den ersten ~30 s; Musik läuft 1,5–3 Min. gleich durch, kein Spannungsaufbau vor Enthüllungen; Passagen von 25–60 s ohne neuen Reiz.
- `setup.sh` lädt audiokit (Repo sound-mediathek) nach /home/claude/audiokit. Die Engine nutzt es automatisch und schreibt `ton_bericht.txt` – Bericht in qa.md übernehmen.
- Sounds werden vor dem Mischen aufgeräumt: gleiche Lautheit, Einblendungs-Sounds nicht im Dauerfeuer, max. 2 Sounds gleichzeitig, keine Endlos-Schleifen, defekte Dateien fliegen raus. Geräusche zu sichtbarer Bewegung bleiben.
- Musik nach Spannungskurve: Wechsel der Stelle/des Tracks spätestens alle ~60–80 s, Anschwellen vor Enthüllungen/Zahlen, Bogen pro Kapitel, Pegel automatisch unter der Stimme. Weiterhin nur die eigene Musik-Bibliothek, keine neuen Tracks.
- Im Skript Enthüllungen klar formulieren (Zahl, „aber“, „doch“, Frage → Antwort): daraus baut die Spannungskurve.
- Bericht meldet Lücken > 22 s ohne neuen Reiz → dort Bild/Effekt/Schnitt ergänzen, bevor gerendert wird.

## Hook-Regeln (Laurin 19.11.2026 – gilt ab dem nächsten Video)
Grundlage: Auswertung erfolgreicher Ausreißer-Videos in allen 5 Nischen (vidIQ), Hook-Studie mit über 4.000 Hooks aus Videos mit über 1 Mio. Aufrufen, Aprilynne Alters Intro-Formel. Es gibt keinen einzelnen besten Hook-Typ – aber alle erfolgreichen Hooks haben diesen Aufbau:
1. **Thema in 0–5 s gesagt UND gezeigt** – genau das, was Titel und Thumbnail versprechen; das Thumbnail-Motiv ist im ersten Bild zu sehen. Kein Datum, kein Logo, keine Vorrede als erster Satz.
2. **Offene Frage / Rätsel spätestens bei 10–15 s.** Die Antwort kommt frühestens im letzten Drittel.
3. **Konkretes Versprechen vor Hook-Ende** (was man am Ende weiß, wie viele Punkte, wer dahintersteckt).
4. **Bestes Material zuerst:** die stärkste Animation / das stärkste Bild gehört in den Hook.
5. **Kurz:** Hook-Länge siehe Kanal-Regel unten. Kontext erst danach, nicht vorne stapeln.
6. **Rehook:** Jedes Kapitel endet mit einer neuen offenen Frage.

**Prüfung vor dem Rendern** (in qa.md eintragen): Sekunde, ab der das Thema klar ist (≤ 5), Sekunde der offenen Frage (≤ 15), Versprechen ja/nein, Hook-Länge (Wörter ÷ 2,4 = Sekunden).
**Nach 48 h:** Retention bei 30 s per vidIQ (audience_retention) ins Video-Log. Ziel ≥ 70 %. Unter 50 % → beim nächsten Video den Alternativ-Typ unten nehmen.
**Meisterwerk-Hook:** **„Unmögliche Frage“** („Wie kann man … bohren, ohne …?“ / „Warum stürzt … nicht ein?“) **oder Szene mit Wendung** (etwas Unmögliches beschreiben – „Und doch schwimmt es.“ – dann auflösen, was es ist). Bauteil/Projekt aus dem Titel spätestens bei 5 s im Bild (Brenner-Hook 002 war gut, aber das Thema kam erst nach ~25 s). Zahlen als greifbarer Vergleich („länger als zwei Fußballfelder“). „du“ ist hier nicht nötig. **Länge bis Titelkarte 30–45 s.**

## Sound-Bibliothek aus Laurins Sammlung (19.11.2026)
- setup.sh lädt `bibliothek/meisterwerk/` (NUR die Effekte dieses Kanals) + `bibliothek/gemeinsam/` (Foley, Atmos, Waffen) nach /home/claude/sfx-bibliothek/bibliothek. Liste: `bibliothek/meisterwerk/LISTE.md` im Repo sound-mediathek.
- **Reihenfolge bei der Sound-Wahl:** 1. eigene assets/sfx (abgenommen) → 2. Bibliothek (`import bibliothek as BIB; BIB.pick("meisterwerk", "whoosh", seed=<video-ordner>)`, `BIB.suche("auto")`) → 3. Hugging Face/SFXMint nur, wenn nichts passt.
- `seed` = Video-Ordner: so wechseln die Sounds von Video zu Video, ohne dass es zufällig klingt. Alle Bibliotheks-Sounds sind geprüft (audit.py), Memes/geschützte/kommerzielle Sounds sind aussortiert.
- Nie Effekte aus fremden Kanal-Ordnern nehmen; `reserve/` nur nach Rückfrage bei Laurin.

- Musik (21.11.2026): 3 neue eigene Tracks (werkhalle_puls, praezision_ticken, aufbau_zeitraffer) – damit hat Meisterwerk 5 eigene Tracks. Alle drei von Gemini als PREMIUM/8 von 10 bewertet, nicht corporate, nicht episch. Unter der Stimme Höhen (Ticks) bzw. Mitten (Arpeggio) absenken. Details assets/music/MUSIK.md.

## Erzähl-Bausteine nach Wissenswert-Vorbild (Laurin 22.11.2026, gilt ab dem nächsten Video)
Referenz: Wissenswert „Wie eine Spionin den größten CEO der Welt ruinierte“ (372 Tsd. Aufrufe in 2 Tagen). Passend für Meisterwerk:
- **Fun-Facts als Würze:** alle 2–3 Min. ein überraschendes, belegtes Detail (Rekord, Kuriosität, Herkunft eines Namens), als kurze 3D-Einblendung.
- **Kurze echte Clips** (2–3 s, höchstens 1 pro Minute) zwischen den Blender-Szenen: echte Werkhalle, Funken, Kran – danach Match-Cut in die 3D-Ansicht. Nur Pixabay (`stock.py`-Muster aus Goldsmith/Unterbau, Schlüssel zur Laufzeit) oder Public Domain, ohne Marken/Logos. 3D bleibt der Kern.
- **Kaltstart als Szene mit Datum + Ort** (eingetippt mit Tastatur-Sound), dann Eskalationstreppe und 3-teiliges Versprechen.
- **Rahmen:** Das erste Bild kommt am Ende verändert zurück (z. B. fertiges Bauwerk statt Baustelle).
