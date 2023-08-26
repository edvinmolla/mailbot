from django.shortcuts import render, HttpResponse, redirect
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
from .models import default
import email.utils
import openai
import base64
import datetime
from bs4 import BeautifulSoup
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.decorators import login_required

openai.api_key = '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'

def get_completion(prompt, model="gpt-3.5-turbo"):

    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
    model=model,
    messages=messages,
    temperature=0,
    )

    return response.choices[0].message["content"]

def home(request):

    print("ok")

    return render(request, "index.html")

def listing(request):
    return HttpResponse("redirect ok")

@login_required
def profile(request):
    global email
    full_name = vars(SocialAccount.objects.filter(user_id=request.user.id)[0])['extra_data']['name']
    email = vars(SocialAccount.objects.filter(user_id=request.user.id)[0])['extra_data']['email']
    image = vars(SocialAccount.objects.filter(user_id=request.user.id)[0])['extra_data']['picture']


    data = default.objects.filter(uemail=email)
    status = data.count() == 0

    return render(request, "profile.html", {'name':full_name, 'email':email, 'image':image, 'data': data, 'empty': status})
from email.parser import BytesParser

def fetch(request):



    


    default.objects.filter(uemail=email).delete()
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
                
                default(uemail=email, sender=sender.replace("<","(").replace('>',")"), subject=subject, time=str(pst_time).rsplit('-', 1)[0]).save()

                # if get_completion("tell me if this text is a complaint or not by simply stating True or False: " + str(body)):
                #     default(uemail=email, sender=sender.replace("<","(").replace('>',")"), subject=subject, time=str(pst_time).rsplit('-', 1)[0], replied=False).save() 
                #     exit()
    
    main()

    return HttpResponse("all ok")

def none(request): 
    default.objects.filter(uemail=email).delete()

    # # import the required libraries
    # from googleapiclient.discovery import build
    # from google_auth_oauthlib.flow import InstalledAppFlow
    # from google.auth.transport.requests import Request
    # import pickle
    # import os.path
    # import base64
    # from datetime import datetime
    # # from gpt import get_completion
    # from bs4 import BeautifulSoup
    
    # # Define the SCOPES. If modifying it, delete the token.pickle file.
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    global mail_array
    mail_array = []
    def getEmails():
        # Variable creds will store the user access token.
        # If no valid token found, we will create one.
        creds = None
    
        # The file token.pickle contains the user access token.
        # Check if it exists
        if os.path.exists('token.pickle'):
    
            # Read the token from the file and store it in the variable creds
            with open('edvin.pickle', 'rb') as token:
                creds = pickle.load(token)

      
    
        # If credentials are not available or are invalid, ask the user to log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(os.getcwd()+'/api.json', SCOPES)
                creds = flow.run_local_server(port=0)
         
                service = build('gmail', 'v1', credentials=creds)
                results = service.users().labels().list(userId='me').execute()
            
            # Save the access token in token.pickle file for the next run
            with open('edvin.pickle', 'wb') as token:
                pickle.dump(creds, token)
    
        # Connect to the Gmail API
        service = build('gmail', 'v1', credentials=creds)
    
        # request a list of all the messages
        result = service.users().messages().list(userId='me').execute()
    
        # We can also pass maxResults to get any number of emails. Like this:
        # result = service.users().messages().list(maxResults=200, userId='me').execute()
        messages = result.get('messages')
        count = 0
        # messages is a list of dictionaries where each dictionary contains a message id.
        
        # iterate through all the messages
        for msg in messages:
            # Get the message from its id
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()

            
            # Use try-except to avoid any Errors
            try:
                # Get value of 'payload' from dictionary 'txt'
                payload = txt['payload']
                headers = payload['headers']
    
                # Look for Subject and Sender Email in the headers
                for d in headers:
                    if d['name'] == 'Subject':
                        subject = d['value']
                    if d['name'] == 'From':
                        sender = d['value']
    
                # The Body of the message is in Encrypted format. So, we have to decode it.
                # Get the data and decode it with base 64 decoder.
                parts = payload.get('parts')[0]
                data = parts['body']['data']
                data = data.replace("-","+").replace("_","/")
                decoded_data = base64.b64decode(data)
    
                # Now, the data obtained is in lxml. So, we will parse 
                # it with BeautifulSoup library
                soup = BeautifulSoup(decoded_data , "lxml")
                body = soup.body()

                def check_reply(email_id):
                    # Get the thread containing the specified email
                    thread = service.users().threads().get(userId='me', id=email_id).execute()

                    # Check if the thread has more than one message (indicating a reply)
                    return len(thread['messages']) > 1


        
                print("From: ", sender)
                # print("Message: ", body)

                print("Subject: ", subject )
                print("Replied To: ", check_reply(msg['id']))
                print("Date received: ", datetime.fromtimestamp(int(txt["internalDate"]) / 1000).strftime('%m/%d/%y') + "\n\n")
                # print(get_completion("tell me if this text is a complaint or not by simply stating True or False: " + str(body)))
                
                default(uemail=email, sender=sender, subject=subject, time=datetime.fromtimestamp(int(txt["internalDate"]) / 1000).strftime('%m/%d/%y')).save()
                mail_array.append([sender, subject, datetime.fromtimestamp(int(txt["internalDate"]) / 1000).strftime('%m/%d/%y')])

                
            except Exception as e:
                print(e)

            count += 1
            print(count)
            if count == 9:
                break
    
                
        print(mail_array)
    getEmails()
    
    return HttpResponse(json.dumps(mail_array))