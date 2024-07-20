import base64
from email import policy
import json
from email.parser import BytesParser
from gtts import gTTS
from django.conf import settings
from django.shortcuts import redirect
import logging
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from datetime import datetime
from google_api import views
from langdetect import detect, DetectorFactory

logger = logging.getLogger('django')

def text_to_audio(text: str, lang: str = None, filename: str = None) -> str:
    DetectorFactory.seed = 0
    if lang is None:
        lang = detect(text)
        print("\n\n\nset lang to: ", lang)
        # Sometimes by mistake english is mistaken as german or danish
        if lang in ['da', 'de']:
            lang = 'en'
    # Replace URLs with the word "url"
    text = re.sub(r'https?://\S+', 'web link', text)
    # Remove long dashes
    text = re.sub(r'-{2,}', '', text)

    audio = gTTS(text=text, lang=lang, slow=False)
    filename = 'message_audio.mp3' if filename is None else str(filename) + '.mp3'
    audio_file_path = os.path.join(
        settings.MEDIA_ROOT,
        "recordings",
        filename
    )
    audio.save(audio_file_path)
    audio_url = settings.MEDIA_URL + 'recordings/' + filename
    return audio_url


def extract_text_from_html(html_content):
    # Remove HTML comments
    html_content = re.sub(r'<!--(.*?)-->', '', html_content, flags=re.DOTALL)
    
    # Remove all HTML tags
    clean_text = re.sub(r'<.*?>', '', html_content, flags=re.DOTALL)
    
    # Normalize spaces and remove extra newlines
    clean_text = re.sub(r'\s+', ' ', clean_text)
    
    return clean_text.strip()


def google_auth(creds=None):
    scopes = ["https://www.googleapis.com/auth/gmail.readonly"]
    client_secrets_path = os.path.join(settings.BASE_DIR, 'google_api/app_secrets.json')
    with open(client_secrets_path, 'r') as file:
        data = json.load(file)
    
    client_id = data.get('web', {}).get('client_id')
    client_secret = data.get('web', {}).get('client_secret')
    token_uri = data.get('web', {}).get('token_uri')
    
    if creds:
      creds = Credentials(
          token=creds['token'],
          refresh_token=creds['refresh_token'],
          client_secret=client_secret,
          client_id=client_id,
          token_uri=token_uri,
          scopes=scopes,
          expiry=datetime.fromisoformat(creds['expiry']),
      )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            can_refresh = creds.expiry > datetime.today()
            if can_refresh:
                creds.refresh(Request())
            else:
                creds = None  # Set creds to None to ensure we run the OAuth flow
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_path, scopes, redirect_uri = "https://127.0.0.1:8000/google/callback"
            )
            authorization_url, state  = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            return {"authorization_url": authorization_url, "state": state}
  
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)

    except HttpError as error:
        # Handle errors from Gmail API.
        print(f"An error occurred: {error}")
    return service


def get_messages(query, creds):
    """
    Returns a list of Gmail messages / emails that match the query.
    """
    try:
        service = google_auth(creds)
        # google_auth returns authorization_url if user has to authorize
        if isinstance(service, dict) and 'authorization_url' in service:
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

            # Try to remove any html elements if present
            body = extract_text_from_html(body)
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


def callback(request):
    scopes = ["https://www.googleapis.com/auth/gmail.readonly"]
    client_secrets_path = os.path.join(settings.BASE_DIR, 'google_api/app_secrets.json')

    flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_path,
                scopes,
                redirect_uri = "https://tedisrozenfelds.pythonanywhere.com/google/callback"
            )
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    credentials = flow.credentials
    request.session['google_credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'expiry': credentials.expiry.isoformat()
    }

    return redirect('google_api:gmail')
