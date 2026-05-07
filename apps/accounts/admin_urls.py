from django.urls import path
from . import admin_views

app_name = 'admin_accounts'

urlpatterns = [
    path('admin/users/',                                  admin_views.user_list,           name='user_list'),
    path('admin/users/create/',                           admin_views.user_create,         name='user_create'),
    path('admin/users/<int:user_id>/edit/',               admin_views.user_edit,           name='user_edit'),
    path('admin/users/<int:user_id>/delete/',             admin_views.user_delete,         name='user_delete'),
    path('admin/users/<int:user_id>/assign-role/',        admin_views.user_assign_role,    name='user_assign_role'),
    path('admin/users/<int:user_id>/make-subadmin/',      admin_views.user_make_subadmin,  name='user_make_subadmin'),
    path('admin/users/<int:user_id>/make-organiser/',     admin_views.user_make_organiser, name='user_make_organiser'),
]
