# Meisterwerk – Handschrift und Effekte (von Laurin abgenommen am 20.11.2026)

Gemeinsame Regeln: `HANDWERK.md`. Hier steht nur, was Meisterwerk von den anderen Kanälen unterscheidet.
Weitere freigegebene Animationsarten für die Nische und die Bild-Drehbuch-Regeln: `ANIMATION.md` (21.11.2026).

## Erkennungsmerkmale
| | Meisterwerk |
| --- | --- |
| Sprache | Deutsch |
| Welt | 3D-Werkhalle und Studio. Das ganze Video spielt dort |
| Technik | Blender, komplett 3D. Weil die Rechenzeit begrenzt ist, als Mischform: Einzelbilder mit Tiefeninfo plus 2,5D-Kamera, echtes 3D für Schlüsselmomente |
| Farben | Hellgrau, Stahl, Glut-Orange |
| Kamera | präzise Kranfahrt, Orbit, Makro |
| Tempo | 4–6 s, im Takt der Maschine |
| Schrift | technische Bemaßung, Laser-Gravur |
| Übergang | Match-Cut über die Form (Kugel wird Planet) |
| Zahlen und Karten | als 3D-Objekt: Stahlträger-Balken, Typenschild |
| Musik | treibend, mechanisch, Percussion-Puls |
| Stimme | Harrison |

## Effekt-Katalog (nur diese verwenden)
| Effekt | Was passiert | Wann | Status |
| --- | --- | --- | --- |
| Explosionsansicht | Das Bauteil fliegt in seine Einzelteile auseinander und setzt sich wieder zusammen | Einstieg, „Woraus besteht es?“ | neu, Stilprobe 20.11. |
| Fahrt durch die Fertigung | Die Kamera fährt mit dem Teil von Station zu Station | Herstellungsablauf | neu |
| Glühen und Abkühlen | Stahl glüht orange, wird dunkel, Dampf steigt auf | Schmieden, Härten | neu, Stilprobe 20.11. |
| Funken | Funkenregen beim Schleifen und Schweißen | Bearbeitung | steht (`sparks`) |
| Maßstab-Figur | Eine kleine graue Menschfigur steht neben der Maschine | Größe greifbar machen | neu |
| Makro-Zoom | Zoom bis auf Mikrometer, eine Maßlinie zeigt die Toleranz | Präzision | neu (baut auf `measure` auf) |
| Bemaßung | Technische Maßlinien zeichnen sich ans Teil | Abmessungen | steht (`measure`) |
| Laser-Gravur | Datum oder Zahl wird ins Metall graviert | Jahr, Ort, harte Zahl | neu, ersetzt das Tippen mit Tastatur |
| Typenschild | Eine Zahl erscheint auf einem Metallschild am Bauteil | große Zahl | neu, ersetzt `big_number` |
| Stahlträger-Diagramm | Die Balken sind Stahlträger, die ein Kran setzt | Vergleich | neu |
| Zeitraffer-Aufbau | Ein Bauwerk wächst Schicht für Schicht | Megaprojekte | neu |
| Schlag-Ruck | Die Kamera ruckt beim Pressen oder Hammerschlag | Wucht | steht (`shake`) |
| Callout | Linie zum Teil, ein Etikett klappt auf | Teil benennen | steht (`callout`) |
| Match-Cut | Die Form springt ins nächste Motiv | Kapitelübergang | neu |
| Zahnrad-Kapitelmarke | Das orange Zahnrad dreht sich ein, dahinter steht der Titel | Kapitelstart | neu, ersetzt `chapter_card` |

| Laser-Karte (`motion` map) | Messpunkte setzen sich, Orange-Laserlinien verbinden Standorte, Orte werden graviert | Lieferkette, Werke, Baustelle im Land | neu, ANOM-Wissen 23.11. |
| Fertigungsablauf 2D (`motion` flow) | Teil wandert über Stationen, Fortschrittsbalken, Abzweig „Ausschuss“ mit Schlag | Ablauf auf einen Blick (ergänzt die 3D-Fahrt durch die Fertigung) | neu, ANOM-Wissen 23.11. |
| Typenschild dreht sich (`motion` flip) | Neugier-Pause, Schild dreht sich, Auflösung glüht orange | Auflösung des Rätsels | neu, ANOM-Wissen 23.11. |
| Zahl auf Stahlplatte (`motion` counter) | Zahl zählt auf gebürsteter Platte hoch, dahinter fallen Teile | große Stückzahl | neu, ANOM-Wissen 23.11. |
| Takt-Raster (`motion` grid) | Teile füllen Reihe für Reihe im Takt, Ausschuss glüht | Stückzahl, Takt | neu, ANOM-Wissen 23.11. |
| Balken-Vergleich 2D (`motion` bars) | Stahl- gegen Glut-Balken | schneller Vergleich (ergänzt Stahlträger-Diagramm) | neu, ANOM-Wissen 23.11. |
| Blaupausen-Stapel (`motion` stack) | Konstruktionszeichnungen stapeln sich, Frage wird graviert | Konstruktion, offene Frage | neu, ANOM-Wissen 23.11. |

**Erweiterung 23.11.2026 (ANOM-Stilprobe):** Die `motion`-Bausteine kommen **zusätzlich** (nichts wird ersetzt, die 3D-Werkhalle bleibt die Welt). Eigene Formen statt nur Farben (Laurin 23.11.): massive Industrie-Piktogramme, Stationen als Sechskant-Muttern, Raster aus Muttern/Schraubenköpfen, Laser-Gravur statt Tippen, Typenschilder, Glut-Orange. Doku: `engine/motion_mw.py`. Demo: `Meisterwerk_Motion_Bausteine.mp4` (23.11.2026 an Laurin). Gemini-Casting 23.11.: Karte und Blaupausen PREMIUM; Takt-Raster mit zufälligem Aufploppen CHEAP → jetzt Reihe für Reihe im Takt; Alarm-Zischen und laute Zähler-Ticks raus.

**Raus:** Kamera-Klick als Sound bei Texteinblendungen (klingt billig), eingetippter Text mit Tastatur (gehört Goldsmith) und stehende Objekte, denn alles bewegt sich. Kein Querschnitt, der gehört Unterbau: Das Innere zeigt die Explosionsansicht.

Stilprobe: `stilprobe_meisterwerk.mp4` (20.11.2026). Sounds folgen nach dem Casting (`doku-ohren`).

## Sound je Effekt (Stand 20.11.2026, von Laurin abgenommen: „war gut“)
Geplant nach dem Grundsatz aus `HANDWERK.md`: erst festlegen, wo überhaupt ein Sound hingehört, dann je Stelle genau einen. Skripte: `engine/stilproben/ton_*.py`.

| Effekt | Sound |
| --- | --- |
| Bemaßung | woodtick |
| Explosionsansicht | lever (gekürzt) + whoosh, Kugeln landen: clink |
| Zusammenbau | whoosh, Einrasten: Musik setzt aus, thud + sub_drop + clink |
| Glühen | hiss leise |
| Laser-Gravur | grind leise, gekürzt |
| Musik | coldopen_tension (industrial_drive ist zu dicht für Effekt-Momente); Erklär-Kapitel werkhalle_puls, Präzision praezision_ticken, Megaprojekte aufbau_zeitraffer (alle drei 21.11.2026, siehe assets/music/MUSIK.md) |
