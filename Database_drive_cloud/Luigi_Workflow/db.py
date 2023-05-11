import luigi
import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime


class Update_token_drive(luigi.Task):
    
    directory=os.path.join(os.path.join(os.getcwd(), 'Tokens'), 'drive_tokens')
    
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
    
    directory=os.path.join(os.path.join(os.getcwd(), 'Tokens'), 'gmail_tokens')
    
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
        print("abc")