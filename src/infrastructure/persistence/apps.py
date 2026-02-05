"""
Configuración de la aplicación Django para el módulo de persistencia.
"""
from django.apps import AppConfig


class PersistenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'infrastructure.persistence'
    verbose_name = 'Persistencia de Videos'
