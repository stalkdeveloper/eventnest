from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('events/',                              views.event_list,         name='event_list'),
    path('events/create/',                       views.event_create,       name='event_create'),
    path('events/<slug:slug>/',                  views.event_detail,       name='event_detail'),
    path('events/<slug:slug>/register/',         views.register_for_event, name='register_event'),
    path('events/<slug:slug>/edit/',             views.event_edit,         name='event_edit'),
    path('events/<slug:slug>/delete/',           views.event_delete,       name='event_delete'),
    path('events/<slug:slug>/attendees/',        views.event_attendees,    name='event_attendees'),
    path('my-tickets/',                          views.my_tickets,         name='my_tickets'),
    path('tickets/<int:ticket_id>/cancel/',      views.cancel_ticket,      name='cancel_ticket'),
]
