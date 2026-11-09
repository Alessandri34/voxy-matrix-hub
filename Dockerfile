FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Les dependances d'abord : leur couche est mise en cache tant que
# pyproject.toml ne bouge pas, donc un changement de code ne les reinstalle pas.
COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install .

COPY . .

# L'application ne tourne pas en root.
RUN useradd --create-home --uid 1000 app && chown -R app:app /app
USER app

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
