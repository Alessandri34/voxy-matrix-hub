# Raccourcis. Chaque cible fait une chose et dit ce qu'elle fait.
.PHONY: help up down logs shell test lint migrate superuser backup restore secret

help:            ## Liste les commandes disponibles
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-12s %s\n", $$1, $$2}'

up:              ## Demarre toute la stack en arriere-plan
	docker compose up -d

down:            ## Arrete la stack (les donnees restent dans les volumes)
	docker compose down

logs:            ## Affiche les journaux en continu
	docker compose logs -f --tail=100

shell:           ## Ouvre un shell Django dans le conteneur web
	docker compose exec web python manage.py shell

migrate:         ## Applique les migrations
	docker compose exec web python manage.py migrate

superuser:       ## Cree un compte administrateur
	docker compose exec web python manage.py createsuperuser

test:            ## Lance les tests
	pytest -q

lint:            ## Verifie le format et les regles de style
	ruff check . && ruff format --check .

backup:          ## Sauvegarde chiffree de la base, copiee hors du VPS
	./scripts/backup.sh

restore:         ## Restaure un dump : make restore FICHIER=backups/xxx.sql.gz.gpg
	./scripts/restore.sh $(FICHIER)

secret:          ## Genere une SECRET_KEY a coller dans le .env
	@python3 -c "import secrets; print(secrets.token_urlsafe(64))"
