from rest_framework import serializers
from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    event_slug  = serializers.CharField(source='event.slug',  read_only=True)
    qr_url      = serializers.SerializerMethodField()

    class Meta:
        model  = Ticket
        fields = ['id','ticket_code','status','amount_paid','event','event_title','event_slug','created_at','qr_url']
        read_only_fields = ['ticket_code','status','amount_paid','created_at']

    def get_qr_url(self, obj):
        qr = obj.get_qr() if hasattr(obj, 'get_qr') else None
        return qr.get_url() if qr else None
