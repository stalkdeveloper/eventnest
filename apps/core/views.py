from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone


def home(request):
    from apps.events.models import Event
    from apps.categories.models import Category
    featured = Event.objects.filter(status='published', is_featured=True)[:6]
    upcoming = Event.objects.filter(
        status='published', start_date__gte=timezone.now()
    ).order_by('start_date')[:8]
    categories = Category.objects.filter(parent=None).annotate(
        event_count=Count('events')
    ).order_by('-event_count')[:8]
    return render(request, 'core/home.html', {
        'featured_events': featured,
        'upcoming_events': upcoming,
        'categories': categories,
    })


@login_required
def dashboard(request):
    """Route to the correct dashboard based on account_type / role."""
    # system users → custom panel
    if request.user.is_system_user:
        return redirect('panel:dashboard')
    # organisers → organiser dashboard
    if request.user.groups.filter(name='Organiser').exists():
        return redirect('core:organiser_dashboard')
    # guests → guest dashboard
    from apps.events.models import Event, Ticket
    tickets  = Ticket.objects.filter(attendee=request.user).select_related('event')[:5]
    upcoming = Event.objects.filter(
        status='published', start_date__gte=timezone.now()
    ).order_by('start_date')[:4]
    return render(request, 'core/dashboard.html', {
        'tickets': tickets, 'upcoming_events': upcoming,
    })


@login_required
def organiser_dashboard(request):
    from apps.events.models import Event, Ticket
    from django.db.models import Q
    if not (request.user.groups.filter(name__in=['Organiser', 'Admin']).exists()
            or request.user.is_staff):
        return redirect('core:dashboard')
    events = Event.objects.filter(organiser=request.user).annotate(
        confirmed_tickets=Count('tickets', filter=Q(tickets__status='confirmed'))
    )
    total_attendees = sum(e.confirmed_tickets for e in events)
    return render(request, 'core/organiser_dashboard.html', {
        'events':           events,
        'total_events':     events.count(),
        'published':        events.filter(status='published').count(),
        'total_attendees':  total_attendees,
    })


@login_required
def admin_dashboard(request):
    """Legacy redirect → custom panel dashboard."""
    if not request.user.is_system_user:
        return redirect('core:dashboard')
    return redirect('panel:dashboard')
