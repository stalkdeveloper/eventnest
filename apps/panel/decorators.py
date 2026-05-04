from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def system_required(view_func):
    """Only system users (admin / sub-admin) may access."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_system_user:
            messages.error(request, 'Access denied. System users only.')
            return redirect('core:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def superadmin_required(view_func):
    """Only superusers may access (create sub-admins, delete users, etc.)."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_superuser:
            messages.error(request, 'Access denied. Superadmin only.')
            return redirect('panel:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
