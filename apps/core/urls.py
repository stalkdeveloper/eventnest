from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<slug:slug>/', views.event_detail, name='event_detail'),
    path('events/<slug:slug>/register/', views.register_for_event, name='register_event'),
    path('events/<slug:slug>/edit/', views.event_edit, name='event_edit'),
    path('events/<slug:slug>/delete/', views.event_delete, name='event_delete'),
    path('events/<slug:slug>/attendees/', views.event_attendees, name='event_attendees'),
    path('tickets/<int:ticket_id>/cancel/', views.cancel_ticket, name='cancel_ticket'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/organiser/', views.organiser_dashboard, name='organiser_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
]
