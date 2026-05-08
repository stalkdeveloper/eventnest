from django.urls import path
from . import admin_views

app_name = 'admin_tickets'

urlpatterns = [
    path('admin/tickets/', admin_views.ticket_list, name='ticket_list'),
    path('admin/tickets/<int:ticket_id>/', admin_views.ticket_detail, name='ticket_detail'),
    path('admin/tickets/<int:ticket_id>/status/', admin_views.ticket_change_status, name='ticket_status'),
    path('admin/tickets/<int:ticket_id>/delete/', admin_views.ticket_delete, name='ticket_delete'),
]