import os
import sys
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import re
from datetime import datetime
import base64
from io import BytesIO
import pandas as pd
#import pprint


database = os.path.abspath(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

sys.path.append(database)

from Luigi_Workflow.db import Update_token_gmail

sys.path.remove(database)

formats = [
            '%d-%m-%Y', '%d/%m/%Y', '%d %m %Y',
            '%d-%b-%Y', '%d/%b/%Y', '%d %b %Y',
            '%d-%B-%Y', '%d/%B/%Y', '%d %B %Y',
            '%Y-%m-%d', '%Y/%m/%d', '%Y %m %d',
            '%Y-%b-%d', '%Y/%b/%d', '%Y %b %d',
            '%Y-%B-%d', '%Y/%B/%d', '%Y %B %d',
            '%B %d, %Y', '%b %d, %Y',
            '%m-%d-%Y', '%m/%d/%Y', '%m %d %Y',
            '%b-%d-%Y', '%b/%d/%Y', '%b %d %Y',
            '%B-%d-%Y', '%B/%d/%Y', '%B %d %Y'
        ]

regexes = []
for fmt in formats:
    # Replace %d, %m, %b, %B, and %Y with regular expression patterns
    regex = fmt.replace(r'%d', r'([1-9]|0[1-9]|[1-2][0-9]|3[0-1])')
    regex = regex.replace(r'%m', r'([1-9]|0[1-9]|1[0-2])')
    regex = regex.replace(r'%b', r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)')
    regex = regex.replace(r'%B', r'(January|February|March|April|May|June|July|August|September|October|November|December)')
    regex = regex.replace(r'%Y', r'\d{4}')
    regex = regex.replace(r" ", r"\s")
    regex = r"\b"+regex+r"\b"
    regexes.append(re.compile(regex, re.IGNORECASE))

update_token = Update_token_gmail()
update_token.run()
token_folder=os.path.join(database, "Luigi_Workflow", "Tokens", "gmail_tokens")

files = os.listdir(token_folder)

for file in files:
    if file.startswith('token_gmail_api'):
        token=os.path.join(token_folder, file)




def format_date(date_given):
    i=date_given
    i = str(i)
    i = i.strip()
    if ("/" in i) or ("-" in i):
        i = "".join(i.split())
    

    for index, regex in enumerate(regexes):
        for match in regex.finditer(i):
            date_string = match.group()
            return datetime.strptime(date_string, formats[index]).strftime("%Y/%m/%d")


def save_attachment(attachment, save_dir):
            file_data = base64.urlsafe_b64decode(attachment['body']['data'])
            


##############################################################################################################

"""Functions are defined below"""

##############################################################################################################


def get_mails(sent_to="", recieved_from="", after="", before=""):
    """
    Returns a list of mails that match the given criteria.
    sent_to: Email address of the recipient.
    recieved_from: Email address of the sender.
    after: Start date of the mails to be retrieved. Included in the list.
    before: End date of the mails to be retrieved. Not Included in the list.
    """
    query = ""
    flag = 0
    if sent_to:
        query += "to:" + sent_to
        flag = 1
    if recieved_from:
        if flag==1:
            query += " "
        query += "from:" + recieved_from
        flag=1
    if after:
        if flag==1:
            query += " "
        after=format_date(after)
        query += "after:" + after
        flag=1
    if before:
        if flag==1:
            query += " "
        before=format_date(before)
        query += "before:" + before
    
    Scopes=['https://www.googleapis.com/auth/gmail.readonly']

    # Create a Gmail API client using OAuth2 credentials
    creds = Credentials.from_authorized_user_file(token, scopes=Scopes) #allow read only access
    
    service = build('gmail', 'v1', credentials=creds)
    
    # Search for the email with the given search query
    result = service.users().messages().list(userId='me', q=query).execute()
    
    messages = result.get('messages')
    data=[]
    if messages:
        for message in messages:
            msg = service.users().messages().get(userId="me", id=message['id']).execute()
            data.append(msg)
    return data #Returns everything in a dictionary format


#######################################################################################################################################
    
def get_mail_messages(sent_to="", recieved_from="", after="", before=""):
    msg = get_mails(sent_to, recieved_from, after, before)
    li=[]
    for message in msg:
        payload = message['payload']
        parts = payload.get('parts', [])
        
        def get_text(parts):

            text_content = ""

            for part in parts:
                mimeType = part['mimeType']
                body = part.get('body')

                if mimeType == 'text/plain':
                    data = body.get('data')
                    if data:
                        text_content += base64.urlsafe_b64decode(data).decode()

                elif mimeType == 'multipart/alternative':
                    parts = part.get('parts', [])
                    text_content += get_text(parts)
            
            return text_content
        li.append(get_text(parts))
    return li


#######################################################################################################################################


def get_mail_html(sent_to="", recieved_from="", after="", before=""):
    msg = get_mails(sent_to, recieved_from, after, before)
    li=[]
    for message in msg:
        payload = message['payload']
        parts = payload.get('parts', [])
        
        def get_text(parts):

            text_content = ""

            for part in parts:
                mimeType = part['mimeType']
                body = part.get('body')
                        
                if mimeType == 'text/html':
                    data = body.get('data')
                    if data:
                        # You can choose to handle HTML content differently if needed
                        # Here, we simply append the raw HTML content to the text_content
                        text_content += base64.urlsafe_b64decode(data).decode()

                elif mimeType == 'multipart/alternative':
                    parts = part.get('parts', [])
                    text_content += get_text(parts)
            
            return text_content
        li.append(get_text(parts))
    return li


######################################################################################################################################


def download_mail_attachments(sent_to="", recieved_from="", after="", before="", save_path=os.path.dirname(os.path.abspath(__file__))):
    
    msg = get_mails(sent_to, recieved_from, after, before)
    
    Scopes=['https://www.googleapis.com/auth/gmail.readonly']
        
    creds = Credentials.from_authorized_user_file(token, scopes=Scopes)
    
    service = build('gmail', 'v1', credentials=creds)
    
    for message in msg:
        
        ms = service.users().messages().get(userId="me", id=message['id']).execute()
            
        for part in ms['payload']['parts']:
            # Check if the part contains an attachment
            if part.get('filename'):
                # Decode the attachment data and save it to a file
                if 'data' in part['body']:
                    data = part['body']['data']
                else:
                    att_id = part['body']['attachmentId']
                    att = service.users().messages().attachments().get(userId="me", messageId=message['id'], id=att_id).execute()
                    data = att['data']
                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                    
                file_path = os.path.join(save_path, part.get('filename'))

                with open(file_path, 'wb') as f:
                    f.write(file_data)

                print(f'Saved attachment: {file_path}')
        
    print("All attachments downloaded")

########################################################################################################################################


def get_dataframes(sent_to="", recieved_from="", after="", before=""):
    
    """
    
    Returns a dictionary with values as list of dataframes
    
    """
    
    msg = get_mails(sent_to, recieved_from, after, before)
    
    Scopes=['https://www.googleapis.com/auth/gmail.readonly']
        
    creds = Credentials.from_authorized_user_file(token, scopes=Scopes)
    
    service = build('gmail', 'v1', credentials=creds)
    
    dataframes={}
    
    for message in msg:
        
        ms = service.users().messages().get(userId="me", id=message['id']).execute()
            
        for part in ms['payload']['parts']:
            # Check if the part contains an attachment
            if part.get('filename'):
                # Decode the attachment data and save it to a file
                if 'data' in part['body']:
                    data = part['body']['data']
                else:
                    att_id = part['body']['attachmentId']
                    att = service.users().messages().attachments().get(userId="me", messageId=message['id'], id=att_id).execute()
                    data = att['data']
                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                filename=part.get('filename')
                if filename.endswith('.xlsx'):
                    df = pd.read_excel(BytesIO(file_data))
                elif filename.endswith('.csv'):
                    df = pd.read_csv(BytesIO(file_data))
                else:
                    df = None
                
                if df is not None:
                    try:
                        dataframes[filename].append(df)
                    except:
                        dataframes[filename]=df
            
    return dataframes
                    
download_mail_attachments(recieved_from="karthicknathan.l@exchange-data.in", after="26-05-2023")