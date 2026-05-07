"""
Shared decorators used by all admin_views across apps.
Lives in core so any app can import without circular dependency.
"""
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
            messages.error(request, 'Access denied. Admin only.')
            return redirect('web_home:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def superadmin_required(view_func):
    """Only superusers may access."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_superuser:
            messages.error(request, 'Superadmin only.')
            return redirect('admin_dashboard:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
