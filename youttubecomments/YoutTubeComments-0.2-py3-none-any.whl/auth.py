
from googleapiclient.discovery import build


import os
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
from google.auth.transport.requests import Request
import json

credential = None
key='AIzaSyD3VRv35apEiqasQ0eGrXk9IptgVitj-gQ'

class BuildClient:
    def __init__(self,client_id,client_secret):
        
      import json
      
      a=open("client_secrets.json")
      a=json.load(a)
      b=a['web']
      b.pop('client_id')
      # b.pop('project_id')
      b.pop("client_secret")
      b
      b['client_id'] = client_id
      # b['project_id'] = project_id
      b['client_secret'] = client_secret
      b['redirect_urls'] = ["http://localhost:8080/"]
      
      z=open("client_secrets.json",'w')
      z.truncate(0)
      json.dump(a,z)


if os.path.exists("token.pickle"):
    with open("token.pickle",'rb') as token:
        credential=pickle.load(token)


if not credential or not credential.valid:
    if credential and credential.expired and credential.refresh_token:
        print("Refreshing your token...")
        credential.refresh(Request())
    else:
        
       flow=InstalledAppFlow.from_client_secrets_file(
           "client_secrets.json",
           scopes=['https://www.googleapis.com/auth/youtube',"https://www.googleapis.com/auth/youtube.force-ssl"]
       )
       
       flow.run_local_server(port=8080,prompt="consent")
       credential = flow.credentials
       if not os.path.exists("token.pickle"):
        open("token.pickle", "a")
       print("Saving credentials for future use..")
       with open("token.pickle",'wb') as f:
           pickle.dump(credential,f) 



class Auth(BuildClient):
 def __init__(self,client_id,client_secret):
  print("Setting up Client....")
  super().__init__(client_id=client_id,client_secret=client_secret)
     
  self.auth=build("youtube","v3",credentials=credential)
   
   