from .models import Category


def global_context(request):
    """Inject categories and user role into every template context."""
    return {
        'nav_categories': Category.objects.order_by('name')[:8],
        'user_role': request.user.role if request.user.is_authenticated and hasattr(request.user, 'role') else 'Guest',
    }
