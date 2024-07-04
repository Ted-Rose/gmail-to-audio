from django.shortcuts import render
from gmail.utils import get_messages, text_to_audio
from django.conf import settings
from django.http import JsonResponse


def index(request):
    if 'get_messages' in request.GET:
        query = request.GET.get('query', '')
        messages = get_messages(query=query)
        context = {'messages': messages}
        return render(request, 'index.html', context)

    # Default behavior: read emails from labels and convert to audio
    return render(request, 'index.html')



def audio(request):
    if request.method == 'GET':
        text = request.GET.get('text')
        filename = request.GET.get('filename')
        audio_url = text_to_audio(text=text, filename=filename)
        
        # Return the audio URL as JSON response
        return JsonResponse({'audio_url': audio_url})
    else:
        # Return a 405 Method Not Allowed response for other request methods
        return JsonResponse({'error': 'Method Not Allowed'}, status=405)
