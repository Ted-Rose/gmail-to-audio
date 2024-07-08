import base64
from email import policy
from email.parser import BytesParser
from gtts import gTTS
from django.conf import settings
from django.http import HttpResponseRedirect
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from datetime import datetime


def text_to_audio(text: str, lang: str = 'en', filename: str = None) -> str:
    lang = 'en' if lang is None else lang

    # Replace URLs with the word "url"
    text = re.sub(r'https?://\S+', 'web link', text)
    # Remove long dashes
    text = re.sub(r'-{2,}', '', text)

    # print("lang: ", lang)
    # print("slow: ", False)
    audio = gTTS(text=text, lang=lang, slow=False)
    filename = 'message_audio.mp3' if filename is None else str(filename) + '.mp3'
    # print("filename: ", filename)
    audio_file_path = os.path.join(
        settings.MEDIA_ROOT,
        "recordings",
        filename
    )
    audio.save(audio_file_path)
    audio_url = settings.MEDIA_URL + 'recordings/' + filename
    return audio_url


def google_auth():
    scopes = ["https://www.googleapis.com/auth/gmail.readonly"]
    creds = None
    token_path = os.path.join(settings.BASE_DIR, 'gmail/google/token.json')
    client_secrets_path = os.path.join(settings.BASE_DIR, 'gmail/google/app_secrets.json')

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
                client_secrets_path, scopes, redirect_uri = "http://127.0.0.1:8000/"
            )
            authorization_url, state  = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            if authorization_url:
                return {"authorization_url": authorization_url}
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)

    except HttpError as error:
        # Handle errors from Gmail API.
        print(f"An error occurred: {error}")
    return service


def get_messages(query):
    """
    Returns a list of Gmail messages / emails that match the query.
    """
    try:
        service = google_auth()
        if 'authorization_url' in service:
          return service

        results = service.users().messages().list(userId="me", q=query, maxResults=100).execute()
        messages = results.get("messages", [])
        
        message_details = []

        if not messages:
            print("No messages found.")
            return
        
        for message in messages:
            message_id = message['id']
            # Retrieve the raw message
            msg = service.users().messages().get(userId="me", id=message_id, format='raw').execute()
            msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
            mime_message = BytesParser(policy=policy.default).parsebytes(msg_str)

            # Extract the subject and from headers
            subject = mime_message['subject']
            sender = mime_message['from']

            # Initialize the body
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

            # Add message details to the list
            message_details.append({
                'id': message_id,
                'subject': subject,
                'sender': sender,
                'body': body
            })

    except HttpError as error:
        # Handle errors from Gmail API.
        print(f"An error occurred: {error}")
    
    return message_details
