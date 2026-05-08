from django.urls import path
from . import admin_views

app_name = 'admin_events'

urlpatterns = [
    path('admin/events/', admin_views.event_list, name='event_list'),
    path('admin/events/create/', admin_views.event_create, name='event_create'),
    path('admin/events/<int:event_id>/', admin_views.event_detail, name='event_detail'),
    path('admin/events/<int:event_id>/edit/', admin_views.event_edit, name='event_edit'),
    path('admin/events/<int:event_id>/delete/', admin_views.event_delete, name='event_delete'),
    path('admin/events/<int:event_id>/status/', admin_views.event_change_status, name='event_status'),
    path('admin/events/<int:event_id>/attendees/', admin_views.event_attendees, name='event_attendees'),
]