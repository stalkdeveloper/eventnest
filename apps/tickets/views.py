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
        return Ticket.objects.filter(attendee=self.request.user).select_related('event')

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status != 'confirmed':
            return Response({'detail': 'Only confirmed tickets can be cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
        ticket.status = 'cancelled'
        ticket.updated_by = request.user
        ticket.save(update_fields=['status', 'updated_by', 'updated_at'])
        return Response(TicketSerializer(ticket).data)
