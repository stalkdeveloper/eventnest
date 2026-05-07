from django.urls import path
from . import web_views

app_name = 'web_categories'

urlpatterns = [
    path('categories/',             web_views.category_list,   name='category_list'),
    path('categories/<slug:slug>/', web_views.category_detail, name='category_detail'),
]
