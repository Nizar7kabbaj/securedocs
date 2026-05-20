import io
import json
import os
import zipfile
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render

from audit.models import AuditLog
from audit.services import log_action
from documents.models import Document


@login_required
def account(request):
    return render(request, "gdpr/account.html")


@login_required
def export_my_data(request):
    user = request.user
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"securedocs_export_{user.username}_{timestamp}.zip"

    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "date_joined": user.date_joined.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }

    documents = Document.objects.filter(owner=user)
    documents_data = [
        {
            "id": doc.id,
            "original_name": doc.original_name,
            "classification": doc.classification,
            "confidence": doc.confidence,
            "uploaded_at": doc.uploaded_at.isoformat(),
            "file_path_in_zip": f"files/{doc.original_name}",
        }
        for doc in documents
    ]

    audit_logs = AuditLog.objects.filter(user=user)
    audit_data = [
        {
            "action": log.action,
            "action_display": log.get_action_display(),
            "target_repr": log.target_repr,
            "ip_address": log.ip_address,
            "timestamp": log.timestamp.isoformat(),
        }
        for log in audit_logs
    ]

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("user.json", json.dumps(user_data, indent=2, ensure_ascii=False))
        zf.writestr("documents.json", json.dumps(documents_data, indent=2, ensure_ascii=False))
        zf.writestr("audit_log.json", json.dumps(audit_data, indent=2, ensure_ascii=False))

        for doc in documents:
            if doc.file and os.path.exists(doc.file.path):
                zf.write(doc.file.path, arcname=f"files/{doc.original_name}")

    log_action(
        request,
        AuditLog.ACTION_EXPORT,
        target=f"User #{user.id} — {user.username}",
    )

    response = HttpResponse(buffer.getvalue(), content_type="application/zip")
    response["Content-Disposition"] = f'attachment; filename="{zip_filename}"'
    return response


@login_required
def delete_my_data(request):
    if request.method == "POST":
        password = request.POST.get("password", "")

        if not request.user.check_password(password):
            messages.error(request, "Mot de passe incorrect. Suppression annulée.")
            return render(request, "gdpr/delete.html")

        user = request.user
        user_id = user.id
        username = user.username

        for doc in Document.objects.filter(owner=user):
            if doc.file and os.path.exists(doc.file.path):
                try:
                    os.remove(doc.file.path)
                except OSError:
                    pass

        log_action(
            request,
            AuditLog.ACTION_DELETE_ACCOUNT,
            target=f"User #{user_id} — {username}",
        )

        logout(request)
        user.delete()

        messages.success(
            request,
            f"Le compte « {username} » a été définitivement supprimé. "
            "Toutes vos données ont été effacées.",
        )
        return redirect("home")

    return render(request, "gdpr/delete.html")