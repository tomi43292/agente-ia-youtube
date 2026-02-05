"""
Source Root Package — agente-ia-youtube.

Paquete raíz que agrupa las tres capas de Clean Architecture:

    - domain/: Modelos Pydantic y reglas de negocio (capa más interna).
    - application/: Casos de uso y orquestación del workflow LangGraph.
    - infrastructure/: Adaptadores externos (YouTube, LLM), API REST y persistencia Django.
    - config/: Configuración del proyecto Django (settings, urls, asgi/wsgi).

La separación en capas garantiza que el dominio permanezca independiente
de frameworks y servicios externos, facilitando testing y mantenibilidad.
"""
