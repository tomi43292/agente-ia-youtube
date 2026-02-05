"""
Módulo de Infraestructura: Implementación de la persistencia mediante Django ORM.
Define cómo se mapean los resultados del análisis a la base de datos PostgreSQL.
"""
from django.db import models

class VideoRecord(models.Model):
    """
    Modelo de Django para la persistencia de análisis de video[cite: 30, 44].
    Se utiliza JSONField para los key_points para aprovechar la flexibilidad de Postgres.
    """
    # Identificación y Metadata [cite: 18-20]
    url = models.URLField(max_length=500, help_text="URL de origen del video analizado")
    title = models.CharField(max_length=255)
    transcript = models.TextField(help_text="Transcripción completa extraída")
    duration_seconds = models.PositiveIntegerField()
    language_code = models.CharField(max_length=10)

    # Resultados del Análisis [cite: 26-29]
    sentiment = models.CharField(max_length=20)
    sentiment_score = models.FloatField()
    tone = models.CharField(max_length=100)
    key_points = models.JSONField(help_text="Lista de los 3 puntos clave en formato JSON")

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Registro de Video"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.sentiment}"