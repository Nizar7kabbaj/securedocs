from django.conf import settings
from django.db import models


class Document(models.Model):
    CLASSIFICATION_CHOICES = [
        ("invoice", "Facture"),
        ("id", "Pièce d'identité"),
        ("contract", "Contrat"),
        ("other", "Autre"),
        ("unclassified", "Non classé"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    file = models.FileField(upload_to="documents/%Y/%m/")
    original_name = models.CharField(max_length=255)
    classification = models.CharField(
        max_length=20,
        choices=CLASSIFICATION_CHOICES,
        default="unclassified",
    )
    confidence = models.FloatField(null=True, blank=True)
    extracted_text = models.TextField(blank=True, default="")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.original_name} ({self.get_classification_display()})"