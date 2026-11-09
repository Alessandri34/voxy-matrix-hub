#!/usr/bin/env bash
# Sauvegarde chiffree de la base, copiee hors du VPS.
#
# Une sauvegarde qui reste sur la machine qu'elle protege ne protege rien :
# si le VPS brule, elle brule avec. D'ou la copie distante, et d'ou le
# chiffrement, puisqu'elle part chez un tiers.
set -euo pipefail

cd "$(dirname "$0")/.."
[ -f .env ] || { echo "ERREUR : .env introuvable" >&2; exit 1; }
set -a; . ./.env; set +a

: "${BACKUP_PASSPHRASE:?BACKUP_PASSPHRASE est vide — sans elle, aucune restauration}"
: "${POSTGRES_USER:?}"; : "${POSTGRES_DB:?}"

DOSSIER=backups
RETENTION_JOURS=${BACKUP_RETENTION_JOURS:-30}
HORODATAGE=$(date -u +%Y%m%dT%H%M%SZ)
FICHIER="$DOSSIER/${POSTGRES_DB}-${HORODATAGE}.sql.gz.gpg"

mkdir -p "$DOSSIER"

echo "1/4  Dump de la base $POSTGRES_DB"
docker compose exec -T db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists \
  | gzip -9 \
  | gpg --batch --yes --symmetric --cipher-algo AES256 \
        --passphrase "$BACKUP_PASSPHRASE" --output "$FICHIER"

TAILLE=$(du -h "$FICHIER" | cut -f1)
echo "2/4  Ecrit : $FICHIER ($TAILLE)"

# Un dump qu'on n'a pas su relire n'est pas une sauvegarde. On verifie
# qu'il se dechiffre et que le gzip est entier, a chaque fois.
echo "3/4  Verification du fichier"
gpg --batch --quiet --decrypt --passphrase "$BACKUP_PASSPHRASE" "$FICHIER" \
  | gzip -t && echo "     dechiffrement et archive : corrects"

if [ -n "${BACKUP_REMOTE:-}" ]; then
  echo "4/4  Copie vers $BACKUP_REMOTE"
  rclone copy "$FICHIER" "$BACKUP_REMOTE" --quiet
  echo "     copie distante faite"
else
  echo "4/4  BACKUP_REMOTE est vide : AUCUNE copie hors du VPS."
  echo "     Le critere de sortie de la phase 0 n'est pas rempli tant qu'il l'est."
fi

find "$DOSSIER" -name '*.sql.gz.gpg' -mtime "+$RETENTION_JOURS" -delete
echo "Termine. Conservation locale : $RETENTION_JOURS jours."
