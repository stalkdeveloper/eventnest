from django.urls import path
from . import web_views

app_name = 'web_home'

urlpatterns = [
    path('', web_views.home, name='home'),
]
