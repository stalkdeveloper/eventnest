from django.urls import path
from . import admin_views

app_name = 'admin_categories'

urlpatterns = [
    path('admin/categories/',                        admin_views.category_list,   name='category_list'),
    path('admin/categories/create/',                 admin_views.category_create, name='category_create'),
    path('admin/categories/<int:cat_id>/',           admin_views.category_detail, name='category_detail'),
    path('admin/categories/<int:cat_id>/edit/',      admin_views.category_edit,   name='category_edit'),
    path('admin/categories/<int:cat_id>/delete/',    admin_views.category_delete, name='category_delete'),
]
