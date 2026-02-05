"""
Suite de Tests de Integración para la API de Análisis de Video.
Se utiliza Mocking para aislar la lógica de negocio de los servicios externos (Gemini/YouTube).
"""
import pytest
from unittest.mock import patch, AsyncMock
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
        Verifica el cumplimiento del esquema JSON requerido [cite: 14, 24-29].
        """
        # Configuramos el Mock para simular una respuesta exitosa del grafo
        mock_execute.return_value = AsyncMock(
            url="https://youtube.com/watch?v=123",
            title="Video Test",
            sentiment="positivo",
            sentiment_score=0.95,
            key_points=["Punto A", "Punto B", "Punto C"]
        )

        payload = {"video_url": "https://www.youtube.com/watch?v=12345678901"}
        response = await async_client.post(self.url, data=payload, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['sentiment'] == 'positivo'
        assert len(response.data['key_points']) == 3

    async def test_invalid_url_error(self, async_client):
        """
        Caso de error: Se envía una URL malformada.
        Verifica que el manejo de errores del Serializer funcione correctamente.
        """
        payload = {"video_url": "esto-no-es-una-url"}
        response = await async_client.post(self.url, data=payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'video_url' in response.data