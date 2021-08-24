import os.path
from pathlib import Path
from . import settings

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

class Auth:
    def login(self):
        creds = self.verify_token()
        
        curr_dir = os.getcwd()
        os.chdir(os.path.expanduser('~') + '/.comcomdrive')

        if not creds:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', settings.get_scopes())
                creds = flow.run_console()

                # save the credentials        
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                print('login success.')
            except:
                print('login failed.')
        else:
            print('already logged in')

        os.chdir(curr_dir)

    def verify_token(self):
        creds = None
        
        curr_dir = os.getcwd()
        os.chdir(os.path.expanduser('~') + '/.comcomdrive')

        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', settings.get_scopes())

        if creds and not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())   

        os.chdir(curr_dir)
        return creds
