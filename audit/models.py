from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    ACTION_LOGIN = "LOGIN"
    ACTION_LOGOUT = "LOGOUT"
    ACTION_LOGIN_FAILED = "LOGIN_FAILED"
    ACTION_LOGIN_BLOCKED = "LOGIN_BLOCKED"
    ACTION_UPLOAD = "UPLOAD"
    ACTION_DOWNLOAD = "DOWNLOAD"
    ACTION_DELETE = "DELETE"
    ACTION_EXPORT = "EXPORT"
    ACTION_DELETE_ACCOUNT = "DELETE_ACCOUNT"

    ACTION_CHOICES = [
        (ACTION_LOGIN, "Connexion"),
        (ACTION_LOGOUT, "Déconnexion"),
        (ACTION_LOGIN_FAILED, "Échec de connexion"),
        (ACTION_LOGIN_BLOCKED, "Connexion bloquée"),
        (ACTION_UPLOAD, "Téléversement"),
        (ACTION_DOWNLOAD, "Téléchargement"),
        (ACTION_DELETE, "Suppression"),
        (ACTION_EXPORT, "Export RGPD"),
        (ACTION_DELETE_ACCOUNT, "Suppression de compte"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target_repr = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["-timestamp"]),
            models.Index(fields=["user", "-timestamp"]),
            models.Index(fields=["action", "-timestamp"]),
        ]

    def __str__(self):
        who = self.user.username if self.user else "anonymous"
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {who} — {self.action}"