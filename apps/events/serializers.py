"""
apps/events/serializers.py
"""
from rest_framework import serializers
from django.db.models import Avg
from .models import Event, Tag
from apps.categories.models import Category


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Tag
        fields = ['id', 'name', 'slug', 'color']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ['id', 'title', 'slug']


class EventListSerializer(serializers.ModelSerializer):
    category     = CategorySerializer(read_only=True)
    tags         = TagSerializer(many=True, read_only=True)
    tickets_sold = serializers.IntegerField(read_only=True)
    spots_left   = serializers.IntegerField(read_only=True)
    is_upcoming  = serializers.BooleanField(read_only=True)
    avg_rating   = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    banner_url   = serializers.SerializerMethodField()
    organiser    = serializers.SerializerMethodField()

    class Meta:
        model  = Event
        fields = [
            'id', 'title', 'slug', 'event_type', 'status',
            'start_date', 'end_date', 'city', 'venue',
            'ticket_price', 'is_free', 'is_featured',
            'max_capacity', 'tickets_sold', 'spots_left',
            'is_upcoming', 'category', 'tags',
            'avg_rating', 'review_count',
            'banner_url', 'organiser',
        ]

    def get_banner_url(self, obj):
        banner = obj.get_banner() if hasattr(obj, 'get_banner') else None
        return banner.get_url() if banner else None

    def get_organiser(self, obj):
        return {'id': obj.organiser.id, 'username': obj.organiser.username}

    def get_avg_rating(self, obj):
        # Uses prefetched reviews if available to avoid extra query
        if hasattr(obj, '_prefetched_objects_cache') and 'reviews' in obj._prefetched_objects_cache:
            reviews = obj._prefetched_objects_cache['reviews']
            if not reviews:
                return None
            avg = sum(r.rating for r in reviews) / len(reviews)
            return round(avg, 1)
        agg = obj.reviews.aggregate(avg=Avg('rating'))
        return round(agg['avg'], 1) if agg['avg'] else None

    def get_review_count(self, obj):
        if hasattr(obj, '_prefetched_objects_cache') and 'reviews' in obj._prefetched_objects_cache:
            return len(obj._prefetched_objects_cache['reviews'])
        return obj.reviews.count()


class EventDetailSerializer(EventListSerializer):
    is_wishlisted = serializers.SerializerMethodField()
    tiers         = serializers.SerializerMethodField()

    class Meta(EventListSerializer.Meta):
        fields = EventListSerializer.Meta.fields + [
            'description', 'address', 'online_link',
            'created_at', 'updated_at',
            'is_wishlisted', 'tiers',
        ]

    def get_is_wishlisted(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.wishlisted_by.filter(user=request.user).exists()

    def get_tiers(self, obj):
        from apps.tickets.models import TicketTier
        tiers = obj.tiers.filter(is_active=True)
        return TicketTierSerializer(tiers, many=True).data


class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Event
        fields = [
            'title', 'description', 'event_type',
            'start_date', 'end_date',
            'venue', 'address', 'city', 'online_link',
            'ticket_price', 'is_free', 'max_capacity',
            'category', 'tags', 'is_featured',
        ]

    def validate(self, attrs):
        if attrs.get('end_date') and attrs.get('start_date'):
            if attrs['end_date'] < attrs['start_date']:
                raise serializers.ValidationError({'end_date': 'End date must be after start date.'})
        if not attrs.get('is_free') and not attrs.get('ticket_price'):
            raise serializers.ValidationError({'ticket_price': 'Paid events must have a ticket price.'})
        return attrs

    def create(self, validated_data):
        tags  = validated_data.pop('tags', [])
        event = Event.objects.create(**validated_data)
        event.tags.set(tags)
        return event

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance


# ── Ticket Tier ───────────────────────────────────────────────────────────────
class TicketTierSerializer(serializers.ModelSerializer):
    slots_left   = serializers.IntegerField(read_only=True)
    slots_sold   = serializers.IntegerField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        from apps.tickets.models import TicketTier
        model  = TicketTier
        fields = [
            'id', 'name', 'description', 'price',
            'total_slots', 'slots_sold', 'slots_left', 'is_available',
            'sale_start', 'sale_end', 'sort_order',
        ]


# ── Review ────────────────────────────────────────────────────────────────────
class ReviewSerializer(serializers.ModelSerializer):
    reviewer_username = serializers.CharField(source='reviewer.username', read_only=True)

    class Meta:
        from .models import Review
        model  = Review
        fields = [
            'id', 'rating', 'body',
            'reviewer_username', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import Review
        model  = Review
        fields = ['rating', 'body']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value
