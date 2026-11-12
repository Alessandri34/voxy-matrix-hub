#!/usr/bin/env bash
# Assemble l'image et le son, puis tire la version legere — pour chaque format rendu.
#
#   ./monter.sh
#
# Suppose que `node rendre.cjs` (et, pour le vertical, `node rendre.cjs --format vertical`)
# puis `python3 son.py` ont deja tourne. Les deux formats portent LE MEME son :
# ils sortent de la meme composition, avec les memes reperes.
# Le controle du texte passe d'abord : un film non conforme ne se monte pas.
set -euo pipefail
cd "$(dirname "$0")"

python3 controler-texte.py

[ -f sortie/son.wav ] || { echo "sortie/son.wav manque : lancer python3 son.py" >&2; exit 1; }

montes=0
monter() {  # $1 : suffixe du format ("" pour le paysage, "-vertical")
  local muet="sortie/film-muet$1.mp4"
  [ -f "$muet" ] || return 0
  local maitre="sortie/VFormations-film-presentation$1.mp4"
  local web="sortie/VFormations-film-presentation$1-web.mp4"

  # L'image n'est pas reencodee : elle sort deja de rendre.cjs en qualite maitre.
  ffmpeg -y -loglevel error -i "$muet" -i sortie/son.wav \
    -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -ar 48000 -shortest \
    -metadata title="VFormations — la formation-action" -movflags +faststart "$maitre"

  # Version legere : 30 images par seconde, pour une page, un courriel ou une relecture.
  # Le son repart du WAV : recompresser un AAC deja compresse abime le son et remonte les cretes.
  ffmpeg -y -loglevel error -i "$maitre" -i sortie/son.wav -map 0:v -map 1:a -vf fps=30 \
    -c:v libx264 -preset slow -crf 23 -pix_fmt yuv420p -profile:v high \
    -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart "$web"

  # L'image d'affiche : le slogan, a 15 s.
  ffmpeg -y -loglevel error -ss 15.2 -i "$maitre" -frames:v 1 -q:v 3 "sortie/affiche$1.jpg"

  for f in "$maitre" "$web"; do
    printf '%s  %s Mo  ' "$f" "$(du -m "$f" | cut -f1)"
    ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate:format=duration -of csv=p=0 "$f" | tr '\n' ' '
    echo
  done
  montes=$((montes + 1))
}

monter ""
monter "-vertical"
[ "$montes" -gt 0 ] || { echo "aucune image dans sortie/ : lancer node rendre.cjs" >&2; exit 1; }
