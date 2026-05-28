"""
apps/tickets/web_views.py  Web ticket views + QR check-in (optimized).
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Ticket


def _is_organiser(user, event):
    return event.organiser == user or user.is_system_user


# ── My Tickets ────────────────────────────────────────────────────────────────

@login_required
def my_tickets(request):
    status_f = request.GET.get('status', '')
    tickets  = (
        Ticket.objects
        .filter(attendee=request.user)
        .select_related('event', 'event__category')
        .order_by('-created_at')
    )
    if status_f:
        tickets = tickets.filter(status=status_f)

    return render(request, 'tickets/web/my_tickets.html', {
        'tickets':       tickets,
        'status_filter': status_f,
        'status_choices': Ticket.Status.choices,
    })


@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(
        Ticket.objects.select_related('event', 'event__category', 'attendee'),
        id=ticket_id,
        attendee=request.user,
    )
    qr = ticket.get_qr() if hasattr(ticket, 'get_qr') else None
    return render(request, 'tickets/web/detail.html', {
        'ticket': ticket,
        'qr':     qr,
    })


@login_required
@require_POST
def cancel_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, attendee=request.user)
    if ticket.status == 'confirmed':
        ticket.status     = 'cancelled'
        ticket.updated_by = request.user
        ticket.save(update_fields=['status', 'updated_by', 'updated_at'])
        try:
            from apps.core.email.mailer import Mailer
            Mailer.send_ticket_cancelled(ticket)
        except Exception:
            pass
        messages.success(request, f'Ticket {ticket.ticket_code} cancelled.')
    else:
        messages.warning(request, f'Cannot cancel a ticket with status "{ticket.status}".')
    return redirect('web_tickets:my_tickets')


# ── QR Check-in ───────────────────────────────────────────────────────────────

@login_required
def checkin_page(request, slug):
    from apps.events.models import Event
    event = get_object_or_404(Event, slug=slug)
    if not _is_organiser(request.user, event):
        messages.error(request, 'Only the event organiser can check in attendees.')
        return redirect('web_events:event_detail', slug=slug)

    # Single aggregation query instead of 3 separate count calls
    from django.db.models import Count, Case, When, IntegerField
    agg = Ticket.objects.filter(event=event).aggregate(
        confirmed=Count(Case(When(status='confirmed', then=1), output_field=IntegerField())),
        attended=Count(Case(When(status='attended',  then=1), output_field=IntegerField())),
        total=Count('id'),
    )
    return render(request, 'tickets/web/checkin.html', {
        'event': event,
        'stats': agg,
    })


@login_required
def checkin_validate(request, slug):
    from apps.events.models import Event
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': 'Method not allowed.'}, status=405)

    event = get_object_or_404(Event, slug=slug)
    if not _is_organiser(request.user, event):
        return JsonResponse({'ok': False, 'message': 'Unauthorised.'}, status=403)

    try:
        data        = json.loads(request.body)
        ticket_code = data.get('ticket_code', '').strip().upper()
    except Exception:
        ticket_code = request.POST.get('ticket_code', '').strip().upper()

    if not ticket_code:
        return JsonResponse({'ok': False, 'message': 'No ticket code provided.'})

    try:
        ticket = (
            Ticket.objects
            .select_related('attendee')
            .get(ticket_code=ticket_code, event=event)
        )
    except Ticket.DoesNotExist:
        return JsonResponse({'ok': False, 'message': f'{ticket_code} not found for this event.'})

    name = ticket.attendee.get_full_name() or ticket.attendee.username

    if ticket.status == 'attended':
        return JsonResponse({
            'ok': False, 'message': f'{name} already checked in.',
            'attendee_name': name, 'ticket_code': ticket_code, 'status': 'already_attended',
        })
    if ticket.status == 'cancelled':
        return JsonResponse({
            'ok': False, 'message': f'Ticket {ticket_code} is cancelled.', 'status': 'cancelled',
        })
    if ticket.status != 'confirmed':
        return JsonResponse({
            'ok': False, 'message': f'Ticket status: {ticket.status}.', 'status': ticket.status,
        })

    ticket.status     = 'attended'
    ticket.updated_by = request.user
    ticket.save(update_fields=['status', 'updated_by', 'updated_at'])

    return JsonResponse({
        'ok': True, 'message': f'Welcome, {name}!',
        'attendee_name': name, 'ticket_code': ticket_code, 'status': 'attended',
    })
