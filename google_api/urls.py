from django.urls import path
from . import views
from google_api.utils import callback

app_name = 'google_api'

urlpatterns = [
    path('gmail-to-audio', views.gmail, name='gmail'),
    path('text-to-audio', views.audio, name='audio'),
    path('google/callback', callback, name='callback'),
]
