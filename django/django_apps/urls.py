from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'main'

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include('google_api.urls')),
    path('google/', include('google_api.urls', namespace='google_api')),
    path('single_pages/', include('single_pages.urls', namespace='single_pages')),
    # path('', include('single_pages.urls')),
    path('', views.home),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
