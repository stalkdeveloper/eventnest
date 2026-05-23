from rest_framework import serializers
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
    banner_url   = serializers.SerializerMethodField()

    class Meta:
        model  = Event
        fields = ['id','title','slug','event_type','status','start_date','end_date',
                  'city','venue','ticket_price','is_free','is_featured','max_capacity',
                  'tickets_sold','spots_left','is_upcoming','category','tags','banner_url']

    def get_banner_url(self, obj):
        banner = obj.get_banner() if hasattr(obj, 'get_banner') else None
        return banner.get_url() if banner else None


class EventDetailSerializer(EventListSerializer):
    class Meta(EventListSerializer.Meta):
        fields = EventListSerializer.Meta.fields + ['description','address','online_link','created_at','updated_at']
