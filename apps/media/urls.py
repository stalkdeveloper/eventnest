from django.urls import path
from . import views

app_name = 'media'

urlpatterns = [
    path('upload/', views.upload, name='upload'),
    path('upload/profile-picture/', views.upload_profile_picture, name='upload_profile_picture'),
]
