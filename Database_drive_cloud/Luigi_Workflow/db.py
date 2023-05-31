import luigi
import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
import pandas as pd
import base64
from io import BytesIO
import time


def update_refresh_token_gmail(): 
    
    """
    Use this only when you get this error: "raise exceptions.RefreshError(google.auth.exceptions.RefreshError: ('invalid_grant: Bad Request', {'error': 'invalid_grant', 'error_description': 'Bad Request'})"
    Also make sure you give access by visiting the link.
    This error occurs when refresh token has expired, which shouldn't happen.
    """
    
    directory=os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)) , 'Tokens'), 'gmail_tokens')
    
    scopes = ['https://www.googleapis.com/auth/gmail.readonly']

    # Create the flow with offline access type
    flow = InstalledAppFlow.from_client_secrets_file(os.path.join(directory, 'client_secret_gmail.json'), scopes=scopes)

    # Start the authorization flow
    credentials = flow.run_local_server(access_type='offline')

    # Store the refresh token securely for future use
    refresh_token = credentials.refresh_token
    with open(os.path.join(directory, 'gmail_refresh_token.txt'), 'w') as f:
        f.write(refresh_token)
        
def update_refresh_token_drive(): 
    
    """
    Use this only when you get this error: "raise exceptions.RefreshError(google.auth.exceptions.RefreshError: ('invalid_grant: Bad Request', {'error': 'invalid_grant', 'error_description': 'Bad Request'})"
    Also make sure you give access by visiting the link.
    This error occurs when refresh token has expired, which shouldn't happen.
    """
    
    scopes = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/spreadsheets'
    ]
    
    directory=os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)) , 'Tokens'), 'drive_tokens')

    # Create the flow with offline access type
    flow = InstalledAppFlow.from_client_secrets_file(os.path.join(directory, 'client_secret_drive.json'), scopes=scopes)

    # Start the authorization flow
    credentials = flow.run_local_server(access_type='offline')

    # Store the refresh token securely for future use
    refresh_token = credentials.refresh_token
    with open(os.path.join(directory, 'drive_refresh_token.txt'), 'w') as f:
        f.write(refresh_token)

class Update_token_drive(luigi.Task):
    
    directory=os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)) , 'Tokens'), 'drive_tokens')
    
    def output(self):
        
        name='token_drive_api'+datetime.datetime.now().strftime('%d-%m-%Y_%H')+'.json'
        
        return luigi.LocalTarget(str(os.path.join(self.directory, name)))
    
    def run(self):
        with open(os.path.join(self.directory, 'client_secret_drive.json'), 'r') as f:
            client_secrets = json.load(f)

        # load the refresh token from the file
        with open(os.path.join(self.directory, 'drive_refresh_token.txt'), 'r') as f:
            refresh_token = f.read().strip()

        # create the credentials object with the refresh token
        creds = Credentials.from_authorized_user_info(
        info={
            'client_id': client_secrets['installed']['client_id'],
            'client_secret': client_secrets['installed']['client_secret'],
            'refresh_token': refresh_token,
        }
        )
        
        # check if the credentials have expired
        if creds.expired:
            # refresh the access token
            creds.refresh(Request())
            
        # Get a list of all files in the folder
        files = os.listdir(self.directory)

        # Loop through the files and delete files that start with the specified prefix
        for file in files:
            if file.startswith('token_drive_api'):
                file_path = os.path.join(self.directory, file)
                os.remove(file_path)

        # save the credentials to a JSON file
        with self.output().open('w') as f:
            f.write(creds.to_json())



class Update_token_gmail(luigi.Task):
    
    directory=os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Tokens'), 'gmail_tokens')
    
    def output(self):
        
        name='token_gmail_api'+datetime.datetime.now().strftime('%d-%m-%Y_%H')+'.json'
        
        return luigi.LocalTarget(os.path.join(self.directory, name))
    
    def run(self):
        # load the client secrets file
        with open(os.path.join(self.directory, 'client_secret_gmail.json'), 'r') as f:
            client_secrets = json.load(f)

        # load the refresh token from the file
        with open(os.path.join(self.directory, 'gmail_refresh_token.txt'), 'r') as f:
            refresh_token = f.read().strip()
        
        creds = Credentials.from_authorized_user_info(
            info={
                'client_id': client_secrets['installed']['client_id'],
                'client_secret': client_secrets['installed']['client_secret'],
                'refresh_token': refresh_token,
            },
            scopes=['https://www.googleapis.com/auth/gmail.readonly']
        )
        
        # check if the credentials have expired
        if creds.expired:
            # refresh the access token
            creds.refresh(Request())
            
        # Get a list of all files in the folder
        files = os.listdir(self.directory)

        # Loop through the files and delete files that start with the specified prefix
        for file in files:
            if file.startswith('token_gmail_api'):
                file_path = os.path.join(self.directory, file)
                os.remove(file_path)

        # save the credentials to a JSON file
        with self.output().open('w') as f:
            f.write(creds.to_json())


        

class Database(luigi.Task):
    def requires(self):
        return [Update_token_drive(), Update_token_gmail()]
    
    def run(self):
        after= datetime.date.today().strftime("%Y/%m/%d")
        before=(datetime.date.today()+datetime.timedelta(days= 1)).strftime("%Y/%m/%d")
        
        gmail_token=self.input()[1].path
        drive_token=self.input()[0].path
        
        def get_mails(sent_to="", recieved_from="", after="", before=""):
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
                query += "after:" + after
                flag=1
            if before:
                if flag==1:
                    query += " "
                query += "before:" + before
            
            Scopes=['https://www.googleapis.com/auth/gmail.readonly']

            # Create a Gmail API client using OAuth2 credentials
            creds = Credentials.from_authorized_user_file(gmail_token, scopes=Scopes) #allow read only access
            
            service = build('gmail', 'v1', credentials=creds)
            
            # Search for the email with the given search query
            result = service.users().messages().list(userId='me', q=query).execute()
            
            messages = result.get('messages')
            data=[]
            if messages:
                for message in messages:
                    msg = service.users().messages().get(userId="me", id=message['id']).execute()
                    data.append(msg)
            return data
        
        def get_dataframes(sent_to="", recieved_from="", after="", before=""):
    
            
            msg = get_mails(sent_to, recieved_from, after, before)
            
            Scopes=['https://www.googleapis.com/auth/gmail.readonly']
                
            creds = Credentials.from_authorized_user_file(gmail_token, scopes=Scopes)
            
            service = build('gmail', 'v1', credentials=creds)
            
            dataframes={}
            
            for message in msg:
                
                ms = service.users().messages().get(userId="me", id=message['id']).execute()
                
                headers = ms['payload']['headers']
                for header in headers:
                    if header['name'] == 'Date':
                        date_str = header['value']
                        date = datetime.datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z").strftime("%d-%m-%Y")
                        
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
                                dataframes[filename].append([df, date])
                            except:
                                dataframes[filename]=[df, date]
                    
            return dataframes
        
        def get_sheet_id(folder_name, file_name):
            creds = Credentials.from_authorized_user_file(drive_token)
            drive_service = build('drive', 'v3', credentials=creds)
            
            
            
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
            
            
            return file_items[0]['id']
            

            
        
        def Database_of_files_recieved_accepted():
                
                dataframes=get_dataframes(recieved_from="karthicknathan.l@exchange-data.in", after=after, before=before)
                
                creds = Credentials.from_authorized_user_file(drive_token)
                sheets_service = build('sheets', 'v4', credentials=creds)
                

                folder_name = 'Database'
                file_name = 'Database_Of_Files_Recieved_Accepted'


                worksheet_name = 'Sheet1'

                spreadsheet_id = get_sheet_id(folder_name=folder_name, file_name=file_name)

                range_name = f"{worksheet_name}!A:Z"
                
                for key in reversed(dataframes.keys()):
                    if "Data" not in key:
                        date = dataframes[key][1]
                        df = dataframes[key][0]
                        
                        num_rows = df.shape[0]
                        values = [[date] + [None] * (df.shape[1] - 1)] * num_rows
                        
                        num_rows_to_insert = num_rows

                        insert_index = 1
                        
                        # Get the sheet ID by name
                        sheets = sheets_service.spreadsheets()
                        sheet_metadata = sheets.get(spreadsheetId=spreadsheet_id).execute()
                        sheets_list = sheet_metadata.get('sheets', [])
                        sheet_id = sheets_list[0]['properties']['sheetId']  # Assuming Sheet1 is the first sheet (index: 0)
                        
                        requests = [
                            {
                                'insertRange': {
                                    'range': {
                                        'sheetId': sheet_id,
                                        'startRowIndex': insert_index,
                                        'endRowIndex': insert_index + num_rows_to_insert
                                    },
                                    'shiftDimension': 'ROWS'
                                }
                            }
                        ]

                        # Execute the batch update request
                        sheets_service.spreadsheets().batchUpdate(
                            spreadsheetId=spreadsheet_id,
                            body={'requests': requests}
                        ).execute()
                        
                        range_name = f"{worksheet_name}!A2:A{num_rows + 1}"
                        
                        request_body = {
                                        'valueInputOption': 'RAW',
                                        'data': [{
                                            'range': range_name,
                                            'values': values
                                        }]
                                    }
                        sheets_service.spreadsheets().values().batchUpdate(
                                    spreadsheetId=spreadsheet_id,
                                    body=request_body
                                ).execute()
                        
                        

                        # Build the request body to merge cells
                        merge_request_body = {
                            'requests': [{
                                'mergeCells': {
                                    'range': {
                                        'sheetId': sheet_id,
                                        'startRowIndex': 1,  # Start from the second row (index: 1)
                                        'endRowIndex': num_rows + 1,  # Include all rows (including header)
                                        'startColumnIndex': 0,  # Column A (index: 0)
                                        'endColumnIndex': 1  # Column A (index: 1)
                                    },
                                    'mergeType': 'MERGE_ALL'
                                }
                            }]
                        }

                        # Send the request to merge cells in the received_date column
                        sheets_service.spreadsheets().batchUpdate(
                            spreadsheetId=spreadsheet_id,
                            body=merge_request_body
                        ).execute()
                        
                        align_request_body = {
                                'requests': [{
                                    'updateCells': {
                                        'rows': [
                                            {
                                                'values': [
                                                    {
                                                        'userEnteredFormat': {
                                                            'verticalAlignment': 'MIDDLE'
                                                        }
                                                    }
                                                ]
                                            }
                                        ],
                                        'range': {
                                            'sheetId': sheet_id,
                                            'startRowIndex': 1,
                                            'endRowIndex': num_rows + 1,
                                            'startColumnIndex': 0,
                                            'endColumnIndex': 1
                                        },
                                        'fields': 'userEnteredFormat.verticalAlignment'
                                    }
                                }]
                            }
                        
                        sheets_service.spreadsheets().batchUpdate(
                            spreadsheetId=spreadsheet_id,
                            body=align_request_body
                        ).execute()

                        # Set the border color to dark gray
                        border_color = {
                            'red': 0.2,
                            'green': 0.2,
                            'blue': 0.2
                        }

                        # Build the request body to update the border format
                        border_request_body = {
                            'requests': [{
                                'updateBorders': {
                                    'range': {
                                        'sheetId': sheet_id,
                                        'startRowIndex': 1,
                                        'endRowIndex': num_rows + 1,
                                        'startColumnIndex': 0,
                                        'endColumnIndex': 16
                                    },
                                    'top': {
                                        'style': 'SOLID',
                                        'width': 2,
                                        'color': border_color
                                    },
                                    'bottom': {
                                        'style': 'SOLID',
                                        'width': 2,
                                        'color': border_color
                                    },
                                    'left': {
                                        'style': 'SOLID',
                                        'width': 2,
                                        'color': border_color
                                    },
                                    'right': {
                                        'style': 'SOLID',
                                        'width': 2,
                                        'color': border_color
                                    },
                                }
                            }]
                        }

                        # Send the request to update the border format
                        sheets_service.spreadsheets().batchUpdate(
                            spreadsheetId=spreadsheet_id,
                            body=border_request_body
                        ).execute()
                        
                        
  
                        values=[[str(cell) if pd.notnull(cell) else '' for cell in row] for row in df.values]
                        range_name = f"{worksheet_name}!B2:{chr(ord('B') + df.shape[1] - 1)}{num_rows + 1}"
                        
                        request_body = {
                                        'valueInputOption': 'RAW',
                                        'data': [{
                                            'range': range_name,
                                            'values': values
                                        }]
                                    }
                        sheets_service.spreadsheets().values().batchUpdate(
                                    spreadsheetId=spreadsheet_id,
                                    body=request_body
                                ).execute()
                        time.sleep(6.1)
                    
        
        
        
        def Database_Of_Files_Recieved():
                dataframes=get_dataframes(recieved_from="karthicknathan.l@exchange-data.in", after="2023/02/21", before=before)
                
                creds = Credentials.from_authorized_user_file(drive_token)
                sheets_service = build('sheets', 'v4', credentials=creds)
                

                folder_name = 'Database'
                file_name = 'Database_Of_Files_Recieved'


                worksheet_name = 'Sheet1'

                spreadsheet_id = get_sheet_id(folder_name=folder_name, file_name=file_name)

                range_name = f"{worksheet_name}!A:AW"
                
                for key in reversed(dataframes.keys()):
                    if "Data" in key:
                        date = dataframes[key][1]
                        df = dataframes[key][0]
                        
                        num_rows = df.shape[0]
                        values = [[date] + [None] * (df.shape[1] - 1)] * num_rows
                        
                        num_rows_to_insert = num_rows

                        insert_index = 1
                        
                        # Get the sheet ID by name
                        sheets = sheets_service.spreadsheets()
                        sheet_metadata = sheets.get(spreadsheetId=spreadsheet_id).execute()
                        sheets_list = sheet_metadata.get('sheets', [])
                        sheet_id = sheets_list[0]['properties']['sheetId']  # Assuming Sheet1 is the first sheet (index: 0)
                        
                        requests = [
                            {
                                'insertRange': {
                                    'range': {
                                        'sheetId': sheet_id,
                                        'startRowIndex': insert_index,
                                        'endRowIndex': insert_index + num_rows_to_insert
                                    },
                                    'shiftDimension': 'ROWS'
                                }
                            }
                        ]

                        # Execute the batch update request
                        sheets_service.spreadsheets().batchUpdate(
                            spreadsheetId=spreadsheet_id,
                            body={'requests': requests}
                        ).execute()
                        
                        range_name = f"{worksheet_name}!A2:A{num_rows + 1}"
                        
                        request_body = {
                                        'valueInputOption': 'RAW',
                                        'data': [{
                                            'range': range_name,
                                            'values': values
                                        }]
                                    }
                        sheets_service.spreadsheets().values().batchUpdate(
                                    spreadsheetId=spreadsheet_id,
                                    body=request_body
                                ).execute()
                        
                        

                        # Build the request body to merge cells
                        merge_request_body = {
                            'requests': [{
                                'mergeCells': {
                                    'range': {
                                        'sheetId': sheet_id,
                                        'startRowIndex': 1,  # Start from the second row (index: 1)
                                        'endRowIndex': num_rows + 1,  # Include all rows (including header)
                                        'startColumnIndex': 0,  # Column A (index: 0)
                                        'endColumnIndex': 1  # Column A (index: 1)
                                    },
                                    'mergeType': 'MERGE_ALL'
                                }
                            }]
                        }

                        # Send the request to merge cells in the received_date column
                        sheets_service.spreadsheets().batchUpdate(
                            spreadsheetId=spreadsheet_id,
                            body=merge_request_body
                        ).execute()
                        
                        align_request_body = {
                                'requests': [{
                                    'updateCells': {
                                        'rows': [
                                            {
                                                'values': [
                                                    {
                                                        'userEnteredFormat': {
                                                            'verticalAlignment': 'MIDDLE'
                                                        }
                                                    }
                                                ]
                                            }
                                        ],
                                        'range': {
                                            'sheetId': sheet_id,
                                            'startRowIndex': 1,
                                            'endRowIndex': num_rows + 1,
                                            'startColumnIndex': 0,
                                            'endColumnIndex': 1
                                        },
                                        'fields': 'userEnteredFormat.verticalAlignment'
                                    }
                                }]
                            }
                        
                        sheets_service.spreadsheets().batchUpdate(
                            spreadsheetId=spreadsheet_id,
                            body=align_request_body
                        ).execute()

                        # Set the border color to dark gray
                        border_color = {
                            'red': 0.2,
                            'green': 0.2,
                            'blue': 0.2
                        }

                        # Build the request body to update the border format
                        border_request_body = {
                            'requests': [{
                                'updateBorders': {
                                    'range': {
                                        'sheetId': sheet_id,
                                        'startRowIndex': 1,
                                        'endRowIndex': num_rows + 1,
                                        'startColumnIndex': 0,
                                        'endColumnIndex': 48
                                    },
                                    'top': {
                                        'style': 'SOLID',
                                        'width': 2,
                                        'color': border_color
                                    },
                                    'bottom': {
                                        'style': 'SOLID',
                                        'width': 2,
                                        'color': border_color
                                    },
                                    'left': {
                                        'style': 'SOLID',
                                        'width': 2,
                                        'color': border_color
                                    },
                                    'right': {
                                        'style': 'SOLID',
                                        'width': 2,
                                        'color': border_color
                                    },
                                }
                            }]
                        }

                        # Send the request to update the border format
                        sheets_service.spreadsheets().batchUpdate(
                            spreadsheetId=spreadsheet_id,
                            body=border_request_body
                        ).execute()
                        
                        
  
                        values=[[str(cell) if pd.notnull(cell) else '' for cell in row] for row in df.values]
                        range_name = f"{worksheet_name}!B2:BA{num_rows + 1}"
                        
                        request_body = {
                                        'valueInputOption': 'RAW',
                                        'data': [{
                                            'range': range_name,
                                            'values': values
                                        }]
                                    }
                        sheets_service.spreadsheets().values().batchUpdate(
                                    spreadsheetId=spreadsheet_id,
                                    body=request_body
                                ).execute()
                        time.sleep(6.1)
                        
        Database_of_files_recieved_accepted()
        Database_Of_Files_Recieved()