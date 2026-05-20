from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from accounts.decorators import admin_required
from audit.models import AuditLog
from documents.models import Document

User = get_user_model()


@login_required
@admin_required
def dashboard_view(request):
    last_24h = timezone.now() - timedelta(hours=24)

    docs_per_class = dict(
        Document.objects
        .values_list("classification")
        .annotate(n=Count("id"))
        .values_list("classification", "n")
    )

    stats = {
        "total_documents": Document.objects.count(),
        "total_users": User.objects.count(),
        "total_audit_events": AuditLog.objects.count(),
        "failed_logins_24h": AuditLog.objects.filter(
            action=AuditLog.ACTION_LOGIN_FAILED,
            timestamp__gte=last_24h,
        ).count(),
        "docs_invoice": docs_per_class.get("invoice", 0),
        "docs_id": docs_per_class.get("id", 0),
        "docs_contract": docs_per_class.get("contract", 0),
        "docs_other": docs_per_class.get("other", 0),
        "docs_unclassified": docs_per_class.get("", 0) + docs_per_class.get(None, 0),
    }

    recent_events = (
        AuditLog.objects
        .select_related("user")
        .order_by("-timestamp")[:20]
    )

    users = (
        User.objects
        .annotate(doc_count=Count("documents"))
        .order_by("-is_staff", "username")
    )

    context = {
        "stats": stats,
        "recent_events": recent_events,
        "users": users,
    }
    return render(request, "dashboard/index.html", context)