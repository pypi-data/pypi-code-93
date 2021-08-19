import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

from auth import Auth

   
class Videoids(Auth):
 def __init__(self,client_secret,client_id,channelId=None):
     super().__init__(client_id=client_id,client_secret=client_secret)
     self.auth=self.auth
     self.channelid=channelId
     
 def getSubscriptions(self):
   auth=self.auth
    
   subs=[]
   r=auth.subscriptions().list(
    part="snippet",
    mine=True,
    maxResults=1,
)
   if self.channelid:
         subs.append(self.channelid)
   else:
         
     for i in r.execute()['items']:
        #  print(i)
        #  a=open('a.json','w')
        #  json.dump(i,a)
         if "snippet" in i.keys():
          subs.append(i['snippet'].get('resourceId').get("channelId"))
   videos=[]
   uploads=[]
   for i in subs:
     r=auth.channels().list(
      part="contentDetails",
      id=i,
      ).execute()
      
      # maxResults=1,
     for i in r['items']:
        if "contentDetails" in i.keys():
            uploads.append(i['contentDetails'].get('relatedPlaylists').get("uploads"))
   
   self.uploads=uploads
 def getVideos(self,limit = 100):
     self.getSubscriptions()
     auth=self.auth
     videoids=[]
     a=0
     for  i in self.uploads:
      r=auth.playlistItems().list(part="contentDetails,snippet",playlistId=i,maxResults=limit).execute()
      for i in r['items']:
            if 'contentDetails' in i.keys():
             print(i['contentDetails'])     
             videoids.append(i['contentDetails'].get("videoId"))
     self.videos=videoids
     
     
     