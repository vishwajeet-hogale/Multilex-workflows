import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
import base64
from difflib import SequenceMatcher
from google.auth.transport.requests import Request
import json
import numpy as np
import os

dir_path = os.path.dirname(os.path.realpath(__file__))


header={
    "Last Sent Date":[],
    "Issuer Name":[],
    "Country":[],
    "Security type":[],
    "Class": [],
    "Exchange Code":[],
    "Currency":[],
    "Issue value (in Million)":[],
    "IPO Date":[],
    "PRE-IPO URL":[]
}

def is_string_match(str1, str2, threshold=0.8):
    similarity_ratio = SequenceMatcher(None, str1, str2).ratio()
    return similarity_ratio >= threshold

def regenerated_token_creds(token, client, refresh, scopes=None):

    # load the client secrets file
    with open(client, 'r') as f:
        client_secrets = json.load(f)

    # load the refresh token from the file
    with open(refresh, 'r') as f:
        refresh_token = f.read().strip()

    # create the credentials object with the refresh token
    if scopes==None:
        creds = Credentials.from_authorized_user_info(
        info={
            'client_id': client_secrets['installed']['client_id'],
            'client_secret': client_secrets['installed']['client_secret'],
            'refresh_token': refresh_token,
        }
        )
        
    else:
        creds = Credentials.from_authorized_user_info(
            info={
                'client_id': client_secrets['installed']['client_id'],
                'client_secret': client_secrets['installed']['client_secret'],
                'refresh_token': refresh_token,
            },
            scopes=scopes,
        )
    # check if the credentials have expired
    if creds.expired:
        # refresh the access token
        creds.refresh(Request())

    # save the credentials to a JSON file
    with open(token, 'w') as f:
        f.write(creds.to_json())
    
    return creds

def gmail_multilex(dir_path):
    #Enter the path address where token.json file is stored
    path_to_token1 = os.path.join(dir_path, "token_gmail_api.json")
    path_to_refresh_token=os.path.join(dir_path, "gmail_refresh_token.txt")
    path_to_client_token=os.path.join(dir_path, "client_secret_gmail.json")
    read_mails_from = "karthicknathan.l@exchange-data.in"

    today = datetime.datetime.now()

    start_date = (today).strftime('%Y/%m/%d') #included for searching
    end_date = (today+datetime.timedelta(days= 1)).strftime('%Y/%m/%d') #not included while searching

    # Creation of query string
    query=f"from:{read_mails_from} after:{start_date} before:{end_date}"
    
    Scopes=['https://www.googleapis.com/auth/gmail.readonly']

    # Create a Gmail API client using OAuth2 credentials
    creds = Credentials.from_authorized_user_file(path_to_token1, scopes=Scopes) #allow read only access
    if creds.expired:
        creds=regenerated_token_creds(path_to_token1, path_to_client_token, path_to_refresh_token, Scopes)
    
    service = build('gmail', 'v1', credentials=creds)
    
    # Search for the email with the given search query
    result = service.users().messages().list(userId='me', q=query).execute()
    
    """
    # To read the text part of the mail recieved from the particular user
    
    messages = result.get('messages', [])
    print(len(messages))
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        print(msg['snippet'])
    """
    
    messages = result.get('messages')
    li=[]
    if messages:
        for message in messages:
            msg = service.users().messages().get(userId="me", id=message['id']).execute()
            
            for part in msg['payload']['parts']:
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
                    
                    if "Data_Received" not in str(part['filename']) and "IPO" in str(part['filename']):
                        li.append([pd.read_excel(file_data), str(part['filename'])])
                   
    return li




def update_database(dir_path):
    
    gmail_dfs=gmail_multilex(dir_path)
    if len(gmail_dfs)==0:
        return
    
    token_directory=os.path.join(dir_path, "token_drive_api.json")
    drive_refresh_token=os.path.join(dir_path, "drive_refresh_token.txt")
    drive_client=os.path.join(dir_path, "client_secret_drive.json")
    
    
    # Set up the Drive API client
    creds = Credentials.from_authorized_user_file(token_directory)
    if creds.expired:
        creds=regenerated_token_creds(token_directory, drive_client, drive_refresh_token)
    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)
    

    # Define the name of the folder where the file is located
    folder_name = 'Database'
    file_name = 'Database'

    # Search for the folder by name
    folder_query = "mimeType='application/vnd.google-apps.folder' and trashed = false and name='"+ folder_name + "'"
    folder_results = drive_service.files().list(q=folder_query,fields="nextPageToken, files(id, name)").execute()
    folder_items = folder_results.get('files', [])

    # If the folder is not found, print an error message and exit
    if not folder_items:
        print('Folder not found: ' + folder_name)
        exit()

    # Get the ID of the folder
    folder_id = folder_items[0]['id']

    # Search for the XLSX file by name and folder ID
    file_query = "mimeType='application/vnd.google-apps.spreadsheet' and trashed = false and name='"+ file_name + "' and parents in '"+ folder_id +"'"
    file_results = drive_service.files().list(q=file_query,fields="nextPageToken, files(id, name)").execute()
    file_items = file_results.get('files', [])
    

    worksheet_name = 'Sheet1'

    spreadsheet_id = file_items[0]['id']

    range_name = f"{worksheet_name}!A:Z"
    

    # Retrieve the current data range
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()
    current_data = result.get('values', [])

    # Convert the current data to a pandas dataframe

    df = pd.DataFrame(current_data[1:], columns=current_data[0])
    
    
    for files in gmail_dfs:
        df_local=files[0]
        date_substring = files[1].split("_")[1]
        datetime_obj = datetime.datetime.strptime(date_substring, "%Y%m%d")
        datetime_obj = datetime_obj.strftime('%d-%m-%Y')
        for index, value in df_local["Issuer Name"].iteritems():
            flag=0
            for index_global, value_global in df["Issuer Name"].iteritems():
                value=value.lower()
                value_global=value_global.lower()
                if (value in value_global) or (value_global in value) or is_string_match(value, value_global):
                    df.loc[index_global, "Last Sent Date"]=datetime_obj
                    for column_name, column_data in df.iteritems():
                        if column_name in df_local.columns and not pd.isnull(df_local.loc[index, column_name]):
                            df.loc[index_global, column_name]=df_local.loc[index, column_name]
                            flag=1
            if flag==0:
                x=header.copy()
                x["Last Sent Date"]=datetime_obj
                for i in x.keys():
                    if i in df_local.columns and not pd.isnull(df_local.loc[index, i]):
                        x[i]=df_local.loc[index, i]
                df = df.append(x, ignore_index=True)
    
    
    df['Last Sent Date'] = pd.to_datetime(df['Last Sent Date'], format='%d-%m-%Y')

    # sort dataframe by date column in descending order
    df = df.sort_values(by='Last Sent Date', ascending=False, ignore_index=True)

    # convert date column back to string form
    df['Last Sent Date'] = df['Last Sent Date'].dt.strftime('%d-%m-%Y')
    
    
    num_rows = df.shape[0]
    range_ = f"{worksheet_name}!A1:Z{num_rows+1}"

    # Convert the updated data to a list of lists for the Sheets API
    updated_data = df.replace(np.nan, '').astype(str).values.tolist()

    # Define the request to update the data in the sheet
    request_body = {
        'range': range_,
        'values': [df.columns.values.tolist()] + updated_data
    }


    request = sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_,
        valueInputOption='USER_ENTERED',
        body=request_body
    )

    # Execute the request to update the data in the sheet
    response = request.execute()        
    
    
    
    
    

if __name__=='__main__':
    today = datetime.datetime.now()
    if today.weekday() < 5:
        update_database(dir_path)