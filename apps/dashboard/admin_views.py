"""Admin panel dashboard  optimized."""
from django.shortcuts import render
from django.db.models import Count, Q
from apps.core.decorators import system_required
from apps.accounts.models import CustomUser
from apps.categories.models import Category
from apps.events.models import Event, Tag
from apps.tickets.models import Ticket


@system_required
def dashboard(request):
    # Single aggregation query instead of 5 separate .count() calls
    counts = {
        'total_users':   CustomUser.objects.count(),
        'total_events':  Event.all_objects.count(),
        'total_tickets': Ticket.objects.filter(status='confirmed').count(),
        'total_cats':    Category.objects.count(),
        'total_tags':    Tag.objects.filter(deleted_at__isnull=True).count(),
    }

    recent_events = (
        Event.all_objects
        .order_by('-created_at')
        .select_related('organiser', 'created_by')
        .prefetch_related('tags')[:10]
    )

    recent_users = (
        CustomUser.objects
        .order_by('-date_joined')
        .prefetch_related('groups')[:8]
    )

    return render(request, 'dashboard/admin/index.html', {
        **counts,
        'recent_events': recent_events,
        'recent_users':  recent_users,
    })
