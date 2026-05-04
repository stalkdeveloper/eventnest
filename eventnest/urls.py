from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

handler403 = 'apps.core.error_views.error_403'
handler404 = 'apps.core.error_views.error_404'
handler500 = 'apps.core.error_views.error_500'

urlpatterns = [
    path('', include('apps.accounts.urls')),
    path('', include('apps.core.urls')),
    path('', include('apps.events.urls')),
    path('', include('apps.panel.urls')),
    path('media/', include('apps.media.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
