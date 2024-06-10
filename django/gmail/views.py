from django.shortcuts import render
from gmail.utils import text_to_audio, get_message_ids, create_message_audios

def index(request):
    if 'create_message_audios' in request.GET:
        # Call the get_emails method when the button is clicked
        created_audios = create_message_audios(request.session.get('message_ids', []))
        context = {'created_audios': created_audios}
        print("in create_message_audios with context: \n", context)
        return render(request, 'index.html', context)

    if 'get_message_ids' in request.GET:
        # Call the get_emails method when the button is clicked
        message_ids, service = get_message_ids()
        created_audios = create_message_audios(message_ids, service)
        request.session['message_ids'] = message_ids
        context = {'message_ids': message_ids, 'created_audios': created_audios}
        return render(request, 'index.html', context, service)

    # Default behavior: read emails from labels and convert to audio
    return render(request, 'index.html')
