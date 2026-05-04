import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.text import slugify
from django.db.models import Count, Q
from django.views.decorators.http import require_POST
from .models import Event, Ticket
from apps.categories.models import Category


def is_organiser_or_admin(user):
    return (
        user.is_authenticated and (
            user.is_staff
            or user.groups.filter(name__in=['Organiser', 'Admin']).exists()
        )
    )


def event_list(request):
    events = Event.objects.filter(status='published').select_related('category', 'organiser')
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

    categories = Category.objects.filter(parent=None)
    return render(request, 'events/event_list.html', {
        'events': events,
        'categories': categories,
        'current_category': cat_slug,
        'current_type': event_type,
        'query': q,
    })


def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug, status='published')
    user_ticket = None
    if request.user.is_authenticated:
        user_ticket = Ticket.objects.filter(event=event, attendee=request.user).first()
    return render(request, 'events/event_detail.html', {
        'event': event,
        'user_ticket': user_ticket,
        'banner': event.get_banner(),
    })


@login_required
@require_POST
def register_for_event(request, slug):
    event = get_object_or_404(Event, slug=slug, status='published')
    if Ticket.objects.filter(event=event, attendee=request.user).exists():
        messages.warning(request, 'You are already registered for this event.')
        return redirect('events:event_detail', slug=slug)
    if event.spots_left == 0:
        messages.error(request, 'Sorry, this event is fully booked.')
        return redirect('events:event_detail', slug=slug)

    Ticket.objects.create(
        event=event,
        attendee=request.user,
        ticket_code=f'TKT-{uuid.uuid4().hex[:8].upper()}',
        status='confirmed',
        amount_paid=event.ticket_price,
        created_by=request.user,
    )
    messages.success(request, 'Successfully registered! Check My Tickets for your code.')
    return redirect('events:my_tickets')


@login_required
def my_tickets(request):
    tickets = Ticket.objects.filter(attendee=request.user).select_related('event')
    return render(request, 'events/my_tickets.html', {'tickets': tickets})


@login_required
@require_POST
def cancel_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, attendee=request.user)
    if ticket.status == 'confirmed':
        ticket.soft_delete(user=request.user)
        ticket.status = 'cancelled'
        ticket.updated_by = request.user
        ticket.save(update_fields=['status', 'updated_by', 'updated_at'])
        messages.success(request, f'Ticket {ticket.ticket_code} cancelled.')
    else:
        messages.warning(request, 'This ticket cannot be cancelled.')
    return redirect('events:my_tickets')


@login_required
@user_passes_test(is_organiser_or_admin)
def event_create(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        slug  = slugify(title) + '-' + uuid.uuid4().hex[:4]
        event = Event.objects.create(
            organiser    = request.user,
            title        = title,
            slug         = slug,
            description  = request.POST.get('description', ''),
            event_type   = request.POST.get('event_type', 'offline'),
            start_date   = request.POST.get('start_date'),
            end_date     = request.POST.get('end_date'),
            venue        = request.POST.get('venue', ''),
            city         = request.POST.get('city', ''),
            address      = request.POST.get('address', ''),
            online_link  = request.POST.get('online_link', ''),
            max_capacity = int(request.POST.get('max_capacity', 0) or 0),
            ticket_price = float(request.POST.get('ticket_price', 0) or 0),
            is_free      = request.POST.get('is_free') == 'on',
            status       = 'draft',
            created_by   = request.user,
            updated_by   = request.user,
        )
        cat_id = request.POST.get('category')
        if cat_id:
            event.category_id = int(cat_id)
            event.save(update_fields=['category_id'])

        if 'banner' in request.FILES:
            from apps.media.utils import save_uploaded_file
            save_uploaded_file(request.FILES['banner'], event, 'event_banner')

        messages.success(request, f'Event "{event.title}" created!')
        return redirect('core:organiser_dashboard')

    return render(request, 'events/event_form.html', {
        'categories': categories, 'action': 'Create'
    })


@login_required
@user_passes_test(is_organiser_or_admin)
def event_edit(request, slug):
    # Admins can edit any event; organisers only their own
    if request.user.is_staff:
        event = get_object_or_404(Event, slug=slug)
    else:
        event = get_object_or_404(Event, slug=slug, organiser=request.user)

    categories = Category.objects.all()
    if request.method == 'POST':
        event.title        = request.POST.get('title', event.title)
        event.description  = request.POST.get('description', event.description)
        event.event_type   = request.POST.get('event_type', event.event_type)
        event.start_date   = request.POST.get('start_date', event.start_date)
        event.end_date     = request.POST.get('end_date', event.end_date)
        event.venue        = request.POST.get('venue', event.venue)
        event.city         = request.POST.get('city', event.city)
        event.address      = request.POST.get('address', event.address)
        event.status       = request.POST.get('status', event.status)
        event.max_capacity = int(request.POST.get('max_capacity', event.max_capacity) or 0)
        event.ticket_price = float(request.POST.get('ticket_price', event.ticket_price) or 0)
        event.is_free      = request.POST.get('is_free') == 'on'
        event.updated_by   = request.user
        cat_id = request.POST.get('category')
        event.category_id  = int(cat_id) if cat_id else None
        event.save()

        if 'banner' in request.FILES:
            from apps.media.utils import save_uploaded_file
            save_uploaded_file(request.FILES['banner'], event, 'event_banner')

        messages.success(request, 'Event updated!')
        if request.user.is_staff:
            return redirect('core:admin_dashboard')
        return redirect('core:organiser_dashboard')

    return render(request, 'events/event_form.html', {
        'event': event, 'categories': categories, 'action': 'Edit'
    })


@login_required
@user_passes_test(is_organiser_or_admin)
def event_delete(request, slug):
    if request.user.is_staff:
        event = get_object_or_404(Event, slug=slug)
    else:
        event = get_object_or_404(Event, slug=slug, organiser=request.user)

    if request.method == 'POST':
        event.soft_delete(user=request.user)
        messages.success(request, f'Event "{event.title}" deleted.')
        if request.user.is_staff:
            return redirect('core:admin_dashboard')
        return redirect('core:organiser_dashboard')

    return render(request, 'events/event_confirm_delete.html', {'event': event})


@login_required
@user_passes_test(is_organiser_or_admin)
def event_attendees(request, slug):
    if request.user.is_staff:
        event = get_object_or_404(Event, slug=slug)
    else:
        event = get_object_or_404(Event, slug=slug, organiser=request.user)
    tickets = Ticket.objects.filter(event=event).select_related('attendee').order_by('-created_at')
    return render(request, 'events/event_attendees.html', {
        'event': event, 'tickets': tickets
    })
