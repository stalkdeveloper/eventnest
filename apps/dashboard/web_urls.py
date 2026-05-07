from django.urls import path
from . import web_views

app_name = 'web_dashboard'

urlpatterns = [
    path('dashboard/', web_views.dashboard, name='dashboard'),
]
