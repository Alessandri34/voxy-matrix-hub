#!/usr/bin/env bash
# Usage : ./deploy.sh root@IP_DU_VPS
# Copie le projet + .env sur le VPS, installe Docker si besoin et (re)demarre le service.
set -euo pipefail

TARGET="${1:?Usage: ./deploy.sh root@IP_DU_VPS}"
DIR=/opt/automation-leads
cd "$(dirname "$0")"

[ -f .env ] || { echo "Cree d'abord .env (cp .env.example .env)"; exit 1; }

ssh "$TARGET" "command -v docker >/dev/null || curl -fsSL https://get.docker.com | sh; mkdir -p $DIR/data && chown 1000:1000 $DIR/data"
tar czf - --exclude=data --exclude=test . | ssh "$TARGET" "tar xzf - -C $DIR"
ssh "$TARGET" "cd $DIR && chmod 600 .env && docker compose up -d --build && docker compose ps"

DOMAIN=$(grep '^DOMAIN=' .env | cut -d= -f2)
echo
echo "Deploye. Test : curl https://$DOMAIN/health"
echo "Logs     : ssh $TARGET 'cd $DIR && docker compose logs -f leads'"
