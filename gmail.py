
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pickle
import os.path
import base64
from datetime import datetime
from gpt import get_completion
from bs4 import BeautifulSoup
  

  
def getEmails():
  
    # We can also pass maxResults to get any number of emails. Like this:
    # result = service.users().messages().list(maxResults=200, userId='me').execute()
    messages = result.get('messages')
  
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


            
        except:
            pass
  
  
getEmails()