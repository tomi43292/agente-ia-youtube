"""
Tests Unitarios para los Nodos del Grafo de LangGraph.
Aísla cada nodo para verificar su comportamiento individual.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from application.workflow.graph import (
    extraction_node, 
    analysis_node, 
    should_continue,
    GraphState
)
from infrastructure.adapters.exceptions import VideoNotFoundError, NoTranscriptError


class TestExtractionNode:
    """Tests para el nodo de extracción."""

    @pytest.mark.asyncio
    @patch('application.workflow.graph.yt_adapter')
    async def test_extraction_success(self, mock_adapter):
        """Test de extracción exitosa."""
        mock_adapter.fetch_full_data = AsyncMock(return_value={
            "transcript": "Transcripción de prueba",
            "metadata": {
                "title": "Video Test",
                "duration_seconds": 180,
                "language_code": "es"
            }
        })
        
        initial_state: GraphState = {
            "video_url": "https://youtube.com/watch?v=test1234",
            "transcript": "",
            "metadata": {},
            "analysis": {},
            "errors": []
        }
        
        result = await extraction_node(initial_state)
        
        assert result["transcript"] == "Transcripción de prueba"
        assert result["metadata"]["title"] == "Video Test"
        assert result["errors"] == []

    @pytest.mark.asyncio
    @patch('application.workflow.graph.yt_adapter')
    async def test_extraction_video_not_found(self, mock_adapter):
        """Test de error cuando video no existe."""
        mock_adapter.fetch_full_data = AsyncMock(
            side_effect=VideoNotFoundError("Video no encontrado")
        )
        
        initial_state: GraphState = {
            "video_url": "https://youtube.com/watch?v=invalid",
            "transcript": "",
            "metadata": {},
            "analysis": {},
            "errors": []
        }
        
        result = await extraction_node(initial_state)
        
        assert len(result["errors"]) == 1
        assert "Video no encontrado" in result["errors"][0]

    @pytest.mark.asyncio
    @patch('application.workflow.graph.yt_adapter')
    async def test_extraction_no_transcript(self, mock_adapter):
        """Test de error cuando no hay transcripción."""
        mock_adapter.fetch_full_data = AsyncMock(
            side_effect=NoTranscriptError("Sin transcripción disponible")
        )
        
        initial_state: GraphState = {
            "video_url": "https://youtube.com/watch?v=noaudio",
            "transcript": "",
            "metadata": {},
            "analysis": {},
            "errors": []
        }
        
        result = await extraction_node(initial_state)
        
        assert len(result["errors"]) == 1
        assert "Sin transcripción" in result["errors"][0]


class TestAnalysisNode:
    """Tests para el nodo de análisis de IA."""

    @pytest.mark.asyncio
    @patch('application.workflow.graph.structured_llm')
    async def test_analysis_success(self, mock_llm):
        """Test de análisis exitoso."""
        mock_result = MagicMock()
        mock_result.dict.return_value = {
            "sentiment": "positivo",
            "sentiment_score": 0.9,
            "tone": "educativo",
            "key_points": ["Punto A", "Punto B", "Punto C"]
        }
        mock_llm.ainvoke = AsyncMock(return_value=mock_result)
        
        state: GraphState = {
            "video_url": "https://youtube.com/watch?v=test",
            "transcript": "Esta es una transcripción de prueba muy positiva.",
            "metadata": {"title": "Test", "duration_seconds": 100, "language_code": "es"},
            "analysis": {},
            "errors": []
        }
        
        result = await analysis_node(state)
        
        assert result["analysis"]["sentiment"] == "positivo"
        assert result["analysis"]["sentiment_score"] == 0.9
        assert len(result["analysis"]["key_points"]) == 3

    @pytest.mark.asyncio
    async def test_analysis_skips_on_error_state(self):
        """Test que el nodo de análisis se salta si hay errores previos."""
        state: GraphState = {
            "video_url": "https://youtube.com/watch?v=test",
            "transcript": "",
            "metadata": {},
            "analysis": {},
            "errors": ["Error previo en extracción"]
        }
        
        result = await analysis_node(state)
        
        # Debe devolver el mismo estado sin modificar
        assert result == state
        assert "analysis" not in result or result["analysis"] == {}

    @pytest.mark.asyncio
    @patch('application.workflow.graph.structured_llm')
    async def test_analysis_llm_failure(self, mock_llm):
        """Test de error cuando falla el LLM."""
        mock_llm.ainvoke = AsyncMock(
            side_effect=Exception("API rate limit exceeded")
        )
        
        state: GraphState = {
            "video_url": "https://youtube.com/watch?v=test",
            "transcript": "Transcripción de prueba",
            "metadata": {"title": "Test", "duration_seconds": 100, "language_code": "es"},
            "analysis": {},
            "errors": []
        }
        
        result = await analysis_node(state)
        
        assert len(result["errors"]) == 1
        assert "Error en análisis de IA" in result["errors"][0]


class TestShouldContinue:
    """Tests para la función de routing condicional."""

    def test_should_continue_returns_continue_on_no_errors(self):
        """Test que continúa cuando no hay errores."""
        state: GraphState = {
            "video_url": "test",
            "transcript": "test",
            "metadata": {},
            "analysis": {},
            "errors": []
        }
        
        result = should_continue(state)
        
        assert result == "continue"

    def test_should_continue_returns_end_on_errors(self):
        """Test que termina cuando hay errores."""
        state: GraphState = {
            "video_url": "test",
            "transcript": "",
            "metadata": {},
            "analysis": {},
            "errors": ["Hubo un error"]
        }
        
        result = should_continue(state)
        
        assert result == "end"

    def test_should_continue_returns_end_on_multiple_errors(self):
        """Test que termina cuando hay múltiples errores."""
        state: GraphState = {
            "video_url": "test",
            "transcript": "",
            "metadata": {},
            "analysis": {},
            "errors": ["Error 1", "Error 2"]
        }
        
        result = should_continue(state)
        
        assert result == "end"
