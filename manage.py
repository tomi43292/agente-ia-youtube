#!/usr/bin/env python
"""
Punto de entrada CLI de Django para agente-ia-youtube.

Utilidad de línea de comandos para tareas administrativas del proyecto:
    - Migraciones: python manage.py migrate
    - Servidor de desarrollo: python manage.py runserver
    - Shell interactivo: python manage.py shell
    - Crear superusuario: python manage.py createsuperuser

Note:
    Requiere PYTHONPATH=src o ejecutar desde la carpeta raíz del proyecto.
    En Docker, el PYTHONPATH se configura automáticamente en el Dockerfile.
"""
import os
import sys


def main():
    """Configura DJANGO_SETTINGS_MODULE y delega la ejecución al CLI de Django."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
