from django.urls import path
from . import views
from gmail.utils import callback

urlpatterns = [
    path('', views.index, name='index'),
    path('audio', views.audio, name='audio'),
    path('callback', callback, name='callback'),
]
