import json
import time
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

def text_to_audio(text: str, lang: str = 'en') -> str:
    lang = 'en' if lang is None else lang
    audio = gTTS(text=text, lang=lang, slow=False)
    audio_file_path = os.path.join(settings.MEDIA_ROOT, 'email_audio.mp3')

    audio.save(audio_file_path)
    return os.path.join(settings.MEDIA_URL, 'email_audio.mp3')

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_labels():
    """
    Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    token_path = os.path.join(settings.BASE_DIR, 'google/token.json')
    client_secrets_path = os.path.join(settings.BASE_DIR, 'google/app_secrets.json')

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_path, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId="me", q="is:unread").execute()
        print("results:\n", results)
        resource_value = results.get("messages", [])


        if not resource_value:
            print("No resource found.")
            return

        labels_string = ""
        for message in resource_value:
            msg = service.users().messages().get(userId="me", id=message['id'], format='raw').execute()
            msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
            mime_message = BytesParser(policy=policy.default).parsebytes(msg_str)

            # Extract parts of the decoded message
            subject = mime_message['subject']
            sender = mime_message['from']
            print("mime_message:\n", mime_message)
            if mime_message.is_multipart():
                for part in mime_message.iter_parts():
                    if part.get_content_type() == 'text/plain':
                        body = part.get_payload(decode=True).decode('utf-8')
                        break
                print("Mime message is multipart!")
                print("body:\n", body)
            else:
                print("Mime message NOT multipart!")
                body = mime_message.get_payload(decode=True)
            print("body:\n", body)
            # time.sleep(10)

    except HttpError as error:
        # Handle errors from Gmail API.
        print(f"An error occurred: {error}")

    return body