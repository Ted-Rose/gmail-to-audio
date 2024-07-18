from django.urls import path, include
from . import views
from google_api.utils import callback

urlpatterns = [
    path('gmail', views.index, name='index'),
    path('transcribe', views.audio, name='audio'),
    path('callback', callback, name='callback'),
]
# TODO
# Add a prefix to the urlpatterns
urlpatterns = [path('google/', include(urlpatterns))]
