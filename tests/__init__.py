"""
Test Suite — agente-ia-youtube.

Contiene tests unitarios y de integración organizados por capa:

    - test_domain_models: Validación de esquemas Pydantic (VideoAnalysis, VideoMetadata).
    - test_graph_nodes: Tests aislados de cada nodo del grafo LangGraph.
    - test_youtube_adapter: Tests del adaptador de YouTube con mocking.
    - test_api: Tests de integración del endpoint REST.
    - conftest: Fixtures compartidos (async_client, mock data).

Ejecutar:
    poetry run pytest          # Todos los tests
    poetry run pytest -k api   # Solo tests de API
"""
