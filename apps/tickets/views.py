"""
apps/tickets/views.py  Optimized Tickets REST API.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Ticket
from .serializers import TicketSerializer


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class   = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = (
            Ticket.objects
            .filter(attendee=self.request.user)
            .select_related('event', 'event__category', 'attendee')
            .order_by('-created_at')
        )
        status_filter = self.request.query_params.get('status', '')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status != 'confirmed':
            return Response(
                {'detail': f'Cannot cancel a ticket with status "{ticket.status}".'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ticket.status     = 'cancelled'
        ticket.updated_by = request.user
        ticket.save(update_fields=['status', 'updated_by', 'updated_at'])
        try:
            from apps.core.email.mailer import Mailer
            Mailer.send_ticket_cancelled(ticket)
        except Exception:
            pass
        return Response({
            'message': 'Ticket cancelled successfully.',
            'ticket':  TicketSerializer(ticket, context={'request': request}).data,
        })

    @action(detail=True, methods=['get'])
    def qr(self, request, pk=None):
        ticket = self.get_object()
        qr = ticket.get_qr() if hasattr(ticket, 'get_qr') else None
        if not qr:
            return Response({'detail': 'QR code not available.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'qr_url': qr.get_url(), 'ticket_code': ticket.ticket_code})
