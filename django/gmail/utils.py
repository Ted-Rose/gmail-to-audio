import base64
from email import policy
from email.parser import BytesParser
from gtts import gTTS
from django.conf import settings
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from datetime import datetime


def text_to_audio(text: str, lang: str = 'en', file_name: str = None) -> str:
    lang = 'en' if lang is None else lang

    # Replace URLs with the word "url"
    text = re.sub(r'https?://\S+', 'web link', text)
    # Remove long dashes
    text = re.sub(r'-{2,}', '', text)

    print("\nText to audio:\n", text)
    # print("lang: ", lang)
    # print("slow: ", False)
    audio = gTTS(text=text, lang=lang, slow=False)
    file_name = 'message_audio.mp3' if file_name is None else str(file_name) + '.mp3'
    # print("file_name: ", file_name)
    audio_file_path = os.path.join(
        settings.MEDIA_ROOT,
        "recordings",
        file_name
    )
    print("audio_file_path: ", audio_file_path)
    audio.save(audio_file_path)
    print("Saved audio to: ", audio_file_path)
    return file_name


def build_google_service():
    scopes = ["https://www.googleapis.com/auth/gmail.readonly"]
    creds = None
    token_path = os.path.join(settings.BASE_DIR, 'google/token.json')
    client_secrets_path = os.path.join(settings.BASE_DIR, 'google/app_secrets.json')

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            can_refresh = creds.expiry < datetime.today()
            if can_refresh:
                creds.refresh(Request())
            else:
                creds = None  # Set creds to None to ensure we run the OAuth flow
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_path, scopes
            )
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token:
            token.write(creds.to_json())
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)

    except HttpError as error:
        # Handle errors from Gmail API.
        print(f"An error occurred: {error}")
    return service


def get_message_ids(query):
    """
    Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    try:
        # Call the Gmail API
        service = build_google_service()
        results = service.users().messages().list(userId="me", q=query, maxResults=100).execute()
        # print("results:\n", results)
        messages = results.get("messages", [])
        message_ids = [message['id'] for message in messages]

        if not messages:
            print("No messages found.")
            return

    except HttpError as error:
        # Handle errors from Gmail API.
        print(f"An error occurred: {error}")
    # print("Returning message_ids:\n", message_ids)
    return message_ids


def create_message_audio(message_id: str) -> str:
    service = build_google_service()

    msg = service.users().messages().get(userId="me", id=message_id, format='raw').execute()
    msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
    mime_message = BytesParser(policy=policy.default).parsebytes(msg_str)

    # Extract parts of the decoded message
    # subject = mime_message['subject']
    # sender = mime_message['from']
    # print("mime_message:\n", mime_message)
    body = None
    charset = mime_message.get_content_charset('utf-8')
    if mime_message.is_multipart():
        for part in mime_message.iter_parts():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True).decode(charset, errors='replace')
                break
        if not body:
            body = 'Multipart message without plain text part!'
    else:
        body = mime_message.get_payload(decode=True).decode(charset, errors='replace')

    # print("body:\n", body)
    audio_file_name = text_to_audio(text=body, file_name=message_id)

    return audio_file_name
