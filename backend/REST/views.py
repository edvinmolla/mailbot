from django.shortcuts import render, HttpResponse, redirect
import os 
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pickle
import json
import pytz
from simplegmail import Gmail
import os.path
import quopri
import email
from email.parser import BytesParser
from .models import default
import email.utils
import openai
import subprocess
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
    
    full_name = vars(SocialAccount.objects.filter(user_id=request.user.id)[0])['extra_data']['name']
    email = vars(SocialAccount.objects.filter(user_id=request.user.id)[0])['extra_data']['email']
    image = vars(SocialAccount.objects.filter(user_id=request.user.id)[0])['extra_data']['picture']
    
    
    data = default.objects.all()
    status = data.count() == 0
    return render(request, "profile.html", {'name':full_name, 'email':email, 'image':image, 'data': data, 'empty': status})




def fetch(request):
    default.objects.all().delete()
    user_list = ['edvin@ingeniousassetgroup.com', 'geoffrey@ingeniousassetgroup.com']
    
    def main(user):
        credentials = service_account.Credentials.from_service_account_file(
            'key.json',
            scopes=['https://www.googleapis.com/auth/gmail.readonly']
        )
       
        # Load the service account credentials from the JSON key file
        

        # Impersonate a user (employee) by setting their email address
        credentials = credentials.with_subject(user)

        # Create a Gmail API service
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

                try:
                    if get_completion("tell me if this text is a complaint or not by simply stating True or False: " + get_email_body(message['id'])) == "False":
                        continue
                except:
                    pass
                
                try:
                    payload = msg['payload']
                    headers = payload['headers']
                    receiver= ""
                    pst_time = ""
                except:
                    pass
                
                
                for d in headers:
                    if d['name'] == 'Subject':
                        subject = d['value']
                    if d['name'] == 'From':
                        sender = d['value']
                    if d['name'] == 'Delivered-To':
                        receiver = d['value']
                    if d['name'] == 'Date':
                        try:
                            date_str = d['value']
                            
                            date_str = date_str.rsplit(' ', 1)[0]
                            received_time_utc = datetime.datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S")
                            pacific_tz = pytz.timezone('US/Pacific')
                            pst_time = received_time_utc.astimezone(pacific_tz)
                        except:
                            pass
                
                

                default(uemail=user, receiver=receiver, sender=sender.replace("<","(").replace('>',")"), subject=subject, time=str(pst_time).rsplit('-', 1)[0]).save()
                
                # subject = ""
                # sender = ""
                # date_str = ""
                # pst_time = ""
                # for header in msg['payload']['headers']:
                #     if header['name'] == 'From':
                #         sender = header['value']
                #     elif header['name'] == 'Subject':
                #         subject = header['value']
                #     elif header['name'] == 'Date':
                #         try:
                #             date_str = header['value']
                            
                #             date_str = date_str.rsplit(' ', 1)[0]
                #             received_time_utc = datetime.datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S")
                #             pacific_tz = pytz.timezone('US/Pacific')
                #             pst_time = received_time_utc.astimezone(pacific_tz)
                #         except:
                #             pass
                
                #         default(uemail="edvin@ingeniousassetgroup.com", sender=sender.replace("<","(").replace('>',")"), subject=subject, time=str(pst_time).rsplit('-', 1)[0]).save()

                # if get_completion("tell me if this text is a complaint or not by simply stating True or False: " + str(body)):
                #     default(uemail=email, sender=sender.replace("<","(").replace('>',")"), subject=subject, time=str(pst_time).rsplit('-', 1)[0], replied=False).save() 
                #     exit()
    
    for i in user_list:
        main(i)

    return HttpResponse("all ok")

