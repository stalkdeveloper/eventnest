from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Ticket


@login_required
def my_tickets(request):
    tickets = Ticket.objects.filter(attendee=request.user).select_related('event')
    return render(request, 'tickets/web/my_tickets.html', {'tickets': tickets})


@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, attendee=request.user)
    return render(request, 'tickets/web/detail.html', {'ticket': ticket})


@login_required
@require_POST
def cancel_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, attendee=request.user)
    
    if ticket.status == 'confirmed':
        ticket.status = 'cancelled'
        ticket.updated_by = request.user
        ticket.save(update_fields=['status', 'updated_by', 'updated_at'])
        messages.success(request, f'Ticket {ticket.ticket_code} cancelled.')
    else:
        messages.warning(request, 'This ticket cannot be cancelled.')
    
    return redirect('web_tickets:my_tickets')