"""Guest and Organiser dashboards (public website side)."""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from apps.events.models import Event, Ticket


@login_required
def dashboard(request):
    """Route to correct dashboard by role."""
    user = request.user
    if user.is_system_user:
        return redirect('admin_dashboard:dashboard')
    if user.groups.filter(name='Organiser').exists():
        return redirect('web_events:organiser_events')
    # Guest dashboard
    tickets  = Ticket.objects.filter(attendee=user).select_related('event')[:5]
    upcoming = Event.objects.filter(
        status='published', start_date__gte=timezone.now()
    ).order_by('start_date')[:4]
    return render(request, 'dashboard/web/guest.html', {
        'tickets': tickets, 'upcoming_events': upcoming,
    })
