from django.urls import path
from . import admin_views

app_name = 'admin_dashboard'

urlpatterns = [
    path('admin/dashboard/', admin_views.dashboard, name='dashboard'),
]
