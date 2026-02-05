"""
Suite de Tests de Integración para la API de Análisis de Video.
Se utiliza Mocking para aislar la lógica de negocio de los servicios externos (Gemini/YouTube).
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
@pytest.mark.asyncio
class TestVideoAnalysisAPI:
    """
    Pruebas de comportamiento para el endpoint de análisis.
    """

    def setup_method(self):
        self.url = reverse('video-analyze')

    @patch('application.use_cases.use_cases.AnalyzeVideoUseCase.execute')
    async def test_successful_video_analysis(self, mock_execute, async_client):
        """
        Caso feliz: Se envía una URL válida y se recibe el análisis completo.
        Verifica el cumplimiento del esquema JSON requerido.
        """
        # Configuramos el Mock para simular una respuesta exitosa
        mock_record = MagicMock()
        mock_record.id = 1
        mock_record.url = "https://youtube.com/watch?v=test123"
        mock_record.title = "Video Test"
        mock_record.transcript = "Transcripción de prueba"
        mock_record.duration_seconds = 180
        mock_record.language_code = "es"
        mock_record.sentiment = "positivo"
        mock_record.sentiment_score = 0.95
        mock_record.tone = "educativo"
        mock_record.key_points = ["Punto A", "Punto B", "Punto C"]
        mock_record.created_at = "2026-02-05T12:00:00Z"
        
        mock_execute.return_value = mock_record

        payload = {"video_url": "https://www.youtube.com/watch?v=12345678901"}
        response = await async_client.post(self.url, data=payload, content_type='application/json')

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['sentiment'] == 'positivo'
        assert len(data['key_points']) == 3
        assert data['sentiment_score'] == 0.95
        assert data['tone'] == 'educativo'

    async def test_invalid_url_format(self, async_client):
        """
        Caso de error: Se envía una URL malformada.
        Verifica que el manejo de errores del Serializer funcione correctamente.
        """
        payload = {"video_url": "esto-no-es-una-url"}
        response = await async_client.post(self.url, data=payload, content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert 'video_url' in data

    async def test_missing_video_url_field(self, async_client):
        """
        Caso de error: Falta el campo video_url.
        """
        payload = {}
        response = await async_client.post(self.url, data=payload, content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert 'video_url' in data

    async def test_empty_video_url(self, async_client):
        """
        Caso de error: video_url está vacío.
        """
        payload = {"video_url": ""}
        response = await async_client.post(self.url, data=payload, content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('application.use_cases.use_cases.AnalyzeVideoUseCase.execute')
    async def test_workflow_error_returns_500(self, mock_execute, async_client):
        """
        Caso de error: Falla el workflow de LangGraph.
        Verifica que errores internos se manejen correctamente.
        """
        mock_execute.side_effect = ValueError("Error en el workflow: Video no encontrado")

        payload = {"video_url": "https://www.youtube.com/watch?v=invalidvid"}
        response = await async_client.post(self.url, data=payload, content_type='application/json')

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert 'error' in data

    @patch('application.use_cases.use_cases.AnalyzeVideoUseCase.execute')
    async def test_no_transcript_error(self, mock_execute, async_client):
        """
        Caso de error específico: Video sin audio/transcripción.
        """
        mock_execute.side_effect = ValueError(
            "Error en el workflow: El video no posee transcripciones"
        )

        payload = {"video_url": "https://www.youtube.com/watch?v=noaudiotest"}
        response = await async_client.post(self.url, data=payload, content_type='application/json')

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert 'transcripciones' in data.get('error', '').lower() or 'error' in data

    @patch('application.use_cases.use_cases.AnalyzeVideoUseCase.execute')
    async def test_llm_api_error(self, mock_execute, async_client):
        """
        Caso de error: Falla la API del LLM (Gemini).
        """
        mock_execute.side_effect = ValueError(
            "Error en el workflow: Error en análisis de IA: API rate limit"
        )

        payload = {"video_url": "https://www.youtube.com/watch?v=validvideo"}
        response = await async_client.post(self.url, data=payload, content_type='application/json')

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @patch('application.use_cases.use_cases.AnalyzeVideoUseCase.execute')
    async def test_response_contains_all_required_fields(self, mock_execute, async_client):
        """
        Verifica que la respuesta contenga todos los campos requeridos por el challenge.
        """
        mock_record = MagicMock()
        mock_record.id = 1
        mock_record.url = "https://youtube.com/watch?v=test"
        mock_record.title = "Test Video"
        mock_record.transcript = "Test transcript"
        mock_record.duration_seconds = 300
        mock_record.language_code = "es"
        mock_record.sentiment = "neutral"
        mock_record.sentiment_score = 0.5
        mock_record.tone = "formal"
        mock_record.key_points = ["P1", "P2", "P3"]
        mock_record.created_at = "2026-02-05T12:00:00Z"
        
        mock_execute.return_value = mock_record

        payload = {"video_url": "https://www.youtube.com/watch?v=testvideo11"}
        response = await async_client.post(self.url, data=payload, content_type='application/json')

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Verificar campos de metadata
        assert 'title' in data
        assert 'duration_seconds' in data
        assert 'language_code' in data
        
        # Verificar campos de análisis
        assert 'sentiment' in data
        assert 'sentiment_score' in data
        assert 'tone' in data
        assert 'key_points' in data
        
        # Verificar persistencia
        assert 'url' in data
        assert 'transcript' in data

    @patch('application.use_cases.use_cases.AnalyzeVideoUseCase.execute')
    async def test_sentiment_score_is_float_in_range(self, mock_execute, async_client):
        """
        Verifica que sentiment_score sea un float entre 0.0 y 1.0.
        """
        mock_record = MagicMock()
        mock_record.id = 1
        mock_record.url = "https://youtube.com/watch?v=test"
        mock_record.title = "Test"
        mock_record.transcript = "Test"
        mock_record.duration_seconds = 100
        mock_record.language_code = "es"
        mock_record.sentiment = "positivo"
        mock_record.sentiment_score = 0.87
        mock_record.tone = "casual"
        mock_record.key_points = ["A", "B", "C"]
        mock_record.created_at = "2026-02-05T12:00:00Z"
        
        mock_execute.return_value = mock_record

        payload = {"video_url": "https://www.youtube.com/watch?v=scoretest1"}
        response = await async_client.post(self.url, data=payload, content_type='application/json')

        data = response.json()
        score = data['sentiment_score']
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0