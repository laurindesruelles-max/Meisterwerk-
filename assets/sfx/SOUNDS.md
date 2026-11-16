# Geräusch-Bibliothek Meisterwerk (assets/sfx)

Neu seit 16.11.2026: echte CC0-Aufnahmen von SFXMint (über Hugging Face flreey/sfxmint-cc0-sound-effects bzw. SFXMint-API), auf Rauschen geprüft, gesäubert, lautheitsnormalisiert. Frei nutzbar, keine Quellenangabe nötig.

**Regel:** Jede sichtbare Bewegung bekommt ihr echtes Geräusch (Presse = hammer, Maschine läuft = machine_engine, Ventil = pneumatic_hiss …) – per `engine/clip_sounds.py` direkt an die Blender-Frames gehängt. Nie selbst synthetisierte Sounds. Text-Einblendungen weiterhin `shutter` (Kamera-Klick), Daten/Orte Tastatur key0–7.

| Name | Quelle (SFXMint-ID) | Inhalt |
|---|---|---|
| amb_factory | factory-machinery-ambience-01 | A factory machinery ambience sound for industrial levels and workshop scenes in games and videos. |
| machine_engine | mechanical-engine-39 | An engine running sound for vehicles and machinery backgrounds in games and videos. |
| lever | mechanical-lever-36 | A lever pull sound for puzzles and mechanisms, or for dungeon switches, in games. |
| hammer | hammer-01 | A hammer sound for building and repair, or for crafting games, in games and videos. |
| filing_metal | steel-spike-scrape-01 | A steel spike scrape sound for spike traps and blades scraping metal in games and videos. |
| step_metal | boot-step-on-metal-plate-01 | A single footstep sound for single steps and animation timing in games and videos. |
| iron_gate | iron-gate-01 | A metal gate rattling, for fences. |
| car_pass | car-pass-by-01 | Auto fährt vorbei |
| car_arrive | car-slowing-to-a-stop-04 | Auto rollt heran und hält |
| car_door | car-door-opening-and-closing-01 | Autotür auf und zu |
| footsteps_street | footsteps-concrete-03 | Dark footsteps on concrete for walking characters and city scenes in games and videos. |
| clock_tick | metronome-ticking-01 | A mechanical pendulum metronome ticking evenly at a moderate pace. |
| elevator_ding | office-elevator-08 | An elevator ding sound for elevators and arrival cues in videos, games and apps. |
| pneumatic_hiss | air-hiss-01 | Luftdruck-Zischen (Pneumatik, Ventile) |
| grind | stone-mill-grinding-01 | Schweres, langsames Schleifen/Mahlen |
| hand_saw | hand-saw-01 | Handsäge |

Fehlt ein Geräusch: zuerst Hugging-Face-Sample (kostenlos), dann SFXMint-API (Schlüssel bei Laurin, 5/Tag, nie ins Repo), Higgsfield mirelo nur als letzte Wahl. Weitere passende Kandidaten im SFXMint-Katalog: mechanical-machine-36…41, factory-machinery-ambience-02 (Loop), bench-grinder-01.
