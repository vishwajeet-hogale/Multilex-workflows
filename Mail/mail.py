import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import date,datetime
from time import strftime
from decouple import config 
import pymysql
import pandas as pd
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
    password = config('PASSWORD')
    fromaddr = config('EMAIL')
    toaddr = [to] + cc 
    
    # instance of MIMEMultipart
    msg = MIMEMultipart()
    
    # storing the senders email address  
    msg['From'] = fromaddr
    
    # storing the receivers email address 
    msg['To'] = to
    # msg["Cc"] = cc
    # msg["body"] = body
    # storing the subject 
    msg['Subject'] = subject
    # body = "Hello , this mail was sent from python for tetsing purposes."
    
    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))
    
    # open the file to be sent 
    filename = attachment_filepath
    attachment = open(attachment_filepath, "rb")
    
    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')
    
    # To change the payload into encoded form
    p.set_payload((attachment).read())
    
    # encode into base64
    encoders.encode_base64(p)
    
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    
    # attach the instance 'p' to instance 'msg'
    msg.attach(p)
    
    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)
    
    # start TLS for security
    s.starttls()
    # Authentication
    s.login(fromaddr, password)
    
    # Converts the Multipart msg into a string
    text = msg.as_string()
    
    # sending the mail
    s.sendmail(fromaddr, toaddr, text)
    print("Message sent")
    
    # terminating the session
    s.quit()
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
  sendemail("sharikavallambatlapes@gmail.com","vishwajeethogale307@gmail.com","Today's report","Report for 20th June","Cleaned_csv.csv")
    