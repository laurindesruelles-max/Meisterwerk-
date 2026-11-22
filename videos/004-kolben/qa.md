# Prüfbericht – 004-kolben (2026-11-23)

## 1. Technik (automatisch, engine/qa.py)
- [x] OK: Länge 10:04 (Minimum 8:00)
- [x] OK: Bild 1920x1080
- [x] OK: Tonspur vorhanden
- [x] OK: Lautheit -14.1 LUFS (Ziel -14 ±2,5)
- [x] OK: Spitzenpegel -2.4 dBFS (max. −0,5)
- [x] OK: Schwarzbilder mitten im Video: keine
- [x] OK: Standbild-Stellen (≥4 s ohne Bewegung): 3 bei 353.20, 357.45, 523.25 s
- [x] OK: Dateigröße 324 MB (Info – Upload-Kopie muss < 299 MB sein)
- [x] Kontaktbogen `qa_frames.jpg` + 8 Zwischen-Kontaktbögen angesehen. Behoben: Kapiteltitel zu breit (Autofit), Diagramm-Text am Rand, Callouts auf Endkarte, Spalt-Szene (3D zu dunkel → 2D-Makro), Schild/Maßlinie überlappend.
- Standbild-Stellen 353/357/523 s = 2D-Diagramme (Makro Bolzen, Gleitschicht) mit langsamer Eigenbewegung – akzeptiert.


## 0. Hook, Bild-Drehbuch, 60-%-Check
- Thema: „Dieser Kolben …“ ab 0,4 s gesagt, Kolben im ersten Bild (Thumbnail-Motiv) ✓
- Offene Frage: „Er ist nicht rund. Und er ist nicht gerade.“ bei ≈ 11–14 s ✓; Kernfrage „Warum … schief?“ bei ≈ 24 s
- Versprechen: „Am Ende weißt du, warum ein perfekt runder Kolben deinen Motor zerstören würde“ ✓
- Hook-Länge bis Titelkarte: 47 s (108 Wörter) – 2 s über Ziel 45 s
- Bild-Drehbuch `bilddrehbuch.json`: engine/bilddrehbuch.py → **0 Fehler**, 180 Einstellungen, 18,1 Bild-Ereignisse/Min. Hinweis: Prüfskript liest das Wort „am“ als Uhrzeit (a.m.) → im Drehbuch-Satz „an dem“ geschrieben.
- Rehook am Ende jedes Kapitels (110, 210, 310, 411, 513) ✓; Auflösung erst in Kapitel 5 (6:45) ✓
- Kein Abschnitt > 20 s ohne neue Bewegung/Enthüllung/Frage (Ereignisse ≤ 6 s laut Drehbuch)

## 1b. Ton (doku-ohren)
- Stimme: Harrison, elevenlabs_v4, 67 Blöcke; Tempo 1,03; ASR-Abgleich (faster-whisper small): 92.7 % roh, **96,4 %** ohne Zahlwörter (Ziffern vs. Wörter) ✓
- earshot critique (Vollvideo, Profil fern/Simplicissimus/Netflix): VERDICT: launch-grade - 23 of 23 scored metrics in range (weighted 100%), 0 critical and 0 major issues.
  - Erst „1 major: lauteste 3 s nur 1,4 LU über Integrated“ → Kapitelkarten als Musik-Akzent ohne Stimme (+13 dB), Treffer-Bus, Limiter lockerer → behoben
- Gemini (gemini-3-flash-preview): Vorschau 0–2:30 Ton **PREMIUM**; Vollvideo **PREMIUM**. Kritik umgesetzt: Messuhr-Ticks leiser, Explosionsansicht mit tiefem Thud, weniger Klicks. Gemini-Hinweis offen: Legierungs-Passage (3:18–3:37) eher trocken, Stahlkolben am Ende wirkt angehängt.
- sk.py check: −14,1 LUFS, TP −2,4 dBTP, 110 Schnitte, 97 % mit Onset ±100 ms
- Musik-Abstand zur Stimme (pyloudnorm, 8-s-Fenster): 20s: 12.4 dB, 95s: 13.4 dB, 200s: 11.6 dB, 300s: 19.6 dB, 420s: 12.8 dB, 540s: 12.6 dB (Ziel 10–12; bei 300 s ruhige Trackstelle)
- Musik: ein Track je Kapitel ab Kapitelkarte (coldopen_tension, praezision_ticken, werkhalle_puls, aufbau_zeitraffer, praezision_ticken, coldopen_tension, werkhalle_puls), Ducking ~9 dB, Swells +7 dB (h2, 104, 307, 408, 508, 607), Musikpausen vor 505 (Kolbenfresser), 511 (rund) und Einrasten 605 mit Treffer
- Effekte: ~8 Ereignisse/Min (Ziel ~6) – meist Szenen-Geräusche an sichtbarer Bewegung; Kapitel-Sound industrial_electromagnetic_launcher_01; Laser-Gravur statt Tastatur (EFFEKTE.md); text_click nur an Typenschildern
## Sound-Casting (Gemini gemini-3-flash-preview, 22.11.2026)
Runde 1: Drehmaschine fs530764 PREMIUM · Gießen fs780503 PREMIUM · Abschrecken fs85482 PREMIUM · Motor fs401552 OK (raus) · Zündung fs73259 PREMIUM · Förderband fs438150 OK (raus) · Wasserstrahl fs532492 OK (raus) · Ofen fs31566 PREMIUM · Bohren fs185232 OK (raus → Drehmaschinen-Sound)
Runde 2: Wasserstrahl fs532823 PREMIUM (genommen) · fs852533 OK · fs798005 CHEAP · Motor fs556692 OK · mechanical_engine_39 PREMIUM (genommen) · factory_machinery_ambience_01 PREMIUM (genommen)


## 2. Fakten (unabhängiger Faktencheck durch separaten Agenten)
Zwei getrennte Agenten: (A) Sprechtext vor dem Einsprechen, (B) Einblendungen + Beschreibung nach dem Schnitt.
| Aussage | Quelle | stimmt? | Korrektur (umgesetzt) |
|---|---|---|---|
| 1.12.1920 Gründung durch Hermann UND Ernst Mahle | mahle-stiftung.de, Wikipedia | nein | „Hermann Mahle fing an … 2 Jahre später Ernst“ |
| Bolzenbohrung ≈ 1 µm größer, Haar 50–100× | MAHLE-Buch Tab. 2.2 | nein | „2–5 Tausendstel mm, Haar ≈ 20× dicker“ |
| „600 Mio. Mal auf und ab“ | Rechnung | nein | „600 Mio. Hübe“ |
| Gas bis 3.000 °C | Motorenliteratur | teilweise | „kurzzeitig weit über 2.000 °C“ |
| 12 t „so viel wie ein Linienbus“ | Rechnung, Busgewicht | teilweise | „leerer Linienbus“ |
| > 2.000 g, Kampfpilot 9 g | Cycle World, PBS | teilweise | g nur im Umkehrpunkt; Pilot-Vergleich gestrichen |
| Bentley „französische Rennmotoren“ | Wikipedia | teilweise | „Motoren seiner französischen Sportwagen“ |
| Auslagern 250 °C | AFE 4/2021 | teilweise | „rund 200 °C“ |
| oben „ein paar Zehntel“ dünner | MAHLE, EngineLabs | teilweise | „an den Ringen“ |
| Salzkern bei allen Kolben | AutoBild, MAHLE | teilweise | „bei Kolben mit Kühlkanal“ |
| 200.000 km Pflicht | – | unbelegt | „soll ein Motorleben halten, oft 200.000 km und mehr“ |
| Schild „0,001 mm“ | MAHLE (Form ≈ 7 µm) | nein | „≈ 0,007 mm Formtoleranz am Schaft“ |
| Schild „12 t Druck“ | Rechnung | teilweise | „bis 12 t Kraft“ |
| Schild „– 25 °C“ | automotiveworld (bis 25 K) | teilweise | „bis – 25 K“ |
| Schild „≈ 0,1–0,5 mm“ | EngineLabs (≈ 0,5 mm Beispiel) | teilweise | „bis ≈ 0,5 mm (Beispiel)“ |
| Maß „Ø 86,000“ | – | nein | „Ø PRÜFEN“ |
| „≈ 400 kg“, „100 MIO.“, „600 MIO.“, „ALU ≈ 2×“ | Rechnung/MAHLE | teilweise | „> 400 kg“, „≈ 100 MIO.*“, „≈ 600 MIO.“, „fast 2×“ |
| übrige Zahlen (200/s, 100 km/h, 120/200 bar, 660/800/500 °C, 1913/1920/1922, 2014 Rottweil, 3–5 %, 12 % Si, Schichtdicken, Spiel 0,03–0,04 mm) | siehe Beschreibung | ja | – |
- [x] Jede Zahl, jedes Datum, jeder Name geprüft; alles mit „nein“/„unbelegt“ geändert. Offen (Hinweis): Rechnung 0,34 mm vs. Spalt vernachlässigt Zylinderdehnung – im Text als „um ein Vielfaches“ formuliert.

## 3. Recht (keine Rechtsberatung – Sorgfaltsprüfung)
- [x] Äußerungsrecht (MAHLE nur mit belegten, eigenen Angaben „nach eigenen Angaben“, Personen Bentley/Mahle nur historische Fakten): Tatsachen nur mit Beleg; Vorwürfe/laufende Verfahren als „Vorwurf“/„laut …“; Urteile korrekt (Gericht, Jahr); Meinung als Meinung erkennbar; keine Beleidigung, keine Spekulation über Privates
- [x] Personen (keine Fotos, keine Gesichter): keine echten Fotos, keine realistischen KI-Gesichter realer Personen, keine Privatpersonen identifizierbar
- [x] Marken (keine Logos; MAHLE/Bentley nur beschreibend; Unabhängigkeits-Hinweis in der Beschreibung): keine Logos/Markenzeichen im Bild oder Thumbnail; Markennamen nur beschreibend; Hinweis „not affiliated/endorsed“ in der Beschreibung
- [x] Titel und Thumbnail (Kolben ist absichtlich unrund – belegt; 12 t = Maximalwert Diesel, belegt) versprechen nichts, was das Video nicht belegt (kein irreführender Vorwurf)

## 4. Lizenzen (Protokoll)
| Material | Quelle | Lizenz |
|---|---|---|
| Sprecherstimme | Higgsfield (Preset-Stimme) | Higgsfield-Abo (kommerzielle Nutzung laut Plan) |
| Thumbnail / alle Bilder | eigene Blender-Szenen | eigen |
| Musik | assets/music (ElevenLabs über Higgsfield) | Higgsfield-Abo |
| Geräusche | assets/sfx + sound-bibliothek (CC0, text_click von Laurin) + Freesound: fs530764, fs780503, fs31566, fs532823 (CC0), fs85482 JasonElrod (CC BY 3.0), fs73259 junggle (CC BY 4.0) – Urheber in der Beschreibung | CC0 / CC BY |
| 3D-Modelle/Materialien | eigene Blender-Geometrie, prozedurale Materialien | eigen |
| Schriften | Inter / Inter Display | SIL OFL |
- [x] Kein fremdes Material (Filmausschnitte, Fotos, Musik) außer den oben gelisteten Quellen

## 5. YouTube
- [x] KI-Kennzeichnung: keine KI-Bilder/-Clips, alles erkennbar 3D-Animation → „Veränderte oder synthetische Inhalte“: nein nötig (Stimme ist KI-Stimme, das betrifft die Regel nicht, da keine reale Person imitiert wird)
- [x] Beschreibung: Quellenliste, Kapitel, Marken-Hinweis; keine < oder > Zeichen
- [x] Werbefreundlich: keine Gewaltbilder, keine Schimpfwörter, keine reißerischen Schock-Thumbnails mit Verletzungen

## Ergebnis: TECHNIK OK · Ton launch-grade · Fakten geprüft (2 Agenten) · Recht/Lizenzen abgehakt → Laurin zur Freigabe
