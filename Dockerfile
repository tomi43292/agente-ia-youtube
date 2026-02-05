# --- Stage 1: Builder ---
FROM python:3.12-slim AS builder

# Seteamos variables de entorno para Python y Poetry
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.8.2 \
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

# --- Stage 2: Runtime ---
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src"

# Instalamos librerías necesarias para que funcione Postgres (libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Creamos un usuario no-root por seguridad
RUN useradd -m appuser
USER appuser

WORKDIR /app

# Copiamos solo el entorno virtual y el código desde el builder
COPY --from=builder /app/.venv /app/.venv
COPY . .

# Exponemos el puerto de Django
EXPOSE 8000

# Comando para correr la aplicación con Uvicorn (ASGI)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]