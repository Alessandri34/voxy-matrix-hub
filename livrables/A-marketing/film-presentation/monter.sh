#!/usr/bin/env bash
# Assemble l'image et le son, puis tire la version legere pour le web.
#
#   ./monter.sh
#
# Suppose que `node rendre.cjs` et `python3 son.py` ont deja tourne.
# Le controle du texte passe d'abord : un film non conforme ne se monte pas.
set -euo pipefail
cd "$(dirname "$0")"

python3 controler-texte.py

MAITRE=sortie/VFormations-film-presentation.mp4
WEB=sortie/VFormations-film-presentation-web.mp4

# L'image n'est pas reencodee : elle sort deja de rendre.cjs en qualite maitre.
ffmpeg -y -loglevel error -i sortie/film-muet.mp4 -i sortie/son.wav \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -ar 48000 -shortest \
  -metadata title="VFormations — la formation-action" -movflags +faststart "$MAITRE"

# Version web : 30 images par seconde, assez legere pour une page ou un courriel.
# Le son repart du WAV : recompresser un AAC deja compresse abime le son et remonte les cretes.
ffmpeg -y -loglevel error -i "$MAITRE" -i sortie/son.wav -map 0:v -map 1:a -vf fps=30 \
  -c:v libx264 -preset slow -crf 23 -pix_fmt yuv420p -profile:v high \
  -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart "$WEB"

# L'image d'affiche : le slogan, a 15 s.
ffmpeg -y -loglevel error -ss 15.2 -i "$MAITRE" -frames:v 1 -q:v 3 sortie/affiche.jpg

for f in "$MAITRE" "$WEB"; do
  printf '%s  %s Mo  ' "$f" "$(du -m "$f" | cut -f1)"
  ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate:format=duration -of csv=p=0 "$f" | tr '\n' ' '
  echo
done
