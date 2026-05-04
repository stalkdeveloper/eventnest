from django.urls import path
from . import views

app_name = 'panel'

urlpatterns = [
    # ── Dashboard ──────────────────────────────────────────────
    path('admin/dashboard/',                              views.dashboard,           name='dashboard'),

    # ── Users ──────────────────────────────────────────────────
    path('admin/users/',                                  views.user_list,           name='user_list'),
    path('admin/users/create/',                           views.user_create,         name='user_create'),
    path('admin/users/<int:user_id>/edit/',               views.user_edit,           name='user_edit'),
    path('admin/users/<int:user_id>/delete/',             views.user_delete,         name='user_delete'),
    path('admin/users/<int:user_id>/assign-role/',        views.user_assign_role,    name='user_assign_role'),
    path('admin/users/<int:user_id>/make-subadmin/',      views.user_make_subadmin,  name='user_make_subadmin'),
    path('admin/users/<int:user_id>/make-organiser/',     views.user_make_organiser, name='user_make_organiser'),

    # ── Categories ─────────────────────────────────────────────
    path('admin/categories/',                             views.category_list,       name='category_list'),
    path('admin/categories/create/',                      views.category_create,     name='category_create'),
    path('admin/categories/<int:cat_id>/',                views.category_detail,     name='category_detail'),
    path('admin/categories/<int:cat_id>/edit/',           views.category_edit,       name='category_edit'),
    path('admin/categories/<int:cat_id>/delete/',         views.category_delete,     name='category_delete'),

    # ── Events (full CRUD inside panel) ────────────────────────
    path('admin/events/',                                 views.event_list,          name='event_list'),
    path('admin/events/create/',                          views.event_create,        name='event_create'),
    path('admin/events/<int:event_id>/',                  views.event_detail,        name='event_detail'),
    path('admin/events/<int:event_id>/edit/',             views.event_edit,          name='event_edit'),
    path('admin/events/<int:event_id>/delete/',           views.event_delete,        name='event_delete'),
    path('admin/events/<int:event_id>/status/',           views.event_change_status, name='event_status'),
    path('admin/events/<int:event_id>/attendees/',        views.event_attendees,     name='event_attendees'),

    # ── Roles / Groups (full CRUD) ─────────────────────────────
    path('admin/roles/',                                  views.role_list,           name='role_list'),
    path('admin/roles/create/',                           views.role_create,         name='role_create'),
    path('admin/roles/<int:role_id>/edit/',               views.role_edit,           name='role_edit'),
    path('admin/roles/<int:role_id>/delete/',             views.role_delete,         name='role_delete'),
]
