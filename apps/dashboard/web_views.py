"""Guest and Organiser dashboards (public website side) — optimized."""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from apps.events.models import Event
from apps.tickets.models import Ticket


@login_required
def dashboard(request):
    user = request.user
    if user.is_system_user:
        return redirect('admin_dashboard:dashboard')
    if user.groups.filter(name='Organiser').exists():
        return redirect('web_events:organiser_events')

    # Guest dashboard — single optimized queryset per concern
    tickets = (
        Ticket.objects
        .filter(attendee=user)
        .select_related('event', 'event__category')
        .order_by('-created_at')[:5]
    )
    upcoming = (
        Event.objects
        .filter(status='published', start_date__gte=timezone.now())
        .select_related('category')
        .prefetch_related('tags')
        .order_by('start_date')[:4]
    )
    return render(request, 'dashboard/web/guest.html', {
        'tickets':         tickets,
        'upcoming_events': upcoming,
    })
