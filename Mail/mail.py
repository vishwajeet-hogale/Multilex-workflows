from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import date,datetime
from time import strftime 
import pymysql
import pandas as pd
import os
import sys
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64

mail_api = os.path.abspath(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

sys.path.append(mail_api)

from Database_drive_cloud.Luigi_Workflow.db import Update_token_gmail

sys.path.remove(mail_api)
update_token = Update_token_gmail()
update_token.run()
token_folder=os.path.join(mail_api, "Database_drive_cloud", "Luigi_Workflow", "Tokens", "gmail_tokens")

files = os.listdir(token_folder)

for file in files:
    if file.startswith('token_gmail_api'):
        token=os.path.join(token_folder, file)


def check_if_present(company):
  try:
    conn = setup_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT Companies FROM preipo.multilex WHERE Companies = '{company}'")
    data = cur.fetchone()
    cur.close()
    conn.close()
  except:
    print("Failed to get data from db")
    return True
  if data is not None:
    return True
  else:
    return False
def drop_countries(df):
  drop_index = []
  drop_countries = ['us', 'usa']
  try:
    for index in df.index:
      country = df['Country'][index].lower()
      # print(country)
      if country in drop_countries:
        drop_index.append(index)

    # print(drop_index)
    return df.drop(index=drop_index)
  except:
    print("Error occured in dropping usa records.")
def setup_connection():
    user = 'root'
    DB_PASSWORD = 'Mjklop@0987'
    DB_PORT = 3306
    passw = DB_PASSWORD
    host =  'localhost'
    port = DB_PORT
    database = 'preipo'
    conn = pymysql.connect(host=host,port=port,user=user,passwd=passw,db=database)
    return conn
def remove_duplicates(df):
  try:
    drop_columns = ['title', 'link']
    return df.drop_duplicates(subset=drop_columns)
  except:
    print("Error occured while dropping duplicate records.")



def sendemail(to,cc,body,subject,attachment_filepath):
    Scopes = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.compose', 'https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.modify']
    creds = Credentials.from_authorized_user_file(token, scopes=Scopes) #allow read only access

    service = build('gmail', 'v1', credentials=creds)
    message = MIMEMultipart()
    message['to'] = to
    message['cc'] = ', '.join(list(cc))
    message['subject'] = subject

    message.attach(MIMEText(body))
    
    if os.path.isfile(attachment_filepath):
            attachment = MIMEBase('application', 'octet-stream')
            with open(attachment_filepath, 'rb') as file:
                attachment.set_payload(file.read())
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_filepath))
            message.attach(attachment)
    else:
            print(f"Attachment file '{attachment_filepath}' not found.")

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    
    message = (service.users().messages().send(userId='me', body={'raw': raw_message})
                   .execute())
    print(f"Message sent. Message ID: {message['id']}")
    

    
    
    
def find_and_update_unique(df):
  drop_index = []
  try:
    for index in df.index:
      # check_if_present() is present in backend/database/db.py
      if check_if_present(df["Companies"][index]) is True:
        drop_index.append(index)
    return df.drop(index=drop_index)
  except:
    print("Failed to find and update unique records")
def run_feature12(df,to,cc,body,subject):
    curdate = date.today()
    curdate = curdate.strftime("%Y-%m-%d")
    # df = pd.read_csv(location)
    # df = drop_countries(df)
    df = remove_duplicates(df)
    df = find_and_update_unique(df)
    df.to_csv("PREIPO_Final_Report_"+curdate + ".xlsx")
    sendemail(to,cc,body,subject,"PREIPO_Final_Report"+curdate + ".csv")

if __name__ == "__main__":
  sendemail("sharikavallambatlapes@gmail.com",["vishwajeethogale307@gmail.com", "ujwalujwalc@gmail.com"],"Today's report","Trial RUn",r"C:\Users\ujwal\OneDrive\Desktop\Projects\Multilex-workflows\ReportMergeWF\Output\PREIPO_Final_Report_2023-01-27.csv")
  