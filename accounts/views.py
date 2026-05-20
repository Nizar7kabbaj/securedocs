from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import redirect, render

from audit.models import AuditLog
from audit.services import (
    LOCKOUT_DURATION_MINUTES,
    is_username_locked,
    log_action,
)

from .decorators import admin_required


def register_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
    else:
        form = UserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if username and is_username_locked(username):
            log_action(request, AuditLog.ACTION_LOGIN_BLOCKED, target=username)
            error = (
                f"Compte temporairement bloqué après plusieurs tentatives. "
                f"Réessayez dans {LOCKOUT_DURATION_MINUTES} minutes."
            )
            return render(request, "accounts/login.html", {"error": error})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            error = "Identifiants invalides."

    return render(request, "accounts/login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("accounts:login")


@admin_required
def admin_only(request):
    return HttpResponse("✅ Vous êtes administrateur. Accès autorisé.")