import uuid
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.text import slugify
from django.db.models import Count, Q
from django.utils import timezone
from .models import Event, Ticket, Category


def is_organiser_or_admin(user):
    return user.groups.filter(name__in=['Organiser', 'Admin']).exists() or user.is_staff


def home(request):
    featured = Event.objects.filter(status='published', is_featured=True)[:6]
    upcoming = Event.objects.filter(status='published', start_date__gte=timezone.now()).order_by('start_date')[:8]
    categories = Category.objects.annotate(event_count=Count('events')).order_by('-event_count')[:8]
    return render(request, 'core/home.html', {
        'featured_events': featured,
        'upcoming_events': upcoming,
        'categories': categories,
    })


def event_list(request):
    events = Event.objects.filter(status='published')
    q = request.GET.get('q', '')
    category = request.GET.get('category', '')
    event_type = request.GET.get('type', '')

    if q:
        events = events.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(city__icontains=q))
    if category:
        events = events.filter(category__slug=category)
    if event_type:
        events = events.filter(event_type=event_type)

    categories = Category.objects.all()
    return render(request, 'core/event_list.html', {
        'events': events,
        'categories': categories,
        'current_category': category,
        'current_type': event_type,
        'query': q,
    })


def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug, status='published')
    user_ticket = None
    if request.user.is_authenticated:
        user_ticket = Ticket.objects.filter(event=event, attendee=request.user).first()
    return render(request, 'core/event_detail.html', {
        'event': event,
        'user_ticket': user_ticket,
        'banner': event.get_banner(),
    })


@login_required
def register_for_event(request, slug):
    event = get_object_or_404(Event, slug=slug, status='published')
    if Ticket.objects.filter(event=event, attendee=request.user).exists():
        messages.warning(request, 'You are already registered for this event.')
        return redirect('core:event_detail', slug=slug)

    if event.spots_left == 0:
        messages.error(request, 'Sorry, this event is fully booked.')
        return redirect('core:event_detail', slug=slug)

    ticket = Ticket.objects.create(
        event=event,
        attendee=request.user,
        ticket_code=f"TKT-{uuid.uuid4().hex[:8].upper()}",
        status='confirmed',
        amount_paid=event.ticket_price,
    )
    messages.success(request, f'Successfully registered! Your ticket code: {ticket.ticket_code}')
    return redirect('core:my_tickets')


@login_required
def my_tickets(request):
    tickets = Ticket.objects.filter(attendee=request.user).select_related('event')
    return render(request, 'core/my_tickets.html', {'tickets': tickets})


@login_required
def dashboard(request):
    if is_organiser_or_admin(request.user):
        return redirect('core:organiser_dashboard')
    tickets = Ticket.objects.filter(attendee=request.user).select_related('event')[:5]
    upcoming = Event.objects.filter(status='published', start_date__gte=timezone.now()).order_by('start_date')[:4]
    return render(request, 'core/dashboard.html', {
        'tickets': tickets,
        'upcoming_events': upcoming,
    })


@login_required
@user_passes_test(is_organiser_or_admin)
def organiser_dashboard(request):
    events = Event.objects.filter(organiser=request.user).annotate(
        confirmed_tickets=Count('tickets', filter=Q(tickets__status='confirmed'))
    )
    total_events = events.count()
    published = events.filter(status='published').count()
    total_attendees = sum(e.confirmed_tickets for e in events)
    return render(request, 'core/organiser_dashboard.html', {
        'events': events,
        'total_events': total_events,
        'published': published,
        'total_attendees': total_attendees,
    })


@login_required
def admin_dashboard(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('core:dashboard')
    from apps.accounts.models import CustomUser
    total_users = CustomUser.objects.count()
    total_events = Event.objects.count()
    total_tickets = Ticket.objects.filter(status='confirmed').count()
    recent_events = Event.objects.order_by('-created_at')[:10]
    return render(request, 'core/admin_dashboard.html', {
        'total_users': total_users,
        'total_events': total_events,
        'total_tickets': total_tickets,
        'recent_events': recent_events,
    })


@login_required
@user_passes_test(is_organiser_or_admin)
def event_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        slug = slugify(title) + '-' + uuid.uuid4().hex[:4]
        event = Event.objects.create(
            organiser=request.user,
            title=title,
            slug=slug,
            description=request.POST.get('description', ''),
            event_type=request.POST.get('event_type', 'offline'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            venue=request.POST.get('venue', ''),
            city=request.POST.get('city', ''),
            address=request.POST.get('address', ''),
            online_link=request.POST.get('online_link', ''),
            max_capacity=int(request.POST.get('max_capacity', 0)),
            ticket_price=float(request.POST.get('ticket_price', 0)),
            is_free=request.POST.get('is_free') == 'on',
            status='draft',
        )
        # Handle banner upload
        if 'banner' in request.FILES:
            from apps.media.utils import save_uploaded_file
            save_uploaded_file(request.FILES['banner'], event, 'event_banner')

        messages.success(request, f'Event "{event.title}" created successfully!')
        return redirect('core:organiser_dashboard')

    categories = Category.objects.all()
    return render(request, 'core/event_form.html', {'categories': categories, 'action': 'Create'})


@login_required
@user_passes_test(is_organiser_or_admin)
def event_edit(request, slug):
    event = get_object_or_404(Event, slug=slug, organiser=request.user)
    if request.method == 'POST':
        event.title = request.POST.get('title', event.title)
        event.description = request.POST.get('description', event.description)
        event.event_type = request.POST.get('event_type', event.event_type)
        event.start_date = request.POST.get('start_date', event.start_date)
        event.end_date = request.POST.get('end_date', event.end_date)
        event.venue = request.POST.get('venue', event.venue)
        event.city = request.POST.get('city', event.city)
        event.status = request.POST.get('status', event.status)
        event.max_capacity = int(request.POST.get('max_capacity', event.max_capacity))
        event.ticket_price = float(request.POST.get('ticket_price', event.ticket_price))
        event.is_free = request.POST.get('is_free') == 'on'
        event.save()
        messages.success(request, 'Event updated!')
        return redirect('core:organiser_dashboard')
    categories = Category.objects.all()
    return render(request, 'core/event_form.html', {
        'event': event,
        'categories': categories,
        'action': 'Edit',
    })


@login_required
@require_POST
def cancel_ticket(request, ticket_id):
    from django.views.decorators.http import require_POST
    ticket = get_object_or_404(Ticket, id=ticket_id, attendee=request.user)
    if ticket.status == 'confirmed':
        ticket.status = 'cancelled'
        ticket.save()
        messages.success(request, f'Ticket {ticket.ticket_code} has been cancelled.')
    else:
        messages.warning(request, 'This ticket cannot be cancelled.')
    return redirect('core:my_tickets')


@login_required
@user_passes_test(is_organiser_or_admin)
def event_delete(request, slug):
    event = get_object_or_404(Event, slug=slug, organiser=request.user)
    if request.method == 'POST':
        title = event.title
        event.delete()
        messages.success(request, f'Event "{title}" deleted.')
        return redirect('core:organiser_dashboard')
    return render(request, 'core/event_confirm_delete.html', {'event': event})


def event_attendees(request, slug):
    """Organiser/admin can see who registered for their event."""
    event = get_object_or_404(Event, slug=slug)
    if not (request.user == event.organiser or request.user.is_staff):
        messages.error(request, 'Access denied.')
        return redirect('core:event_detail', slug=slug)
    tickets = Ticket.objects.filter(event=event).select_related('attendee').order_by('-registered_at')
    return render(request, 'core/event_attendees.html', {'event': event, 'tickets': tickets})
