#!/usr/bin/env python
# coding: utf-8

# In[92]:


import urllib
from datetime import datetime, timedelta
from urllib.request import urlopen
from urllib import request, parse
from hashlib import md5
from os import system
from time import time
from pathlib import Path
import shutil
g_str_bucket="default_bucket"
    
def set_bucket(str_bucket_name):
    g_str_bucket=str_bucket_name

def get_hash_filename(str_key):
    return f"""{md5(str_key.encode(encoding="utf-8")).hexdigest()}.cache"""

def get_str_cache(str_key):
    print(f"cameo_cache.py, get_str_cache, {get_cache_path()}{get_hash_filename(str_key)}")
    io=open(f"{get_cache_path()}{get_hash_filename(str_key)}","r")
    str_content=io.read()
    io.close()
    return str_content

def get_year_month():
    return datetime.now().strftime("%Y-%m-%d")

def get_year_month_yesterday():
    return datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')

def get_cache_path():
    return f"./cameo_cache_data/{get_year_month()}/"

def get_cache_path_yesterday():
    return f"./cameo_cache_data/{get_year_month_yesterday()}/"

def delete_cache_yesterday():
    print(f"cameo_cache.py, delete_cache_yesterday, {get_cache_path_yesterday()}")
    shutil.rmtree(get_cache_path_yesterday(),ignore_errors=True)
        
def make_cache(str_key, str_value):
    delete_cache_yesterday()
    Path(get_cache_path()).mkdir(parents=True, exist_ok=True)
    print(f"cameo_cache.py, make_cache, {get_cache_path()}{get_hash_filename(str_key)}")
    io=open(f"{get_cache_path()}{get_hash_filename(str_key)}","w")
    io.write(str_value)
    io.close()
    return f"{get_cache_path()}{get_hash_filename(str_key)}"

if __name__=="__main__":
    set_bucket("aiot_public")
    make_cache("key 3","value 333")
    print("get_str_cache,"+get_str_cache("key 3"))


# In[61]:





# In[ ]:


# import urllib
# from datetime import datetime
# from urllib.request import urlopen
# from urllib import request, parse
# from hashlib import md5
# from os import system
# from time import time

# g_str_bucket="default_bucket"
# g_str_cameo_cache_server="http://cache.cameo.tw:8083/"
    
# def set_bucket(str_bucket_name):
#     g_str_bucket=str_bucket_name

# def get_str_cache(str_key):
#     try:
#         str_key=urllib.parse.quote(str_key,safe='')
#         return urlopen(f"{g_str_cameo_cache_server}get/get_str_cache?str_bucket={g_str_bucket}&str_key={str_key}").read().decode("utf-8")
#     except Exception as e:
#         return f"Exception 20200521_090819, {e}"

# def make_cache(str_key, str_value):
#     try:
#         str_encode=parse.urlencode({'str_key':str_key,'str_value':str_value}).encode()
# #         str_encode=parse.urlencode(f'''{"str_key":{str_key},"str_value":{str_value}}''').encode()
    
#         req=request.Request(f"{g_str_cameo_cache_server}post/make_cache", data=str_encode) # this will make the method "POST"
#         str_response=request.urlopen(req).read().decode("utf-8")
#         print(f"make_cache,str_response,{str_response}")
#     except Exception as e:
#         return f"Exception 20200521_092110, {e}"

# if __name__=="__main__":
#     set_bucket("aiot_public")
#     print('key1,'+get_str_cache("key1"))
#     str_url="https://iotai-dev.cameo.tw/api/v2/iot/events?start_time=2020-04-01 00:00:00&end_time=2020-04-29 23:59:59&min_lat=22.43422&max_lat=22.89&min_lon=120.1393&max_lon=120.4398"
#     print('key2,'+get_str_cache(str_url))
#     make_cache("post key 1","post value 1")

