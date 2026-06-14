from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.accounts.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('accounts/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.businesses.urls')),
    path('staff/', include('apps.businesses.staff_urls')),
    path('', include('apps.bookings.urls')),
    path('', home, name='home'),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
