#!/usr/bin/env bash
# Reconstruit le film : bande-son → images → encodage H.264.
# Prérequis : node + playwright (Chromium), ffmpeg, python3 (numpy, scipy).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build out
python3 audio.py build/soundtrack.wav
rm -rf build/frames
node render.cjs --fps 60 --workers "${WORKERS:-4}"
# normalisation du niveau sonore à -14 LUFS (cible des plateformes sociales)
I=$(ffmpeg -hide_banner -nostats -i build/soundtrack.wav -af ebur128 -f null - 2>&1 | awk '/I:/{v=$2} END{print v}')
GAIN=$(python3 -c "print(round(-14 - ($I), 2))")
ffmpeg -y -loglevel error -framerate 60 -i build/frames/%05d.png -i build/soundtrack.wav \
  -vf "scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p" \
  -c:v libx264 -preset slow -crf "${CRF:-17}" -profile:v high -level 4.2 -g 120 \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
  -af "volume=${GAIN}dB" -c:a aac -b:a 256k -ar 48000 -movflags +faststart -shortest out/voxy-motion-design.mp4
ffmpeg -y -loglevel error -i build/soundtrack.wav -af "volume=${GAIN}dB" -c:a aac -b:a 192k out/voxy-soundtrack.m4a
ffmpeg -y -loglevel error -ss 50 -i out/voxy-motion-design.mp4 -frames:v 1 -q:v 2 out/voxy-poster.jpg
echo "OK → out/voxy-motion-design.mp4 (gain audio ${GAIN} dB)"
