from gtts import gTTS
from django.conf import settings
import os


def text_to_audio(text: str, lang: None):
    lang = 'en' if lang is None else lang
    audio = gTTS(text=text, lang=lang, slow=False)
    audio_file_path = os.path.join(settings.MEDIA_ROOT, 'email_audio.mp3')

    audio.save(audio_file_path)

    return os.path.join(settings.MEDIA_URL, 'email_audio.mp3')
