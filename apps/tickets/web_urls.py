from django.urls import path
from . import web_views
from .checkin_views import checkin_page, checkin_validate

app_name = 'web_tickets'

urlpatterns = [
    path('my-tickets/',                      web_views.my_tickets,    name='my_tickets'),
    path('tickets/<int:ticket_id>/cancel/',  web_views.cancel_ticket, name='cancel_ticket'),
    path('tickets/<int:ticket_id>/',         web_views.ticket_detail, name='ticket_detail'),

    path('events/<slug:slug>/checkin/',          checkin_page,     name='checkin_page'),
    path('events/<slug:slug>/checkin/validate/', checkin_validate, name='checkin_validate'),
]