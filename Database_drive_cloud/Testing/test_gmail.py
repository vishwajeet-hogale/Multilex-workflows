''' from Modules.gmail import get_mails,get_mail_messages


received_from = 'karthicknathan.l@exchange-data.in'
sent_to = 'techmultilex.gmail.com'
after_date = '1/5/2023'
before_date = '10/5/2023'
dict_file = get_mails(sent_to,received_from,after_date,before_date)
print(dict_file) '''

import os
import sys
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import re
from datetime import datetime
import base64
from io import BytesIO
import pandas as pd
import pprint


database = os.path.abspath(os.path.join(os.path.realpath(__file__), "..", ".."))

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
            file_path = os.path.join(save_dir, attachment['filename'])

            with open(file_path, 'wb') as f:
                f.write(file_data)

            print(f'Saved attachment: {file_path}')


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


if __name__ == '__main__':
    received_from = 'karthicknathan.l@exchange-data.in'
    sent_to = 'gitaseshadri2019@gmail.com'
    after_date = '1/5/2023'
    before_date = '10/5/2023'
    dict_file = get_mails(sent_to,received_from,after_date,before_date)
    pprint.pprint(dict_file)
    #df = pd.DataFrame(dict_file)
    #df_final = pd.DataFrame(df['payload'])
    #df_final.to_csv(r"D:\Prathima\mail_multiplex_file_final.csv")


