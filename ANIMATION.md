# Meisterwerk – Animations-Möglichkeiten (Laurin, 21.11.2026)

Ergänzt `EFFEKTE.md` (abgenommener Kern-Katalog) um alles, was zur Nische passt: Fertigung, Maschinen, Megaprojekte. Alles spielt weiter in der **3D-Werkhalle / im Studio** (Hellgrau, Stahl, Glut-Orange). Exklusiv-Regeln bleiben: kein Querschnitt (Unterbau – das Innere zeigt die Explosionsansicht), keine Tastatur-Tipp-Schrift (Goldsmith), nichts steht still. Für jedes Skript gilt das Bild-Drehbuch aus `HANDWERK.md`.

## Zeit und Geschehen in dieser Nische
- **Zeit:** Fertigungsschritte mit **echter Dauer** (Sekunden-Takt, Ofenzeit, Bauzeit in Jahren) – als Taktuhr, Zeitlupe oder Zeitraffer exakt zeigen. Jahr der Erfindung per Laser-Gravur.
- **Geschehen:** Jeder Fertigungsschritt zeigt den **physikalischen Moment** (Stahl verformt sich, Funken, Material fließt) – nicht nur das fertige Teil. Reihenfolge muss stimmen.
- **Zahlen:** Maße, Toleranzen, Kräfte **exakt** mit Einheit, immer mit greifbarem Vergleich (Haar, Bus, Fußballfeld).
- **Neugier-Lücke:** Teil zuerst nur als Silhouette oder in Einzelteilen zeigen („Was wird das?“), zusammengesetzt erst später.

## Animations-Katalog (zusätzlich zu EFFEKTE.md)
| Animation | Was passiert | Wann | Genauigkeit | Werkzeug | Status |
| --- | --- | --- | --- | --- | --- |
| Physik-Simulation | Metall verformt sich unter der Presse, Flüssigstahl fließt in die Form, Teile fallen echt | Umformen, Gießen | exakt | Blender (Rigid Body, Fluid) | bauen |
| Werkzeugbahn | Eine leuchtende Bahn zeichnet vor, wo Fräser/Laser gleich schneiden, dann schneidet er | CNC, Laser | exakt | Blender Grease Pencil | bauen |
| Schweißnaht wächst | Die Naht wächst Punkt für Punkt mit Glut und Funken | Schweißen | exakt | Blender Geometry Nodes | bauen |
| Taktuhr | Neben dem Band läuft eine Uhr, bei jedem fertigen Teil springt ein Zähler | „1 Teil alle 3 Sekunden“ | exakt | Blender + Typenschild | bauen |
| Zeitlupe mit Zähler | Der entscheidende Moment läuft in Zeitlupe, eine Bemaßung zeigt die echte Dauer (z. B. 0,02 s) | Aufprall, Pressen | exakt | Blender | bauen |
| Roboter-Choreografie | Roboterarme greifen, drehen, setzen ein – synchron im Takt | Montage | schema | Blender (IK-Rig) | bauen |
| Bauplan wird Stahl | Eine Konstruktionszeichnung liegt flach, Linien heben sich ab und werden zum 3D-Teil | Konstruktion, Erfindung | schema | Grease Pencil → Mesh | bauen |
| Kraftfluss | Farbige Spannungsverläufe (Blau → Orange) laufen durchs Bauteil, wenn Last kommt | Belastung, Statik | schema | Blender Shader | bauen |
| Größenvergleich | Kamera fährt zurück, neben dem Teil erscheinen Mensch, Bus, Fußballfeld | Dimension | exakt | Blender | bauen (Maßstab-Figur steht als Idee) |
| Physik-Formel graviert | Die Formel wird ins Metall graviert, die Werte setzen sich ein | Warum es funktioniert | exakt | Manim → Laser-Gravur | bauen |
| Baustellen-Zeitraffer | Kräne drehen, Stockwerke wachsen, Tag/Nacht wechseln, Jahr am Bauschild zählt mit | Megaprojekt | exakt | Blender Geometry Nodes | steht als Idee (Zeitraffer-Aufbau), bauen |
| Materialkunde-Zoom | Zoom ins Gefüge: Körner/Kristalle des Stahls ordnen sich beim Härten | Härten, Material | schema | Blender Partikel | bauen |
| Echte Fertigung im Werkstatt-Monitor | Echter Pixabay-Clip läuft auf einem Monitor in der Werkhalle | echte Bilder | exakt | stock.py | bauen |
| Fehler-Szenario | Teil mit Fehler: Riss wächst, Teil bricht – dann richtig gefertigt | Warum Präzision zählt | exakt | Blender (Fracture) | bauen |

## Werkzeuge (alle ohne Credits, getestet 21.11.2026)
| Werkzeug | Wofür | Einrichten |
| --- | --- | --- |
| Blender (`bpy`) | echtes 3D, Physik (Rigid Body, Flüssigkeit, Stoff, Partikel), Geometry Nodes für Wachstum/Aufbau, Grease Pencil für gezeichnete Linien im Raum, Rigging für Figuren | `pip install bpy` (setup.sh) |
| 2,5D-Tiefe (`depth25d.py`, Depth Anything) | jedes Standbild in Ebenen zerlegen, Kamera fährt mit Tiefe hindurch, Ebenen bewegen sich einzeln | im Goldsmith-/Unterbau-Repo vorhanden |
| PIL + numpy + ffmpeg | eigene Motion-Grafik, Partikel, Licht, Übergänge, Compositing | vorhanden |
| Manim | exakte, animierte Diagramme, Netzwerke, Abläufe, Formeln, Zählwerke – danach im Kanal-Look eingefärbt | `apt-get install -y libpango1.0-dev libcairo2-dev && pip install manim` |
| rlottie | Lottie-Vektoranimationen (Icons, kleine Abläufe) als Vorlage, immer im Kanal-Stil nachgezeichnet | `pip install rlottie-python` |
| Pixabay, Wikimedia, Archive | echte Clips und Fotos, nur innerhalb der Kanal-Welt eingebaut (siehe HANDWERK.md) | `stock.py`, `sources.py` |
| Higgsfield | nur KI-**Bilder** (0,25 Credits), Freistellen, 3D-Modell aus Bild. **Keine KI-Videoclips** (Laurin 21.11.2026) | – |

Status in den Tabellen: **steht** = in der Engine vorhanden · **bauen** = freigegeben (Laurin 21.11.2026), beim ersten Einsatz als Baustein in die Engine aufnehmen und kurz Stilprobe an Laurin.
