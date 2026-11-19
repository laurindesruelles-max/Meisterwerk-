#!/bin/sh
# Usage: sh setup.sh <work_dir>   -> legt work_dir mit sfx/, music/ an und installiert Blender (bpy)
set -e
REPO=$(cd "$(dirname "$0")" && pwd); WORK="${1:-/home/claude/mw-work}"
mkdir -p "$WORK/sfx" "$WORK/music" "$WORK/img" "$WORK/vo" "$WORK/vo2" "$WORK/r2" "$WORK/t" "$WORK/t3"
cp "$REPO"/assets/sfx/*.wav "$WORK/sfx/"; cp "$REPO"/assets/music/*.mp3 "$WORK/music/"
python3 -c "import bpy" 2>/dev/null || pip install bpy --break-system-packages -q
# Tastatursounds (nicht im Repo) aus Laurins Higgsfield-Speicher
if [ ! -f "$WORK/sfx/key0.wav" ]; then
  curl -sSfL -o /tmp/mw_keys.zip "https://d2ol7oe51mr4n9.cloudfront.net/user_3LhrXzDQGZeDXCNfJbMSIhJMEcn/a97d9544-3788-456e-802a-03b6847d4f8c.zip" && (cd "$WORK/sfx" && unzip -oq /tmp/mw_keys.zip) || echo "WARNUNG: Tastatursounds nicht ladbar"
fi
# Laurins Sound-Bibliothek (19.11.2026): eigene Effekte dieses Kanals + gemeinsame Geräusche -> /home/claude/sfx-bibliothek/bibliothek
python3 -c "import sys; sys.path.insert(0, '$AK'); import bibliothek; print('Sound-Bibliothek bereit:', bibliothek.ensure('meisterwerk'))" || echo "WARNUNG: Sound-Bibliothek nicht geladen"
# Meisterwerk hat eigene Effekte (assets/sfx) – die Goldsmith-Bibliothek wird nicht eingebunden (Laurin 17.11.2026: jeder Kanal eigene Effekte)
# Ton-Werkzeug audiokit (18.11.2026): Sounds aufräumen, Musik nach Spannungskurve, Endkontrolle.
# Gemeinsam sind nur die Regeln – Sounds und Musik bleiben kanal-eigen. Repo: laurindesruelles-max/sound-mediathek
AK="${AUDIOKIT:-/home/claude/audiokit}"
if [ ! -f "$AK/adapter.py" ] || [ -n "$AK_UPDATE" ]; then
  AKT=$(mktemp -d); git clone -q --depth 1 https://github.com/laurindesruelles-max/sound-mediathek "$AKT/r" && mkdir -p "$AK" && cp "$AKT"/r/audiokit/*.py "$AKT"/r/audiokit/*.json "$AK"/ && echo "audiokit bereit: $AK"; rm -rf "$AKT"
fi
echo "Workdir bereit: $WORK"
