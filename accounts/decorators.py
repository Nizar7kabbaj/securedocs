from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def admin_required(view_func):

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        if not request.user.is_staff:
            messages.error(request, "Accès réservé aux administrateurs.")
            return redirect("home")
        return view_func(request, *args, **kwargs)

    return _wrapped