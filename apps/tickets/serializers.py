"""
apps/tickets/serializers.py
"""
from rest_framework import serializers
from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    event_title  = serializers.CharField(source='event.title',  read_only=True)
    event_slug   = serializers.CharField(source='event.slug',   read_only=True)
    event_date   = serializers.DateTimeField(source='event.start_date', read_only=True)
    event_venue  = serializers.CharField(source='event.venue',  read_only=True)
    event_city   = serializers.CharField(source='event.city',   read_only=True)
    event_type   = serializers.CharField(source='event.event_type', read_only=True)
    online_link  = serializers.SerializerMethodField()
    tier_name    = serializers.SerializerMethodField()
    qr_url       = serializers.SerializerMethodField()

    class Meta:
        model  = Ticket
        fields = [
            'id', 'ticket_code', 'status', 'amount_paid',
            'event', 'event_title', 'event_slug', 'event_date',
            'event_venue', 'event_city', 'event_type',
            'online_link', 'tier_name', 'qr_url', 'created_at',
        ]
        read_only_fields = ['ticket_code', 'status', 'amount_paid', 'created_at']

    def get_qr_url(self, obj):
        qr = obj.get_qr() if hasattr(obj, 'get_qr') else None
        return qr.get_url() if qr else None

    def get_online_link(self, obj):
        # Only show join link to the ticket holder
        request = self.context.get('request')
        if request and request.user == obj.attendee:
            return obj.event.online_link or None
        return None

    def get_tier_name(self, obj):
        return obj.tier.name if hasattr(obj, 'tier') and obj.tier else None
