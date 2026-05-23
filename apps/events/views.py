"""
apps/events/views.py
Full Events REST API — list, detail, create, update, delete,
register, my_ticket, wishlist toggle, reviews, analytics.
"""
import uuid
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django.db.models import Q, Sum, Count
from django.shortcuts import get_object_or_404

from .models import Event
from .serializers import (
    EventListSerializer, EventDetailSerializer,
    EventCreateSerializer, ReviewSerializer, ReviewCreateSerializer,
)


class IsOrganiserOrReadOnly(permissions.BasePermission):
    """Allow read to all. Write only to the event organiser."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.organiser == request.user


class EventViewSet(viewsets.ModelViewSet):
    """
    GET    /api/v1/events/                        list all published events
    POST   /api/v1/events/                        create event (auth required)
    GET    /api/v1/events/{slug}/                 event detail
    PUT    /api/v1/events/{slug}/                 update event (organiser only)
    PATCH  /api/v1/events/{slug}/                 partial update (organiser only)
    DELETE /api/v1/events/{slug}/                 delete event (organiser only)
    GET    /api/v1/events/my_events/              my organised events (auth)
    POST   /api/v1/events/{slug}/register/        register for event (auth)
    DELETE /api/v1/events/{slug}/register/        cancel registration (auth)
    GET    /api/v1/events/{slug}/my_ticket/       my ticket for this event (auth)
    POST   /api/v1/events/{slug}/wishlist/        toggle wishlist (auth)
    GET    /api/v1/events/{slug}/reviews/         list reviews
    POST   /api/v1/events/{slug}/reviews/         submit review (auth + attended)
    DELETE /api/v1/events/{slug}/reviews/         delete my review (auth)
    GET    /api/v1/events/{slug}/analytics/       event analytics (organiser only)
    """
    lookup_field        = 'slug'
    permission_classes  = [IsAuthenticatedOrReadOnly, IsOrganiserOrReadOnly]

    # ── Queryset & Serializer ─────────────────────────────────────────────────

    def get_queryset(self):
        if self.action == 'my_events':
            return Event.objects.filter(
                organiser=self.request.user
            ).select_related('category').prefetch_related('tags').order_by('-created_at')

        qs = Event.objects.filter(status='published').select_related('category').prefetch_related('tags')

        q        = self.request.query_params.get('q', '')
        category = self.request.query_params.get('category', '')
        typ      = self.request.query_params.get('type', '')
        city     = self.request.query_params.get('city', '')
        free     = self.request.query_params.get('free', '')
        featured = self.request.query_params.get('featured', '')

        if q:        qs = qs.filter(Q(title__icontains=q) | Q(city__icontains=q) | Q(description__icontains=q))
        if category: qs = qs.filter(category__slug=category)
        if typ:      qs = qs.filter(event_type=typ)
        if city:     qs = qs.filter(city__icontains=city)
        if free == 'true':     qs = qs.filter(is_free=True)
        if featured == 'true': qs = qs.filter(is_featured=True)

        return qs

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EventCreateSerializer
        if self.action == 'retrieve':
            return EventDetailSerializer
        return EventListSerializer

    def get_permissions(self):
        if self.action in ['create', 'my_events', 'register', 'my_ticket', 'wishlist', 'reviews', 'analytics']:
            return [IsAuthenticated()]
        return super().get_permissions()

    # ── Create ────────────────────────────────────────────────────────────────

    def perform_create(self, serializer):
        import django.utils.text as slugify_module
        from django.utils.text import slugify
        title = serializer.validated_data.get('title', '')
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        while Event.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{counter}'
            counter += 1
        serializer.save(
            organiser=self.request.user,
            slug=slug,
            created_by=self.request.user,
        )

    # ── My Events ─────────────────────────────────────────────────────────────

    @action(detail=False, methods=['get'], url_path='my-events')
    def my_events(self, request):
        qs = self.get_queryset()
        serializer = EventListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    # ── Register / Cancel Registration ────────────────────────────────────────

    @action(detail=True, methods=['post', 'delete'])
    def register(self, request, slug=None):
        from apps.tickets.models import Ticket

        event = self.get_object()

        # DELETE → cancel registration
        if request.method == 'DELETE':
            ticket = Ticket.objects.filter(event=event, attendee=request.user, status='confirmed').first()
            if not ticket:
                return Response({'detail': 'No active registration found.'}, status=status.HTTP_404_NOT_FOUND)
            ticket.status     = 'cancelled'
            ticket.updated_by = request.user
            ticket.save(update_fields=['status', 'updated_by', 'updated_at'])
            return Response({'message': 'Registration cancelled.'})

        # POST → register
        if Ticket.objects.filter(event=event, attendee=request.user).exclude(status='cancelled').exists():
            return Response({'detail': 'Already registered for this event.'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_verified:
            return Response({'detail': 'Please verify your email before registering.'}, status=status.HTTP_403_FORBIDDEN)

        if event.spots_left == 0:
            return Response({'detail': 'Event is fully booked.'}, status=status.HTTP_400_BAD_REQUEST)

        # Paid events → return checkout info (frontend handles Razorpay)
        if not event.is_free and event.ticket_price > 0:
            return Response({
                'requires_payment': True,
                'checkout_url': f'/events/{event.slug}/checkout/',
                'amount':       float(event.ticket_price),
                'currency':     'INR',
                'event':        event.title,
            }, status=status.HTTP_200_OK)

        # Free → direct ticket
        ticket = Ticket.objects.create(
            event=event,
            attendee=request.user,
            ticket_code=f'TKT-{uuid.uuid4().hex[:8].upper()}',
            status='confirmed',
            amount_paid=0,
            created_by=request.user,
        )
        try:
            from apps.core.email.mailer import Mailer
            Mailer.send_ticket_confirmation(ticket)
        except Exception:
            pass

        from apps.tickets.serializers import TicketSerializer
        return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)

    # ── My Ticket ─────────────────────────────────────────────────────────────

    @action(detail=True, methods=['get'], url_path='my-ticket')
    def my_ticket(self, request, slug=None):
        from apps.tickets.models import Ticket
        from apps.tickets.serializers import TicketSerializer
        ticket = Ticket.objects.filter(event=self.get_object(), attendee=request.user).first()
        if not ticket:
            return Response({'detail': 'Not registered for this event.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(TicketSerializer(ticket).data)

    # ── Wishlist ──────────────────────────────────────────────────────────────

    @action(detail=True, methods=['post'])
    def wishlist(self, request, slug=None):
        from .models import Wishlist
        event = self.get_object()
        obj, created = Wishlist.objects.get_or_create(user=request.user, event=event)
        if not created:
            obj.delete()
        return Response({
            'saved':   created,
            'message': 'Added to wishlist.' if created else 'Removed from wishlist.',
            'count':   event.wishlisted_by.count(),
        })

    # ── Reviews ───────────────────────────────────────────────────────────────

    @action(detail=True, methods=['get', 'post', 'delete'])
    def reviews(self, request, slug=None):
        from .models import Review
        from apps.tickets.models import Ticket
        event = self.get_object()

        # GET → list all reviews
        if request.method == 'GET':
            reviews = event.reviews.select_related('reviewer').order_by('-created_at')
            return Response(ReviewSerializer(reviews, many=True).data)

        # POST → submit review
        if request.method == 'POST':
            ticket = Ticket.objects.filter(
                event=event, attendee=request.user, status__in=['confirmed', 'attended']
            ).first()
            if not ticket:
                return Response({'detail': 'Only verified attendees can leave a review.'}, status=status.HTTP_403_FORBIDDEN)
            if event.is_upcoming:
                return Response({'detail': 'Reviews open after the event ends.'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = ReviewCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            review, _ = Review.objects.update_or_create(
                event=event, reviewer=request.user,
                defaults=serializer.validated_data,
            )
            return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)

        # DELETE → delete my review
        if request.method == 'DELETE':
            deleted, _ = Review.objects.filter(event=event, reviewer=request.user).delete()
            if not deleted:
                return Response({'detail': 'No review found to delete.'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'message': 'Review deleted.'})

    # ── Analytics ─────────────────────────────────────────────────────────────

    @action(detail=True, methods=['get'])
    def analytics(self, request, slug=None):
        from apps.tickets.models import Ticket
        from django.db.models.functions import TruncDay

        event = self.get_object()
        if event.organiser != request.user:
            return Response({'detail': 'Only the organiser can view analytics.'}, status=status.HTTP_403_FORBIDDEN)

        tickets_qs = Ticket.all_objects.filter(event=event)

        daily = (
            tickets_qs.filter(status='confirmed')
            .annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(count=Count('id'), revenue=Sum('amount_paid'))
            .order_by('day')
        )

        status_counts = {
            'confirmed': tickets_qs.filter(status='confirmed').count(),
            'attended':  tickets_qs.filter(status='attended').count(),
            'cancelled': tickets_qs.filter(status='cancelled').count(),
            'pending':   tickets_qs.filter(status='pending').count(),
        }

        total_revenue = tickets_qs.filter(
            status='confirmed'
        ).aggregate(total=Sum('amount_paid'))['total'] or 0

        confirmed_attended = status_counts['confirmed'] + status_counts['attended']
        attendance_rate = round(
            (status_counts['attended'] / confirmed_attended * 100) if confirmed_attended else 0, 1
        )

        return Response({
            'event':            event.title,
            'status_counts':    status_counts,
            'total_tickets':    sum(status_counts.values()),
            'total_revenue':    float(total_revenue),
            'attendance_rate':  attendance_rate,
            'capacity_pct':     round(event.tickets_sold / event.max_capacity * 100, 1) if event.max_capacity else None,
            'daily_sales': [
                {
                    'date':    str(d['day'].date()),
                    'tickets': d['count'],
                    'revenue': float(d['revenue'] or 0),
                }
                for d in daily
            ],
        })
