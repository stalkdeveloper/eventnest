import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from .models import Event, Ticket
from apps.categories.models import Category


def _is_organiser(user):
    return user.is_authenticated and (
        user.groups.filter(name='Organiser').exists() or user.is_system_user
    )


def event_list(request):
    events     = Event.objects.filter(status='published').select_related('category')
    q          = request.GET.get('q', '')
    cat_slug   = request.GET.get('category', '')
    event_type = request.GET.get('type', '')
    if q:
        events = events.filter(
            Q(title__icontains=q) | Q(description__icontains=q) | Q(city__icontains=q)
        )
    if cat_slug:
        events = events.filter(category__slug=cat_slug)
    if event_type:
        events = events.filter(event_type=event_type)
    return render(request, 'events/web/list.html', {
        'events': events,
        'categories': Category.objects.filter(parent=None),
        'current_category': cat_slug,
        'current_type': event_type,
        'query': q,
    })


def event_detail(request, slug):
    event       = get_object_or_404(Event, slug=slug, status='published')
    user_ticket = None
    if request.user.is_authenticated:
        user_ticket = Ticket.objects.filter(event=event, attendee=request.user).first()
    return render(request, 'events/web/detail.html', {
        'event': event, 'user_ticket': user_ticket, 'banner': event.get_banner(),
    })


@login_required
@require_POST
def register_for_event(request, slug):
    event = get_object_or_404(Event, slug=slug, status='published')
    if Ticket.objects.filter(event=event, attendee=request.user).exists():
        messages.warning(request, 'Already registered.')
        return redirect('web_events:event_detail', slug=slug)
    if event.spots_left == 0:
        messages.error(request, 'Event is fully booked.')
        return redirect('web_events:event_detail', slug=slug)
    Ticket.objects.create(
        event=event, attendee=request.user,
        ticket_code=f'TKT-{uuid.uuid4().hex[:8].upper()}',
        status='confirmed', amount_paid=event.ticket_price,
        created_by=request.user,
    )
    messages.success(request, 'Registered! Check My Tickets.')
    return redirect('web_events:my_tickets')


@login_required
def my_tickets(request):
    tickets = Ticket.objects.filter(attendee=request.user).select_related('event')
    return render(request, 'events/web/my_tickets.html', {'tickets': tickets})


@login_required
@require_POST
def cancel_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, attendee=request.user)
    if ticket.status == 'confirmed':
        ticket.status     = 'cancelled'
        ticket.updated_by = request.user
        ticket.save(update_fields=['status', 'updated_by', 'updated_at'])
        messages.success(request, f'Ticket {ticket.ticket_code} cancelled.')
    return redirect('web_events:my_tickets')


@login_required
def organiser_events(request):
    if not _is_organiser(request.user):
        return redirect('web_events:event_list')
    events = Event.objects.filter(organiser=request.user).annotate(
        confirmed_tickets=Count('tickets', filter=Q(tickets__status='confirmed'))
    )
    return render(request, 'events/web/organiser_events.html', {
        'events': events,
        'total_events':    events.count(),
        'published':       events.filter(status='published').count(),
        'total_attendees': sum(e.confirmed_tickets for e in events),
    })


@login_required
def event_create(request):
    if not _is_organiser(request.user):
        messages.error(request, 'Organisers only.')
        return redirect('web_events:event_list')
    categories = Category.objects.filter(parent=None)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        event = Event.objects.create(
            organiser=request.user,
            title=title,
            slug=slugify(title) + '-' + uuid.uuid4().hex[:4],
            description=request.POST.get('description', ''),
            event_type=request.POST.get('event_type', 'offline'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            venue=request.POST.get('venue', ''),
            city=request.POST.get('city', ''),
            address=request.POST.get('address', ''),
            online_link=request.POST.get('online_link', ''),
            max_capacity=int(request.POST.get('max_capacity', 0) or 0),
            ticket_price=float(request.POST.get('ticket_price', 0) or 0),
            is_free=request.POST.get('is_free') == 'on',
            status='draft',
            created_by=request.user, updated_by=request.user,
        )
        cat_id = request.POST.get('category')
        if cat_id:
            event.category_id = int(cat_id)
            event.save(update_fields=['category_id'])
        if 'banner' in request.FILES:
            from apps.media.utils import save_uploaded_file
            save_uploaded_file(request.FILES['banner'], event, 'event_banner')
        messages.success(request, f'Event "{event.title}" created as Draft.')
        return redirect('web_events:organiser_events')
    return render(request, 'events/web/form.html', {
        'categories': categories, 'action': 'Create',
    })


@login_required
def event_edit(request, slug):
    event      = get_object_or_404(Event, slug=slug, organiser=request.user)
    categories = Category.objects.filter(parent=None)
    if request.method == 'POST':
        event.title        = request.POST.get('title', event.title)
        event.description  = request.POST.get('description', event.description)
        event.event_type   = request.POST.get('event_type', event.event_type)
        event.start_date   = request.POST.get('start_date', event.start_date)
        event.end_date     = request.POST.get('end_date', event.end_date)
        event.venue        = request.POST.get('venue', event.venue)
        event.city         = request.POST.get('city', event.city)
        event.status       = request.POST.get('status', event.status)
        event.max_capacity = int(request.POST.get('max_capacity', event.max_capacity) or 0)
        event.ticket_price = float(request.POST.get('ticket_price', event.ticket_price) or 0)
        event.is_free      = request.POST.get('is_free') == 'on'
        event.updated_by   = request.user
        cat_id = request.POST.get('category')
        event.category_id  = int(cat_id) if cat_id else None
        event.save()
        messages.success(request, 'Event updated.')
        return redirect('web_events:organiser_events')
    return render(request, 'events/web/form.html', {
        'event': event, 'categories': categories, 'action': 'Edit',
    })


@login_required
def event_attendees(request, slug):
    event   = get_object_or_404(Event, slug=slug, organiser=request.user)
    tickets = Ticket.objects.filter(event=event).select_related('attendee').order_by('-created_at')
    return render(request, 'events/web/attendees.html', {'event': event, 'tickets': tickets})
