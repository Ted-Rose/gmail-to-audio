from django.shortcuts import render, redirect
from gmail.utils import get_messages, text_to_audio, google_auth
from django.conf import settings
from django.http import JsonResponse



def index(request):
    if 'get_messages' in request.GET:
        creds = request.session.get('google_credentials')
        if creds:
            query = request.GET.get('query', '')
            messages = get_messages(query=query, creds=creds)

            if 'authorization_url' in messages and 'state' in messages:
                request.session['state'] = messages['state']
                return redirect(messages['authorization_url'])
            
            context = {'messages': messages}
            print("Got these messages: ", messages)
            return render(request, 'index.html', context)
        else:
            auth = google_auth()
            request.session['state'] = auth['state']
            return redirect(auth['authorization_url'])  # Redirect to authentication if no token

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
