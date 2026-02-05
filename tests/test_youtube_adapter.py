"""
Tests Unitarios para el Adaptador de YouTube.
Utiliza mocking para aislar las pruebas de la API externa.
"""
import pytest
from unittest.mock import patch, MagicMock
from infrastructure.adapters.youtube_adapter import YouTubeAdapter
from infrastructure.adapters.exceptions import (
    VideoNotFoundError, 
    NoTranscriptError, 
    YouTubeError
)
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import VideoUnavailable, TranscriptsDisabled, NoTranscriptFound


class TestYouTubeAdapterVideoIdExtraction:
    """Tests para la extracción de IDs de video."""

    def setup_method(self):
        self.adapter = YouTubeAdapter()

    def test_extract_id_from_standard_url(self):
        """Extrae ID de URL estándar de YouTube."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = self.adapter._extract_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_id_from_short_url(self):
        """Extrae ID de URL corta youtu.be."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = self.adapter._extract_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_id_with_extra_params(self):
        """Extrae ID cuando hay parámetros adicionales."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120"
        video_id = self.adapter._extract_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_id_limits_to_11_chars(self):
        """Verifica que solo tome 11 caracteres del ID."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQextratext"
        video_id = self.adapter._extract_id(url)
        assert len(video_id) == 11


class TestYouTubeAdapterTranscriptFetching:
    """Tests para la obtención de transcripciones."""

    def setup_method(self):
        self.adapter = YouTubeAdapter()

    @patch.object(YouTubeTranscriptApi, 'fetch')
    def test_get_transcript_success(self, mock_fetch):
        """Test de transcripción exitosa."""
        # Crear objetos mock que simulen los transcript entries
        mock_entry1 = MagicMock()
        mock_entry1.text = "Hola mundo"
        mock_entry2 = MagicMock()
        mock_entry2.text = "Este es un video"
        mock_fetch.return_value = [mock_entry1, mock_entry2]
        
        result = self.adapter._get_transcript("test_video_id")
        
        assert "Hola mundo" in result
        assert "Este es un video" in result
        mock_fetch.assert_called_once_with(
            "test_video_id", 
            languages=['es', 'en']
        )

    @patch.object(YouTubeTranscriptApi, 'fetch')
    def test_get_transcript_spanish_preference(self, mock_fetch):
        """Verifica que se priorice español sobre inglés."""
        mock_entry = MagicMock()
        mock_entry.text = "Texto"
        mock_fetch.return_value = [mock_entry]
        
        self.adapter._get_transcript("video_id")
        
        call_args = mock_fetch.call_args
        languages = call_args[1]['languages']
        assert languages[0] == 'es'  # Español debe ser primero


@pytest.mark.asyncio
class TestYouTubeAdapterAsync:
    """Tests asíncronos para fetch_full_data."""

    def setup_method(self):
        self.adapter = YouTubeAdapter()

    @patch('infrastructure.adapters.youtube_adapter.YouTubeAdapter._get_transcript')
    async def test_fetch_full_data_success(self, mock_get_transcript):
        """Test de obtención completa de datos."""
        mock_get_transcript.return_value = "Transcripción de prueba"
        
        result = await self.adapter.fetch_full_data(
            "https://www.youtube.com/watch?v=test12345"
        )
        
        assert "transcript" in result
        assert "metadata" in result
        assert result["transcript"] == "Transcripción de prueba"
        assert "title" in result["metadata"]
        assert "duration_seconds" in result["metadata"]
        assert "language_code" in result["metadata"]

    @patch('infrastructure.adapters.youtube_adapter.YouTubeAdapter._get_transcript')
    async def test_fetch_video_unavailable_raises_error(self, mock_get_transcript):
        """Test de error cuando el video no está disponible."""
        mock_get_transcript.side_effect = VideoUnavailable("video_id")
        
        with pytest.raises(VideoNotFoundError) as exc_info:
            await self.adapter.fetch_full_data(
                "https://www.youtube.com/watch?v=notexist"
            )
        
        assert "no está disponible" in str(exc_info.value)

    @patch('infrastructure.adapters.youtube_adapter.YouTubeAdapter._get_transcript')
    async def test_fetch_no_transcript_raises_error(self, mock_get_transcript):
        """Test de error cuando no hay transcripción."""
        mock_get_transcript.side_effect = TranscriptsDisabled("video_id")
        
        with pytest.raises(NoTranscriptError) as exc_info:
            await self.adapter.fetch_full_data(
                "https://www.youtube.com/watch?v=nosubtitles"
            )
        
        assert "no posee transcripciones" in str(exc_info.value)

    @patch('infrastructure.adapters.youtube_adapter.YouTubeAdapter._get_transcript')
    async def test_fetch_no_transcript_found_raises_error(self, mock_get_transcript):
        """Test de error cuando no se encuentra transcripción."""
        mock_get_transcript.side_effect = NoTranscriptFound(
            "video_id", 
            ["en"], 
            None
        )
        
        with pytest.raises(NoTranscriptError):
            await self.adapter.fetch_full_data(
                "https://www.youtube.com/watch?v=notranscript"
            )

    @patch('infrastructure.adapters.youtube_adapter.YouTubeAdapter._get_transcript')
    async def test_fetch_generic_error_raises_youtube_error(self, mock_get_transcript):
        """Test de error genérico se encapsula correctamente."""
        mock_get_transcript.side_effect = Exception("Error de red inesperado")
        
        with pytest.raises(YouTubeError) as exc_info:
            await self.adapter.fetch_full_data(
                "https://www.youtube.com/watch?v=somevideooo"
            )
        
        assert "Error inesperado" in str(exc_info.value)
