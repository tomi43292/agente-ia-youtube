"""
Config Package — Configuración central del proyecto Django.

Contiene los módulos estándar de configuración de Django:

    - settings: Variables de entorno, apps instaladas, DB, DRF, i18n.
    - urls: Enrutamiento principal (admin + API v1).
    - asgi: Punto de entrada ASGI para servidores async (Daphne, Uvicorn).
    - wsgi: Punto de entrada WSGI para servidores sync (Gunicorn).

Environment:
    DJANGO_SETTINGS_MODULE=config.settings
"""
