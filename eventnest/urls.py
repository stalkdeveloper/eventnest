"""
EventNest — Master URL configuration
-------------------------------------
Pattern: include each app's web_urls and admin_urls separately.
No app needs to be in INSTALLED_APPS just for URLs.
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

handler403 = 'apps.core.error_views.error_403'
handler404 = 'apps.core.error_views.error_404'
handler500 = 'apps.core.error_views.error_500'

urlpatterns = [

    # ── Public website ──────────────────────────────────────────────────────
    path('', include('apps.core.web_urls')),               # /
    path('', include('apps.accounts.web_urls')),           # /login/ /register/ /profile/
    path('', include('apps.events.web_urls')),             # /events/* /my-tickets/
    path('', include('apps.categories.web_urls')),         # /categories/*
    path('', include('apps.dashboard.web_urls')),          # /dashboard/

    # ── Admin panel ─────────────────────────────────────────────────────────
    path('', include('apps.dashboard.admin_urls')),        # /admin/dashboard/
    path('', include('apps.accounts.admin_urls')),         # /admin/users/*
    path('', include('apps.events.admin_urls')),           # /admin/events/* /admin/tickets/
    path('', include('apps.categories.admin_urls')),       # /admin/categories/*
    path('', include('apps.roles.admin_urls')),            # /admin/roles/*

    # ── Shared ──────────────────────────────────────────────────────────────
    path('media/', include('apps.media.urls')),            # /media/upload/

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
