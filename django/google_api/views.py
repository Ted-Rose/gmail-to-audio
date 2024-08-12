from django.shortcuts import render, redirect
from google_api.utils import get_messages, text_to_audio, google_auth
from django.http import JsonResponse


def gmail(request):
    if 'get_messages' in request.GET:
        creds = request.session.get('google_credentials')
        if creds:
            query = request.GET.get('query', '')
            messages = get_messages(query=query, creds=creds)

            # If user has to authorize authorization_url is returned
            if 'authorization_url' in messages and 'state' in messages:
                request.session['state'] = messages['state']
                return redirect(messages['authorization_url'])
            
            context = {'messages': messages}
            return render(request, 'gmail.html', context)
        else:
            auth = google_auth()
            request.session['state'] = auth['state']
            return redirect(auth['authorization_url'])

    return render(request, 'gmail.html')



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
