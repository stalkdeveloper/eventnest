"""
EventNest — Master URL configuration
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from apps.events.views  import EventViewSet
from apps.tickets.views import TicketViewSet

handler403 = 'apps.core.error_views.error_403'
handler404 = 'apps.core.error_views.error_404'
handler500 = 'apps.core.error_views.error_500'

router = DefaultRouter()
router.register(r'events',  EventViewSet,  basename='api-events')
router.register(r'tickets', TicketViewSet, basename='api-tickets')

urlpatterns = [
    # ── Public website ──────────────────────────────────────────────────────
    path('', include('apps.core.web_urls')),
    path('', include('apps.accounts.web_urls')),
    path('', include('apps.events.web_urls')),
    path('', include('apps.tickets.web_urls')),
    path('', include('apps.categories.web_urls')),
    path('', include('apps.dashboard.web_urls')),

    # ── Admin panel ─────────────────────────────────────────────────────────
    path('', include('apps.dashboard.admin_urls')),
    path('', include('apps.accounts.admin_urls')),
    path('', include('apps.events.admin_urls')),
    path('', include('apps.tickets.admin_urls')),
    path('', include('apps.categories.admin_urls')),
    path('', include('apps.roles.admin_urls')),

    # ── Shared ──────────────────────────────────────────────────────────────
    path('media/', include('apps.media.urls')),
    path('', include('apps.payments.urls')),

    # ── REST API ─────────────────────────────────────────────────────────────
    path('api/v1/', include('apps.accounts.api_urls')),   # auth endpoints
    path('api/v1/', include(router.urls)),                # events + tickets
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
