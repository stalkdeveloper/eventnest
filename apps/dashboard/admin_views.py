"""Admin panel dashboard."""
from django.shortcuts import render
from apps.core.decorators import system_required
from apps.accounts.models import CustomUser
from apps.categories.models import Category
from apps.events.models import Event
from apps.tickets.models import Ticket


@system_required
def dashboard(request):
    return render(request, 'dashboard/admin/index.html', {
        'total_users':   CustomUser.objects.count(),
        'total_events':  Event.all_objects.count(),
        'total_tickets': Ticket.objects.filter(status='confirmed').count(),
        'total_cats':    Category.objects.count(),
        'recent_events': Event.all_objects.order_by('-created_at')
                             .select_related('organiser', 'created_by')[:10],
        'recent_users':  CustomUser.objects.order_by('-date_joined')[:8],
    })
