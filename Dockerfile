# =============================================================================
# agente-ia-youtube — Dockerfile (Multi-stage Build)
# =============================================================================
# Stage 1 (builder): Instala Poetry y dependencias de producción en un venv.
# Stage 2 (runtime): Imagen slim con solo el venv compilado y el código fuente.
#
# Build:
#   docker build -t agente-ia-youtube .
#
# Run:
#   docker run -p 8000:8000 --env-file .env agente-ia-youtube
#
# Seguridad: Ejecuta como usuario no-root (appuser).
# =============================================================================

# --- Stage 1: Builder ---
FROM python:3.12-slim AS builder

# Seteamos variables de entorno para Python y Poetry
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=2.2.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Instalamos dependencias de sistema mínimas para construir paquetes
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalamos Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app

# Copiamos solo los archivos de dependencias para aprovechar el cache de capas
COPY pyproject.toml poetry.lock ./

# Instalamos dependencias de producción (sin las de dev)
RUN poetry install --without dev --no-root

# Verificamos que Django se instaló correctamente
RUN /app/.venv/bin/python -c "import django; print(f'Django {django.VERSION} installed')"

# --- Stage 2: Runtime ---
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src"

# Instalamos librerías necesarias para que funcione Postgres (libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Creamos un usuario no-root por seguridad
RUN useradd -m appuser

WORKDIR /app

# IMPORTANTE: Primero copiamos el código fuente (esto puede traer .venv vacio si existe)
COPY --chown=appuser:appuser . .

# Luego copiamos el venv del builder (sobrescribe cualquier .venv local)
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

USER appuser

# Exponemos el puerto de Django
EXPOSE 8000

# Comando para correr la aplicación
CMD ["/app/.venv/bin/python", "manage.py", "runserver", "0.0.0.0:8000"]