from django.shortcuts import render
from gmail.utils import get_message_ids, create_message_audio
from django.conf import settings


def index(request):
    if 'get_message_ids' in request.GET:
        # Call the get_emails method when the button is clicked
        message_ids = get_message_ids()
        # created_audios = create_message_audios(message_ids)
        request.session['message_ids'] = message_ids
        context = {'message_ids': message_ids}
        return render(request, 'index.html', context)

    elif 'create_message_audio' in request.GET:
        message_id = request.GET.get('message_id')
        create_message_audio(message_id)
        audio_url = settings.MEDIA_URL + 'recordings/' + message_id + '.mp3'
        created_audios = True
        print("Rendering audio_player")
        return render(request, 'index.html', {
            'message_ids': request.session.get('message_ids', []),
            'created_audios': created_audios,
            'audio_url': audio_url,
        })

    # Default behavior: read emails from labels and convert to audio
    return render(request, 'index.html')
