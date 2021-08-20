from __future__ import print_function


import pickle, io
import os.path
import copy
from py3toolbox import fs_tools   as fs_tools
from py3toolbox import helper     as helper




# ====================================================================
#
# This google drive api wrapper is based on Goodgle Drive API v3
#
# ====================================================================

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request



SCOPES          = ['https://www.googleapis.com/auth/drive']
TOKEN_PICKLE    = 'gdrive.<ID>.token.pkl'
CHUNK_SIZE      = 100*1024*1024


class Gdrive():
  def __init__(self, cred_file=None, cred_id=1, page_size=100):
    self.cred_file          = cred_file
    self.cred_id            = str(cred_id)
    self.token_pickle       = TOKEN_PICKLE.replace('<ID>', self.cred_id)
    self.page_size          = page_size
    self.meta_cache         = None
    self.gdrive_service_v3  = None
    self.auth_cred()
    self.init_gdrive()
    
    pass
    
    
    
  # ====================================================
  #
  # authenticate login
  #
  # ====================================================    
  def auth_cred(self):
    """
      authenticate user credential
    
    
    """
    
    creds = None
    if os.path.exists(self.token_pickle):
      with open(self.token_pickle, 'rb') as token:
        creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(self.cred_file, SCOPES)
        creds = flow.run_local_server(port=0)
      
      # Save the credentials for the next run
      with open(self.token_pickle, 'wb') as token:
        pickle.dump(creds, token)

    assert creds is not None, "Gdrive credential error."
    
    self.gdrive_service_v3 = build('drive', 'v3', credentials=creds)
    
    pass
    


  # ====================================================
  #
  # init gdrive
  #
  # ====================================================    
    
  def init_gdrive(self):
    self.root_id  = self.gdrive_service_v3.files().get(fileId="root", fields=("id")).execute()['id']  
    pass
    

  # ====================================================
  #
  # Parse full names of the given name (path)
  #
  # ====================================================
  
  def _parse_full_name (self, name):
  
    if name is None:
      return []
      
    name  = name.replace('\\','/').replace('//','/')

    while name[:1] == '/' : 
      name = name[1:]
      
    names = name.split('/')
    return names    


  # ====================================================
  #
  # Apply operation task on cache hierachy
  #
  # ====================================================

  def _get_hierchy(self, tree_data, id, operation="list" ) :
    id_collections = []
    tree_data_result = {}

    # find out the impacted id list
    while True:
      v = len(id_collections)
      for k in tree_data.keys() :
        r = tree_data[k]
        parent_id = r['parents'][0]
        if k == id and k not in id_collections:
          id_collections.append(k)
          if (parent_id != self.root_id) and parent_id not in id_collections :
            id_collections.append(parent_id)  
          
        if parent_id in id_collections and k not in id_collections:
          id_collections.append(k)
          
      id_collections = list(set(id_collections))
      
      if v == len(id_collections) :
        break;
    
    
    # execute the operation task
    if operation == "list" :
      for k in tree_data.keys() :
        r = tree_data[k] 
        if k in id_collections:
          tree_data_result[k] = r
     
     
    elif operation == "remove":
      tree_data_result = copy.deepcopy(tree_data)
      for k in tree_data.keys() :
        if k in id_collections:
          tree_data_result.pop(k, None)
  
    return id_collections,tree_data_result
      

  # ====================================================
  #
  #  download files from gdrive and verify MD5
  #
  # ====================================================
  
  def download(self, id, localname, verify=False):
    download_request = self.gdrive_service_v3.files().get_media(fileId=id)
    file_handler = io.FileIO(localname, mode='wb')
    downloader = MediaIoBaseDownload(fd=file_handler, request=download_request, chunksize=CHUNK_SIZE)
    done = False
    try :
      while done is False:
        status, done = downloader.next_chunk()
    except Exception as err:
      return False, "download:" + str(err)

    if verify :
      src_md5 = self.get_meta(id=id)['md5Checksum']
      dst_md5 = fs_tools.get_md5(localname)
      if src_md5==dst_md5:
        return True, "success"
      else:
        return False, "Downloaded, but verification failed. src_md5=" + src_md5 + ", dst_md5=" + dst_md5
    else:
      return True, "success"
    


  def upload(self, id, localname, verify=False):
    
    src_md5 = None
    dst_md5 = None
    
    assert fs_tools.exists(localname), "local file doesn't exist"
    
    
    if verify:
      src_md5 = self.get_meta(id=id)['md5Checksum']
      dst_md5 = fs_tools.get_md5(localname)
      if src_md5 == dst_md5:
        return True, "upload: bypassed."
    
    try :
      body_meta = {
        "mimetype" : helper.get_mimetype(localname=localname)
      }
      file_upload = MediaFileUpload(filename=localname, mimetype=helper.get_mimetype(localname=localname), chunksize=CHUNK_SIZE )
      file = self.gdrive_service_v3.files().update(fileId=id, body=body_meta, media_body=file_upload).execute()
    except Exception as err:
       return Fasle, "upload:" + str(err)

    if verify:
      src_md5 = self.get_meta(id=id)['md5Checksum']
      if src_md5 == dst_md5:
        return True, "upload: verified"
    else:
      return True, "upload: success"
    
    
    
    
    
  # ====================================================
  #
  #  Create file
  #
  # ====================================================    
    
  def create(self, name, localname):
    
    names=self._parse_full_name(name)
    
    if len(names) == 1: 
      parent = self.root_id
    else:
      pass
    
  
    # if file not exist, then create
    # otherwise : TODO
    if len(self.get_id(name=name)) == 0: 
      type = helper.get_mimetype(type=type)
      
      file_metadata = {
        'name': name,
        'mimeType': type,
        'parents' : [ parent ]
      }
      
      file = self.gdrive_service_v3.files().create(body=file_metadata, fields='id').execute()  
    else:
      return None
      
    
    
    if localname is not None and type != helper.get_mimetype(type="folder") :
      self.upload(localname=localname )
    
    return file.get('id')
  


  # ====================================================
  #
  #  Gdrive file list generator
  #
  # ====================================================    

  def gen_list(self, name=None, is_folder=None, parent=None, cust_properties=None, fields=None, order_by='folder,name,createdTime'):
    q = []
    params = {'fields' : fields, 'pageSize' : self.page_size, 'pageToken': None, 'orderBy': order_by}
    

    if fields is not None:
      params['fields'] =  ','.join([ 'files/'+ f.replace('files/','')  for f in fields.split(',')])
    else:
      params.pop('fields', None)
    
    if name is not None:
      q.append("name = '%s'" % name.replace("'", "\\'"))
    if is_folder is not None:
      q.append("mimeType %s '%s'" % ('=' if is_folder else '!=', helper.get_mimetype(type='folder')))
    if parent is not None:
      q.append("'%s' in parents" % parent.replace("'", "\\'"))
    if cust_properties is not None:
      for k,v in cust_properties.items():
        q.append("properties has { key='%s' and value='%s' }" % (k , v.replace("'", "\\'") ) )
      
    
    # add query expression
    if q: params['q'] = ' and '.join(q)

    while True:
      response = self.gdrive_service_v3.files().list(**params).execute()
      for f in response['files']:
        yield f
      try:
        params['pageToken'] = response['nextPageToken']
      except KeyError:
        return
    
    
    
  # ====================================================
  #
  #  Gdrive file list 
  #
  # ====================================================    
  
  def get_list(self,**kwargs):
    result = []
    response = self.gen_list(**kwargs)
    for f in response:
      result.append(f)
    
    return result
  

  # ===============================================================  
  #  Get Full name (path) of the GDrive file
  #  For example: /folder1/sub-folder2/sub_folder3/the_file
  #
  #
  # ===============================================================
  def get_id (self, name=None, id=None, force_update_cache=False):
    assert name is not None or id is not None , "provide at least one of name or id"
    
    if force_update_cache == True or self.meta_cache is None:
      self.get_meta_cache(name=name, id=id)
      
    ids = []
    
    if name is not None:
      for k in self.meta_cache.keys():
        r = self.meta_cache[k]
        if r['full_name'][-len(name):] == name :
          ids.append(k)
          
    else:
      for k in self.meta_cache.keys():
        r = self.meta_cache[k]
        if k == id :
          ids.append(k)
      
    return ids
      
  

  # ===============================================================  
  #  Get Full name (path) of the GDrive file
  #  For example: /folder1/sub-folder2/sub_folder3/the_file
  #
  #
  # ===============================================================
  def get_full_name (self, name=None, id=None, force_update_cache=False):
    assert name is not None or id is not None , "provide at least one of name or id"
    
    if force_update_cache == True or self.meta_cache is None:
      self.get_meta_cache(name=name, id=id)
      
    full_name = []
    
    if name is not None:
      for k in self.meta_cache.keys():
        r = self.meta_cache[k]
        if r['full_name'][-len(name):] == name :
          full_name.append(r['full_name'])
          
    else:
      for k in self.meta_cache.keys():
        r = self.meta_cache[k]
        if k == id :
          full_name.append(r['full_name'])
      
    return full_name
  
  

  def delete(self, id, trash=False):
    if self.get_meta(id=id) is not None:
      try :
        if trash :
          self.gdrive_service_v3.files().trash(fileId=id).execute()
        else:
          self.gdrive_service_v3.files().delete(fileId=id).execute()
      except Exception as err:
        return False, "delete:" + str(err)
    else:
      return True, "success"
  

  
  def set_meta(self,id,body_meta):
    try :
      results = self.gdrive_service_v3.files().update(fileId=id, body=body_meta).execute()
    except Exception as err:
      return False, "set_meta:" + str(err)
    return True, "success"
    

  def get_meta(self,id,fields="*"):
    results = None
    try :
      results = self.gdrive_service_v3.files().get(fileId=id, fields=fields).execute()
    except Exception as err:
      pass
    return results



  # ============================================================
  #
  # Read meta cache of the file and parant chain.
  # 
  #
  # ============================================================
  
    
  def get_meta_cache(self, name=None, id=None, tree=True):
    assert name is not None or id is not None , "provide at least one of name or id"
    
    layer_meta = {}
    chain_meta = {}
    names = self._parse_full_name(name)
    
    if name is not None:
      n = names[-1]
      found_list = self.get_list(name=n)
      for f in found_list:
        id = f['id']
        layer_meta[id] = self.get_meta(id=id)
    else:
      layer_meta[id] = self.get_meta(id=id)
      
    while True:
      chain_meta = copy.deepcopy(layer_meta)
      
      names = names[:-1]
      
      if len(names) >0 :
        n = names[-1]
      else:
        n = None
      
      for k in layer_meta.keys():
        r = layer_meta[k]
        parent_id = r['parents'][0]
        
        if parent_id == self.root_id :
          continue
        
        if parent_id in chain_meta :
          continue
       
        t = self.get_meta(id=parent_id)

        # if parent name match the n
        if t['name'] == n or n is None and tree==True:
          chain_meta[parent_id] = t
          
        # if parent name not match the n, then remove the node meta
        if t['name'] != n and n is not None :
          _, chain_meta = self._get_hierchy (tree_data = chain_meta, id=k, operation="remove")
      
      if chain_meta != layer_meta:
        layer_meta = copy.deepcopy(chain_meta)
      else:
        break
    
    # if no entire tree to be returned
    
    if tree == False:
      self.meta_cache = chain_meta
      return self.meta_cache
    
    
    # cleanup layer_meta
    clean_chain_meta = {}
    while True:
      v = len(clean_chain_meta.keys())
      for k in layer_meta.keys():
        
        r = layer_meta[k]
        parent_id = r['parents'][0]
        
        if parent_id == self.root_id :
          clean_chain_meta[k] = r
          clean_chain_meta[k]["full_name"] = "/" + clean_chain_meta[k]["name"]
      
        
        if parent_id in clean_chain_meta :
          clean_chain_meta[k] = r
          clean_chain_meta[k]["full_name"] = clean_chain_meta[parent_id]["full_name"] + "/" + clean_chain_meta[k]["name"] 
        
      if v == len(clean_chain_meta.keys()):
        break;
      
    self.meta_cache = clean_chain_meta
    return self.meta_cache



if __name__ == "__main__":
  my_cloud = Gdrive(cred_file="R:/credentials.json" )
  #my_cloud.get_folder_list()
  
  #for f in my_cloud.search_folder(name= "root"):   print (f)
  #print (my_cloud.get_id(name="/test2/test2/1_junco.jpg"))
  
  #print (my_cloud.get_meta_cache(id="10KGzUTKURK82_OU-1qFuxYKdgUKHD4LC"))
  
  #print (my_cloud.get_meta_cache(name="/test2/1_junco.jpg"))
  #print (my_cloud.get_full_name(name="1_junco.jpg"))
  #print (my_cloud.get_full_name(id="10KGzUTKURK82_OU-1qFuxYKdgUKHD4LC"))
  #print (my_cloud.get_id(name="1_junco.jpg"))

  #print (my_cloud.is_folder(name="1_junco.jpg"))
  #print (my_cloud.create(name="LP6.txt"))
  
  #print(helper.get_mimetype(localname="R:/IMG1.bin"))
  #print (my_cloud.get_meta_cache(name="LP6.txt", tree=False))
  #print (my_cloud.upload(id="1KGmskL2N8f7snWP_EvLTKyzpz4uJ1RTp", localname="R:/IMG1.bin", verify=True))
  
  body_meta = { 

                "description" : " { \"archive\": \" abc\" } ",
                "properties" : { 
                  "my_prop" : "test_p1",
                  "src_name_key" : "abcdefg"
                } ,
                
                "contentHints" : {
                  "indexableText" : " ___ a long description here ___"
                
                
                }
              }
              
  #print(my_cloud.set_meta(id="1KGmskL2N8f7snWP_EvLTKyzpz4uJ1RTp", body_meta=body_meta))
  
  cust_properties =  {'my_prop': 'test_p1' }
  
  #for f in my_cloud.get_list(cust_properties = cust_properties) :
  #  print (f)
    
    
  print (my_cloud.get_list(cust_properties = cust_properties, fields="kind,id,name,modifiedTime,properties/src_name_key,md5Checksum") )
  #print(my_cloud.download(id="1nAD4tlsAIAM2Cadg3LqY1DlB5CoZrZrJ", localname="R:/t1.dat", verify=True))
  #print(my_cloud.delete(id="1nAD4tlsAIAM2Cadg3LqY1DlB5CoZrZrJ"))
  
  
  
  
  
  """
  f = my_cloud.get_list(name="test2")
  print (f)
  print (my_cloud.get_parent_id(f[0]['id']))
  #my_cloud.delete_file(id='1BTVsE1jU0X9cwPP88xElW90FUHZTvBPm')

    
  #14_i-9jqqzPC6sECZwVH-IxTKrD93ueC7
  #0ALjvPRMe8hRyUk9PVA
  print (my_cloud.get_full_name(name='1_rangandas-gardenglimpses4.jpg'))
  print (my_cloud.create(name='my_file2.txt'))
  #print (my_cloud.get_name(id='0ALjvPRMe8hRyUk9PVA'))  
  
  #my_cloud.search_files_folers()
  #my_cloud.create_folder(folder_name="test2")
  #print (my_cloud.get_id(name='test1'))
  #print (my_cloud.root_id)
  """
