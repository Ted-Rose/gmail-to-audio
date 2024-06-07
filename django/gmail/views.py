from django.shortcuts import render
from gmail.utils import text_to_audio, get_labels


def index(request):
    print("Calling get labels")
    labels = get_labels()
    print("labels in index:", labels)
    print("Calling get text_to_audio")
    audio_url = text_to_audio(labels, 'en')
    return render(request, 'index.html', {'audio_url': audio_url})
