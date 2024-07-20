from django.urls import path, include
from . import views
from google_api.utils import callback

urlpatterns = [
    path('gmail-to-audio', views.index, name='index'),
    path('text-to-audio', views.audio, name='audio'),
    path('google/callback', callback, name='callback'),
]
