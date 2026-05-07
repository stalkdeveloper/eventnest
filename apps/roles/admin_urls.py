from django.urls import path
from . import admin_views

app_name = 'admin_roles'

urlpatterns = [
    path('admin/roles/',                      admin_views.role_list,   name='role_list'),
    path('admin/roles/create/',               admin_views.role_create, name='role_create'),
    path('admin/roles/<int:role_id>/edit/',   admin_views.role_edit,   name='role_edit'),
    path('admin/roles/<int:role_id>/delete/', admin_views.role_delete, name='role_delete'),
]
