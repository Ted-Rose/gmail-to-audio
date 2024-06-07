from django.shortcuts import render
from gmail.utils import text_to_audio


def index(request):
    audio_url = text_to_audio('Hello, World!', 'en')
    return render(request, 'index.html', {'audio_url': audio_url})
