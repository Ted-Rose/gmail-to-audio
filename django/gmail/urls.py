from django.urls import path, include
from . import views
from gmail.utils import callback

urlpatterns = [
    path('', views.index, name='index'),
    path('audio', views.audio, name='audio'),
    path('callback', callback, name='callback'),
]
# TODO
# Add a prefix to the urlpatterns
# urlpatterns = [path('google/', include(urlpatterns))]
