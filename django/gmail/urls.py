from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('audio', views.audio, name='audio'),
]
