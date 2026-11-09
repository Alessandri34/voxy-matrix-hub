#!/usr/bin/env bash
# Restauration d'un dump chiffre.
#
# AVERTISSEMENT : cette commande ECRASE la base en place. Elle demande une
# confirmation tapee a la main, et elle prend un dump de securite avant.
set -euo pipefail

cd "$(dirname "$0")/.."
FICHIER="${1:-}"
[ -n "$FICHIER" ] || { echo "Usage : ./scripts/restore.sh backups/xxx.sql.gz.gpg" >&2; exit 1; }
[ -f "$FICHIER" ] || { echo "ERREUR : $FICHIER introuvable" >&2; exit 1; }
set -a; . ./.env; set +a
: "${BACKUP_PASSPHRASE:?}"; : "${POSTGRES_USER:?}"; : "${POSTGRES_DB:?}"

echo "AVERTISSEMENT"
echo "  La base $POSTGRES_DB va etre REMPLACEE par le contenu de :"
echo "  $FICHIER"
echo "  Tout ce qui a ete saisi depuis ce dump sera perdu."
read -r -p "Taper exactement REMPLACER pour continuer : " reponse
[ "$reponse" = "REMPLACER" ] || { echo "Annule — rien n'a ete touche."; exit 1; }

SECOURS="backups/avant-restauration-$(date -u +%Y%m%dT%H%M%SZ).sql.gz"
echo "1/3  Dump de securite de l'etat actuel"
mkdir -p backups
docker compose exec -T db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" | gzip -9 > "$SECOURS"
echo "     $SECOURS"

echo "2/3  Restauration"
gpg --batch --quiet --decrypt --passphrase "$BACKUP_PASSPHRASE" "$FICHIER" \
  | gunzip \
  | docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" --quiet

echo "3/3  Migrations, au cas ou le dump precede le code"
docker compose exec -T web python manage.py migrate --noinput

echo "Termine. Dump de securite conserve : $SECOURS"
