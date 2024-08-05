from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from single_pages import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('google_api.urls')),
    path('twister', views.twister),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
