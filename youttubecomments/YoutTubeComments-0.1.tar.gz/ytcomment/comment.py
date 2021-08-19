from uploads import Videoids

from auth import build

class Comment(Videoids):
    def __init__(self,client_id,client_secret,limit=100,commentLimit=4,channelId=None):
    
     super().__init__(channelId=channelId,client_secret=client_secret,client_id=client_id)
     self.limit=limit
     self.commentLimit=commentLimit
     
     
    def insert_comment(self,text,is_reply: bool =False,apiKey=None,numberOfCommentsToReply: int =1,numberofComments: int =1):
      self.getVideos(limit=1)
      
      parentIds={}
      for i in self.videos:

        channel_id=self.auth.videos().list(part='snippet',
                                           id=i).execute()
        channel_id=channel_id['items'][0].get('snippet').get("channelId")
        x=0
        if is_reply:
            if not apiKey:

             raise ValueError("Provide Your Google Developer Api Key!")
            else:
              results=self.auth2.commentThreads().list(
            part='snippets,replies',
            videoId=i
        ).execute()             
              for n in results['replies']['comments'] :
                 
                 if 'snippet' in n.keys():
                   if x== numberOfCommentsToReply:
                       break
                   reply=n['snippet']
                   parentIds.update({reply['videoId']: reply['parentId']})
                   x+=1
              for i in parentIds:
                  self.auth2.commentThreads().insert(part='snippet',body=
                                                     {
  "snippet": {
    "videoId": i,
    "textOriginal": text,
    "parentId": parentIds[i]
    
  }
}
                                                     )
                  print("Commented on videos", i)
        else:
         x=0
         if x ==      numberofComments:
             break
         self.auth.commentThreads().insert(
            part='snippet',
            body=dict(
                snippet=dict(channelId=channel_id,
                             videoId=i,
                             topLevelComment=dict(
                                 snippet=dict(
                                     textOriginal=text
                                 )
                             ))
            )
        ).execute()
         x+=1
         print("Commented On Video on: ",i)
        
a=Comment(channelId="UC6EICaldcyFSUUFBc4SHfzw",client_secret='ggXZe_9G1CIxq-s91X0GoBSo',client_id='338364909367-v60uad41kfsa50sa7j4sgchqhcjki0df.apps.googleusercontent.com')

a.insert_comment('....')