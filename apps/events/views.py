import uuid
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Event
from .serializers import EventListSerializer, EventDetailSerializer


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'slug'

    def get_queryset(self):
        qs  = Event.objects.filter(status='published').select_related('category').prefetch_related('tags')
        q   = self.request.query_params.get('q', '')
        cat = self.request.query_params.get('category', '')
        typ = self.request.query_params.get('type', '')
        if q:   qs = qs.filter(Q(title__icontains=q) | Q(city__icontains=q))
        if cat: qs = qs.filter(category__slug=cat)
        if typ: qs = qs.filter(event_type=typ)
        return qs

    def get_serializer_class(self):
        return EventDetailSerializer if self.action == 'retrieve' else EventListSerializer

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def register(self, request, slug=None):
        from apps.tickets.models import Ticket
        from apps.tickets.serializers import TicketSerializer
        event = self.get_object()
        if Ticket.objects.filter(event=event, attendee=request.user).exists():
            return Response({'detail': 'Already registered.'}, status=status.HTTP_400_BAD_REQUEST)
        if event.spots_left == 0:
            return Response({'detail': 'Fully booked.'}, status=status.HTTP_400_BAD_REQUEST)
        ticket = Ticket.objects.create(
            event=event, attendee=request.user,
            ticket_code=f'TKT-{uuid.uuid4().hex[:8].upper()}',
            status='confirmed', amount_paid=event.ticket_price, created_by=request.user,
        )
        return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_ticket(self, request, slug=None):
        from apps.tickets.models import Ticket
        from apps.tickets.serializers import TicketSerializer
        ticket = Ticket.objects.filter(event=self.get_object(), attendee=request.user).first()
        if ticket:
            return Response(TicketSerializer(ticket).data)
        return Response({'detail': 'Not registered.'}, status=status.HTTP_404_NOT_FOUND)
