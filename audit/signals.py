from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.dispatch import receiver

from .models import AuditLog


def _ip(request):
    """Read the IP that AuditContextMiddleware stashed on the request."""
    return getattr(request, "audit_ip", None) if request else None


@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action=AuditLog.ACTION_LOGIN,
        ip_address=_ip(request),
    )


@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action=AuditLog.ACTION_LOGOUT,
        ip_address=_ip(request),
    )


@receiver(user_login_failed)
def on_user_login_failed(sender, credentials, request, **kwargs):
    AuditLog.objects.create(
        user=None,
        action=AuditLog.ACTION_LOGIN_FAILED,
        target_repr=(credentials.get("username") or "")[:255],
        ip_address=_ip(request),
    )