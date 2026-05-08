from django.urls import path
from . import web_views

app_name = 'web_tickets'

urlpatterns = [
    path('my-tickets/', web_views.my_tickets, name='my_tickets'),
    path('tickets/<int:ticket_id>/cancel/', web_views.cancel_ticket, name='cancel_ticket'),
    path('tickets/<int:ticket_id>/', web_views.ticket_detail, name='ticket_detail'),
]