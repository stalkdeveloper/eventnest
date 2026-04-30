from django.contrib import admin
from .models import Event, Ticket, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'organiser', 'status', 'event_type', 'start_date', 'city', 'is_featured', 'tickets_sold']
    list_filter = ['status', 'event_type', 'is_featured', 'category']
    search_fields = ['title', 'city', 'organiser__email']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['status', 'is_featured']
    ordering = ['-created_at']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_code', 'attendee', 'event', 'status', 'amount_paid', 'registered_at']
    list_filter = ['status']
    search_fields = ['ticket_code', 'attendee__email', 'event__title']
    ordering = ['-registered_at']
