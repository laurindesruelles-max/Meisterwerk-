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
echo "Workdir bereit: $WORK"
