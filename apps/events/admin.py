from django.contrib import admin
from .models import Event, Ticket


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display  = ['title', 'organiser', 'status', 'event_type', 'start_date', 'city', 'is_featured', 'created_by', 'deleted_at']
    list_filter   = ['status', 'event_type', 'is_featured', 'category']
    search_fields = ['title', 'city', 'organiser__email']
    prepopulated_fields  = {'slug': ('title',)}
    list_editable = ['status', 'is_featured']
    readonly_fields = ['created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by', 'deleted_by']

    def get_queryset(self, request):
        return Event.all_objects.all()

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display  = ['ticket_code', 'attendee', 'event', 'status', 'amount_paid', 'created_at', 'created_by']
    list_filter   = ['status']
    search_fields = ['ticket_code', 'attendee__email', 'event__title']
    readonly_fields = ['created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by', 'deleted_by']

    def get_queryset(self, request):
        return Ticket.all_objects.all()
