"""
Application Layer Package.

Contiene la lógica de aplicación siguiendo Clean Architecture:
    - use_cases/: Casos de uso que orquestan el flujo de negocio
    - workflow/: Grafo de agentes LangGraph para procesamiento de videos

Esta capa actúa como intermediaria entre la infraestructura (API, DB)
y el dominio (modelos de negocio), manteniendo la separación de responsabilidades.
"""
