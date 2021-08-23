import tweepy

def get_zeroscore(api,usr_id):
  try:
    usr_main=api.get_user(usr_id)
    usr_followers_count=usr_main.followers_count
    usr_friends_count=usr_main.friends_count
    return float(usr_followers_count)/float(usr_friends_count+1)
  except:
    return 0

def get_multilist(api,username):
  c = tweepy.Cursor(api.followers_ids, id=username)
  ids = []
  for page in c.pages():
   ids.extend(page)  
  return ids

def get_multiscore(api,list_ids,degree_score):
  if degree_score==1:
    net_score=0.0
    for elem in list_ids:
      net_score=net_score+get_zeroscore(api,elem)
    net_score=float(net_score)/len(list_ids)
    return net_score
  else:
    degree_score=degree_score-1
    tmp_list=[0]*len(list_ids)
    for elem_idx in range(len(list_ids)):
      new_list_ids=get_multilist(api,list_ids[elem_idx])
      tmp_list[elem_idx]=get_multiscore(api,new_list_ids,degree_score)
    fin_val=0.0
    for elem in tmp_list:
      fin_val=fin_val+elem
    fin_val=float(fin_val)/float(len(tmp_list))    
    return fin_val

def get_score(api,username,degree_score):
  if degree_score<=0:
    return get_zeroscore(api,username)
  else:
    list_ids=get_multilist(api,username)
    return get_multiscore(api,list_ids,degree_score)

def social_score(consumer_key,consumer_secret,access_token,access_token_secret,username,degree_score):
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)
  api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)
  score=get_score(api,username,degree_score)
  usr_main=api.get_user(username)
  usr_followers_count=usr_main.followers_count
  usr_friends_count=usr_main.friends_count
  delta=float(usr_followers_count)/float(usr_friends_count+1)
  final_score=score*(delta)
  return final_score
