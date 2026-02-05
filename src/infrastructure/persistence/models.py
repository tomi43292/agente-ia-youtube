"""
Módulo de Infraestructura: Implementación de la persistencia mediante Django ORM.
Define cómo se mapean los resultados del análisis a la base de datos PostgreSQL.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class VideoRecord(models.Model):
    """
    Modelo de Django para la persistencia de análisis de video.
    Incluye optimizaciones de índices y validaciones de rango.
    """
    # Identificación y Metadata [cite: 18-20, 30]
    # url con índice y unicidad para evitar duplicados y acelerar búsquedas
    url = models.URLField(
        max_length=500, 
        unique=True, 
        db_index=True, 
        help_text="URL única de origen del video"
    )
    title = models.CharField(max_length=255)
    transcript = models.TextField(help_text="Transcripción completa extraída")
    duration_seconds = models.PositiveIntegerField()
    language_code = models.CharField(max_length=10)

    # Resultados del Análisis [cite: 26-29, 30]
    sentiment = models.CharField(max_length=20)
    # sentiment_score con validadores de rango (0.0 a 1.0)
    sentiment_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    tone = models.CharField(max_length=100)
    key_points = models.JSONField(help_text="Lista de los 3 puntos clave en formato JSON")

    # Auditoría con índice para reportes cronológicos
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Registro de Video"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.sentiment}"