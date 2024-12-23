from django.urls import path
from . import views

app_name = 'tv_archive'

urlpatterns = [
    path('tv-arhivs', views.content_list, name='tv-arhivs'),
]
