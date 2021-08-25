from . import utils
try:
    from StringIO import StringIO
except:
    from io import StringIO
import pandas as pd
import json
from ...utilities import api_base
from ...config.default_config import *
 
def gdelt_feed(query, condition=[], pos=0, count=10, 
               filter='must', format='pandas'):
    http_client = api_base.__get_conn__()
    request_string = []
    
    request_string.append('api/search/v1/bhr_feed')
    request_string.append('?query=')
    request_string.append(str(query))
    
    request_string.append('&pos=')
    request_string.append(str(pos))
    
    request_string.append('&count=')
    request_string.append(str(count))
    
    request_string.append('&filter=')
    request_string.append(filter)
    
        
    if len(condition) > 0:
        request_string.append('&condition=')
        request_string.append(str(condition))
        
    result = api_base.__get_result__('GET',''.join(request_string), http_client, gw=True)
    return result if format=='json' else utils.to_pandas(result)

def bhr_feed(query, condition=[], pos=0, count=10, 
             filter='must', format='pandas'):
    http_client = api_base.__get_conn__()
    request_string = []
    
    request_string.append('api/search/v1/bhr_feed')
    request_string.append('?query=')
    request_string.append(str(query))

    request_string.append('&pos=')
    request_string.append(str(pos))
    
    request_string.append('&count=')
    request_string.append(str(count))
    
    request_string.append('&filter=')
    request_string.append(str(filter))
    
    
    if len(condition) > 0:
        request_string.append('&condition=')
        request_string.append(str(condition))
        
    result = api_base.__get_result__('GET',''.join(request_string), http_client, gw=True)
    return result if format=='json' else utils.to_pandas(result)


def company(query, pos=0, count=10, format='padnas'):
    http_client = api_base.__get_conn__()
    request_string = []
    
    request_string.append('api/search/v1/company')
    request_string.append('?query=')
    request_string.append(str(query))
    
    request_string.append('&pos=')
    request_string.append(str(pos))
    
    request_string.append('&count=')
    request_string.append(str(count))
   
    request_string.append('&format_str=')
    request_string.append(str(0))
    
    result = api_base.__get_result__('GET',''.join(request_string), http_client, gw=True)
    return result if format=='json' else pd.DataFrame(json.loads(result))#utils.to_pandas(result)
    
    
def gd_reviews(query, condition=[],  pos=0, count=10,  
               filter='must', format='pandas'):
    http_client = api_base.__get_conn__()
    request_string = []
    
    request_string.append('api/search/v1/gd_reviews')
    request_string.append('?query=')
    request_string.append(str(query))
    
    
    request_string.append('&pos=')
    request_string.append(str(pos))
    
    request_string.append('&count=')
    request_string.append(str(count))
    
    
    request_string.append('&filter=')
    request_string.append(str(filter))
    
    if len(condition) > 0:
        request_string.append('&condition=')
        request_string.append(str(condition))
        
    result = api_base.__get_result__('GET',''.join(request_string), http_client, gw=True)
    return result if format=='json' else utils.to_pandas(result)