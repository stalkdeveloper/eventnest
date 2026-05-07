from django.urls import path
from . import web_views

app_name = 'web_events'

urlpatterns = [
    path('events/',                              web_views.event_list,         name='event_list'),
    path('events/create/',                       web_views.event_create,       name='event_create'),
    path('events/my/',                           web_views.organiser_events,   name='organiser_events'),
    path('events/<slug:slug>/',                  web_views.event_detail,       name='event_detail'),
    path('events/<slug:slug>/register/',         web_views.register_for_event, name='register_event'),
    path('events/<slug:slug>/edit/',             web_views.event_edit,         name='event_edit'),
    path('events/<slug:slug>/attendees/',        web_views.event_attendees,    name='event_attendees'),
    path('my-tickets/',                          web_views.my_tickets,         name='my_tickets'),
    path('tickets/<int:ticket_id>/cancel/',      web_views.cancel_ticket,      name='cancel_ticket'),
]
