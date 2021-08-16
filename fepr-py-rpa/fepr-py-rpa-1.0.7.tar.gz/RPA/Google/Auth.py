from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os


def auth(client_secrets_json_path):
    """GCPで各種API操作するために必要なトークンをtoken.pickleに保存する。

    Args:
        client_secrets_json_path (str): OAuthクライアントjsonのファイルパス
        
    """
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets.readonly', 
        'https://www.googleapis.com/auth/spreadsheets', 
        'https://www.googleapis.com/auth/youtube', 
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.metadata.readonly', 
        'https://www.googleapis.com/auth/drive.file', 
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.labels',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/script.deployments', 
        'https://www.googleapis.com/auth/script.deployments.readonly', 
        'https://www.googleapis.com/auth/script.metrics', 
        'https://www.googleapis.com/auth/script.processes', 
        'https://www.googleapis.com/auth/script.projects', 
        'https://www.googleapis.com/auth/script.projects.readonly', 
        ]
    cred = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            cred = pickle.load(token)
    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_json_path, scopes)
            cred = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(cred, token)