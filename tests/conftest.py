"""
Configuración de Pytest para el proyecto.
Define fixtures compartidos para tests asíncronos con Django.
"""
import os
import pytest
from django.test import AsyncClient

# Configurar Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')


@pytest.fixture
def async_client():
    """
    Fixture que provee un cliente async para tests de API.
    Compatible con pytest-asyncio y pytest-django.
    """
    return AsyncClient()


@pytest.fixture
def sample_video_url():
    """URL de ejemplo para tests."""
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@pytest.fixture
def mock_transcript():
    """Transcripción mockeada para tests unitarios."""
    return """
    Este es un video de ejemplo sobre tecnología.
    Hoy vamos a hablar de inteligencia artificial.
    La IA está transformando el mundo moderno.
    Punto uno: los modelos de lenguaje son revolucionarios.
    Punto dos: la automatización mejora la productividad.
    Punto tres: la ética en IA es fundamental.
    Gracias por ver este contenido educativo.
    """


@pytest.fixture
def mock_metadata():
    """Metadata mockeada para tests unitarios."""
    return {
        "title": "Video de Ejemplo sobre IA",
        "duration_seconds": 300,
        "language_code": "es"
    }


@pytest.fixture
def mock_analysis_result():
    """Resultado de análisis mockeado para tests."""
    return {
        "sentiment": "positivo",
        "sentiment_score": 0.85,
        "tone": "educativo",
        "key_points": [
            "Los modelos de lenguaje son revolucionarios",
            "La automatización mejora la productividad", 
            "La ética en IA es fundamental"
        ]
    }


@pytest.fixture
def mock_graph_final_state(mock_transcript, mock_metadata, mock_analysis_result):
    """Estado final del grafo mockeado para tests de integración."""
    return {
        "video_url": "https://www.youtube.com/watch?v=test123",
        "transcript": mock_transcript,
        "metadata": mock_metadata,
        "analysis": mock_analysis_result,
        "errors": []
    }
