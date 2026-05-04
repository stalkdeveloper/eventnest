def global_context(request):
    from apps.categories.models import Category
    return {
        'nav_categories': Category.objects.filter(parent=None).order_by('title')[:8],
        'user_role': (
            request.user.role
            if request.user.is_authenticated and hasattr(request.user, 'role')
            else 'Guest'
        ),
    }
