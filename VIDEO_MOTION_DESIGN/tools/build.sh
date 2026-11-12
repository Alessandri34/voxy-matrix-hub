#!/usr/bin/env bash
# Full rebuild of the Voxy Matrix motion design video.
# Requires: node + playwright (chromium), python3 + numpy + scipy, ffmpeg.
# Usage: bash tools/build.sh [frames_dir]
set -euo pipefail
cd "$(dirname "$0")/.."
FRAMES="${1:-build/frames}"
FPS=60
WORKERS=4
mkdir -p "$FRAMES" build

echo "→ Rendu des images ($FPS fps, $WORKERS workers)…"
for i in $(seq 0 $((WORKERS-1))); do
  node tools/render.js "$FRAMES" "$FPS" 0 60 "$i" "$WORKERS" &
done
wait

echo "→ Sound design…"
python3 tools/sound_design.py build/sound_raw.wav

echo "→ Encodage final…"
ffmpeg -y -loglevel error -framerate "$FPS" -i "$FRAMES/%05d.jpg" -i build/sound_raw.wav \
  -af "loudnorm=I=-14:TP=-1:LRA=9" -ar 48000 \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -profile:v high -movflags +faststart \
  -c:a aac -b:a 256k -shortest VOXY_MATRIX_Motion_16x9.mp4
echo "✓ VOXY_MATRIX_Motion_16x9.mp4"
