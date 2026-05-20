from datetime import timedelta

from django.utils import timezone

from .models import AuditLog



LOCKOUT_THRESHOLD = 5 
LOCKOUT_WINDOW_MINUTES = 15   
LOCKOUT_DURATION_MINUTES = 15 


def log_action(request, action, target=None):
    user = request.user if request and request.user.is_authenticated else None
    ip = getattr(request, "audit_ip", None) if request else None

    if target is None:
        target_repr = ""
    elif isinstance(target, str):
        target_repr = target[:255]
    else:
        target_repr = _describe(target)

    AuditLog.objects.create(
        user=user,
        action=action,
        target_repr=target_repr,
        ip_address=ip,
    )


def is_username_locked(username):
    if not username:
        return False

    cutoff = timezone.now() - timedelta(minutes=LOCKOUT_DURATION_MINUTES)
    recent_failures = AuditLog.objects.filter(
        action=AuditLog.ACTION_LOGIN_FAILED,
        target_repr=username,
        timestamp__gte=cutoff,
    ).count()

    return recent_failures >= LOCKOUT_THRESHOLD


def _describe(obj):
    model_name = obj.__class__.__name__
    pk = getattr(obj, "pk", "?")
    label = (
        getattr(obj, "original_name", None)
        or getattr(obj, "name", None)
        or getattr(obj, "title", None)
        or str(obj)
    )
    return f"{model_name} #{pk} — {label}"[:255]