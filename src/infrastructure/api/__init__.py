"""
Infrastructure API Package.

Expone los endpoints REST del servicio de análisis de video mediante
Django REST Framework con soporte asíncrono (django-adrf).

Modules:
    views: Controladores HTTP asíncronos (APIView).
    serializers: DTOs de entrada/salida y validación de datos.
    urls: Configuración de rutas del módulo.

Endpoint principal:
    POST /api/v1/videos/analyze/ — Dispara el análisis completo de un video.
"""
