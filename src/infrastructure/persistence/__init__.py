"""
Persistence Package — Capa de persistencia con Django ORM.

Implementa el almacenamiento de resultados de análisis de video en
PostgreSQL (producción) o SQLite (testing).

Modules:
    models: Modelo VideoRecord con validaciones y índices optimizados.
    apps: Configuración de la aplicación Django (PersistenceConfig).
    migrations/: Migraciones autogeneradas por Django.

Exports:
    VideoRecord: Modelo principal de persistencia (via models.py).
"""
default_app_config = 'infrastructure.persistence.apps.PersistenceConfig'
