
import os 
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import json
import pytz
import os.path
import quopri
import email

import email.utils
import openai
import base64
import datetime
from bs4 import BeautifulSoup


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
    date_limit = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    query = f'after:{date_limit}'
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q=query).execute()
    messages = results.get('messages', [])

    

    def check_reply(email_id):
        
        # Get the thread containing the specified email
        thread = service.users().threads().get(userId='me', id=email_id).execute()

        # Check if the thread has more than one message (indicating a reply)
        return len(thread['messages']) > 1
    
    def get_email_body(email_id):
        try:
            # Get the email
            email_data = service.users().messages().get(userId='me', id=email_id, format='raw').execute()
            raw_email = base64.urlsafe_b64decode(email_data['raw']).decode('utf-8')

            # Parse the raw email content
            msg = BytesParser().parsebytes(raw_email.encode('utf-8'))

            # Find the first text/plain part of the message (email body)
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    email_body = part.get_payload(decode=True).decode('utf-8')
                    return email_body

            return None

        except:
            pass
    
    if not messages:
        pass
    else:
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            
            try:
                if check_reply(message['id']):
                    continue
            except:
                pass

            if get_completion("tell me if this text is a complaint or not by simply stating True or False: " + get_email_body(message['id'])) == "False":
                continue
            
            subject = ""
            sender = ""
            date_str = ""
            pst_time = ""
            for header in msg['payload']['headers']:
                if header['name'] == 'From':
                    sender = header['value']
                elif header['name'] == 'Subject':
                    subject = header['value']
                elif header['name'] == 'Date':
                    try:
                        date_str = header['value']
                        
                        date_str = date_str.rsplit(' ', 1)[0]
                        received_time_utc = datetime.datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S")
                        pacific_tz = pytz.timezone('US/Pacific')
                        pst_time = received_time_utc.astimezone(pacific_tz)
                    except:
                        pass
            
            

main()