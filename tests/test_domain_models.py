"""
Tests Unitarios para los Modelos de Dominio.
Valida que los esquemas Pydantic cumplan con las restricciones del challenge.
"""
import pytest
from pydantic import ValidationError
from domain.models import VideoAnalysis, VideoMetadata


class TestVideoAnalysis:
    """Tests para el modelo VideoAnalysis."""

    def test_valid_analysis_creation(self):
        """Verifica que se pueda crear un análisis válido."""
        analysis = VideoAnalysis(
            sentiment="positivo",
            sentiment_score=0.85,
            tone="informal",
            key_points=["Punto 1", "Punto 2", "Punto 3"]
        )
        
        assert analysis.sentiment == "positivo"
        assert analysis.sentiment_score == 0.85
        assert analysis.tone == "informal"
        assert len(analysis.key_points) == 3

    def test_sentiment_score_must_be_in_range(self):
        """Verifica que sentiment_score esté en rango [0.0, 1.0]."""
        # Score negativo debe fallar
        with pytest.raises(ValidationError):
            VideoAnalysis(
                sentiment="positivo",
                sentiment_score=-0.1,
                tone="formal",
                key_points=["P1", "P2", "P3"]
            )
        
        # Score mayor a 1 debe fallar
        with pytest.raises(ValidationError):
            VideoAnalysis(
                sentiment="positivo",
                sentiment_score=1.5,
                tone="formal",
                key_points=["P1", "P2", "P3"]
            )

    def test_key_points_must_have_exactly_three(self):
        """Verifica que key_points tenga exactamente 3 elementos."""
        # Menos de 3 puntos debe fallar
        with pytest.raises(ValidationError):
            VideoAnalysis(
                sentiment="neutral",
                sentiment_score=0.5,
                tone="técnico",
                key_points=["Punto 1", "Punto 2"]
            )
        
        # Más de 3 puntos debe fallar
        with pytest.raises(ValidationError):
            VideoAnalysis(
                sentiment="neutral",
                sentiment_score=0.5,
                tone="técnico",
                key_points=["P1", "P2", "P3", "P4"]
            )

    def test_required_fields_validation(self):
        """Verifica que todos los campos requeridos se validen."""
        with pytest.raises(ValidationError):
            VideoAnalysis(
                sentiment="positivo",
                # Falta sentiment_score
                tone="informal",
                key_points=["P1", "P2", "P3"]
            )

    def test_sentiment_enum_values(self):
        """Verifica los valores permitidos de sentiment."""
        for sentiment in ["positivo", "negativo", "neutral"]:
            analysis = VideoAnalysis(
                sentiment=sentiment,
                sentiment_score=0.5,
                tone="formal",
                key_points=["A", "B", "C"]
            )
            assert analysis.sentiment == sentiment


class TestVideoMetadata:
    """Tests para el modelo VideoMetadata."""

    def test_valid_metadata_creation(self):
        """Verifica que se pueda crear metadata válida."""
        metadata = VideoMetadata(
            title="Video de Prueba",
            duration_seconds=300,
            language_code="es"
        )
        
        assert metadata.title == "Video de Prueba"
        assert metadata.duration_seconds == 300
        assert metadata.language_code == "es"

    def test_metadata_with_different_languages(self):
        """Verifica diferentes códigos de idioma ISO 639-1."""
        for lang_code in ["es", "en", "pt", "fr"]:
            metadata = VideoMetadata(
                title="Test Video",
                duration_seconds=100,
                language_code=lang_code
            )
            assert metadata.language_code == lang_code

    def test_duration_is_integer(self):
        """Verifica que duration_seconds sea entero."""
        metadata = VideoMetadata(
            title="Test",
            duration_seconds=180,
            language_code="en"
        )
        assert isinstance(metadata.duration_seconds, int)

    def test_required_fields_validation(self):
        """Verifica que todos los campos requeridos existan."""
        with pytest.raises(ValidationError):
            VideoMetadata(
                title="Test",
                # Falta duration_seconds
                language_code="es"
            )
