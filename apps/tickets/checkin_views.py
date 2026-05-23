"""
Feature 6: QR Check-in views.
Append / merge into apps/tickets/web_views.py
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Ticket


def _is_organiser(user, event):
    return event.organiser == user or user.is_system_user


@login_required
def checkin_page(request, slug):
    from apps.events.models import Event
    event = get_object_or_404(Event, slug=slug)
    if not _is_organiser(request.user, event):
        messages.error(request, 'Only the event organiser can check in attendees.')
        return redirect('web_events:event_detail', slug=slug)
    stats = {
        'confirmed': Ticket.objects.filter(event=event, status='confirmed').count(),
        'attended':  Ticket.objects.filter(event=event, status='attended').count(),
        'total':     Ticket.objects.filter(event=event).count(),
    }
    return render(request, 'tickets/web/checkin.html', {'event': event, 'stats': stats})


@login_required
def checkin_validate(request, slug):
    from apps.events.models import Event
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': 'Method not allowed.'}, status=405)
    event = get_object_or_404(Event, slug=slug)
    if not _is_organiser(request.user, event):
        return JsonResponse({'ok': False, 'message': 'Unauthorised.'}, status=403)
    try:
        data = json.loads(request.body)
        ticket_code = data.get('ticket_code', '').strip().upper()
    except Exception:
        ticket_code = request.POST.get('ticket_code', '').strip().upper()
    if not ticket_code:
        return JsonResponse({'ok': False, 'message': 'No ticket code provided.'})
    try:
        ticket = Ticket.objects.get(ticket_code=ticket_code, event=event)
    except Ticket.DoesNotExist:
        return JsonResponse({'ok': False, 'message': f'{ticket_code} not found for this event.'})
    name = ticket.attendee.get_full_name() or ticket.attendee.username
    if ticket.status == 'attended':
        return JsonResponse({'ok': False, 'message': f'{name} already checked in.', 'attendee_name': name, 'ticket_code': ticket_code, 'status': 'already_attended'})
    if ticket.status == 'cancelled':
        return JsonResponse({'ok': False, 'message': f'Ticket {ticket_code} is cancelled.', 'status': 'cancelled'})
    if ticket.status != 'confirmed':
        return JsonResponse({'ok': False, 'message': f'Ticket status: {ticket.status}.', 'status': ticket.status})
    ticket.status = 'attended'
    ticket.updated_by = request.user
    ticket.save(update_fields=['status', 'updated_by', 'updated_at'])
    return JsonResponse({'ok': True, 'message': f'Welcome, {name}!', 'attendee_name': name, 'ticket_code': ticket_code, 'status': 'attended'})
