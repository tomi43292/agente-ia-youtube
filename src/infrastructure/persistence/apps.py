"""
Configuración de la aplicación Django para el módulo de persistencia.
"""
from django.apps import AppConfig


class PersistenceConfig(AppConfig):
    """
    Configuración de la app Django para el módulo de persistencia.

    Registra el módulo ``infrastructure.persistence`` como aplicación Django,
    habilitando migraciones automáticas y el admin para el modelo VideoRecord.

    Attributes:
        default_auto_field: Tipo de campo auto-incremental (BigAutoField).
        name: Ruta Python del módulo de persistencia.
        verbose_name: Nombre legible para el panel de administración.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'infrastructure.persistence'
    verbose_name = 'Persistencia de Videos'
