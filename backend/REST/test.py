from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# Set up OAuth 2.0 credentials
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_with_oauth():
    flow = InstalledAppFlow.from_client_secrets_file(os.getcwd()+'/api.json', SCOPES)
    credentials = flow.run_local_server(port=0)
    return credentials

def main():
    credentials = authenticate_with_oauth()

    # Set up Gmail API service
    service = build('gmail', 'v1', credentials=credentials)

    # List inbox emails
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No messages found.")
    else:
        print("Inbox emails:")
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            subject = ""
            for header in msg['payload']['headers']:
                if header['name'] == 'Subject':
                    subject = header['value']
                    break
            print(f"Subject: {subject}, From: {msg['payload']['headers'][16]['value']}")

if __name__ == "__main__":
    main()