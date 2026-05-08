from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_POST
from apps.core.decorators import system_required
from .models import Ticket


@system_required
def ticket_list(request):
    q = request.GET.get('q', '')
    status_f = request.GET.get('status', '')
    tickets = Ticket.all_objects.select_related('event', 'attendee', 'created_by').order_by('-created_at')
    
    if q:
        tickets = tickets.filter(
            Q(ticket_code__icontains=q) | 
            Q(attendee__email__icontains=q) | 
            Q(event__title__icontains=q)
        )
    if status_f:
        tickets = tickets.filter(status=status_f)
    
    return render(request, 'tickets/admin/list.html', {
        'tickets': tickets, 
        'q': q, 
        'status_filter': status_f,
    })


@system_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket.all_objects, pk=ticket_id)
    return render(request, 'tickets/admin/detail.html', {'ticket': ticket})


@system_required
@require_POST
def ticket_change_status(request, ticket_id):
    ticket = get_object_or_404(Ticket.all_objects, pk=ticket_id)
    status = request.POST.get('status')
    
    if status in dict(Ticket.Status.choices):
        ticket.status = status
        ticket.updated_by = request.user
        ticket.save(update_fields=['status', 'updated_by', 'updated_at'])
        messages.success(request, f'Ticket {ticket.ticket_code} status → {ticket.status}')
    
    return redirect('admin_tickets:ticket_list')


@system_required
@require_POST
def ticket_delete(request, ticket_id):
    ticket = get_object_or_404(Ticket.all_objects, pk=ticket_id)
    
    if ticket.deleted_at:
        ticket.restore()
        messages.success(request, f'Ticket "{ticket.ticket_code}" restored.')
    else:
        ticket.soft_delete(user=request.user)
        messages.success(request, f'Ticket "{ticket.ticket_code}" deleted.')
    
    return redirect('admin_tickets:ticket_list')