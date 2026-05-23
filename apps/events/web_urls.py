from django.urls import path
from . import web_views
from .new_web_views import (
    event_analytics,
    toggle_wishlist, my_wishlist,
    submit_review, delete_review,
    manage_tiers,
)

app_name = 'web_events'

urlpatterns = [
    path('events/',                          web_views.event_list,        name='event_list'),
    path('events/create/',                   web_views.event_create,      name='event_create'),
    path('events/my-events/',                web_views.organiser_events,  name='organiser_events'),
    path('events/<slug:slug>/',              web_views.event_detail,      name='event_detail'),
    path('events/<slug:slug>/edit/',         web_views.event_edit,        name='event_edit'),
    path('events/<slug:slug>/register/',     web_views.register_for_event, name='register_event'),
    path('events/tag/<slug:slug>/',          web_views.tag_events,        name='tag_events'),

    path('events/<slug:slug>/analytics/',    event_analytics,             name='event_analytics'),

    path('events/<slug:slug>/wishlist/',     toggle_wishlist,             name='toggle_wishlist'),
    path('wishlist/',                        my_wishlist,                 name='my_wishlist'),

    path('events/<slug:slug>/review/',        submit_review,              name='submit_review'),
    path('events/<slug:slug>/review/delete/', delete_review,              name='delete_review'),

    path('events/<slug:slug>/tiers/',        manage_tiers,                name='manage_tiers'),
]