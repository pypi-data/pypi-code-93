import aiohttp
import requests
import xxurl.xxurl as xuxu
import elist.elist as elel
import efuntool.efuntool as eftl
from requests_toolbelt.adapters import source
import json


##################
def get_base_url_from_cfg(cfg):
    d = {
        'scheme': cfg['scheme'],
        'username': '',
        'password': '',
        'hostname': cfg['hostname'],
        'port': '',
        'path': '',
        'params': '',
        'query': '',
        'fragment': ''
    }
    return(xuxu.d2u(d))

##################


##########################
def set_src_addr(**kwargs):
    src_ip = eftl.dflt_kwargs("src_ip",None,**kwargs)
    src_port = eftl.dflt_kwargs("src_port",None,**kwargs)
    src_addr = (None,None)
    if((src_ip != None) and (src_port !=None)):
        src_addr=(src_ip,src_port)
    elif(src_ip != None):
        src_addr=(src_ip)
    else:
        src_addr = None
    return(src_addr)
##########################


############
def set_sess(**kwargs):
    src_addr = set_src_addr(**kwargs) 
    sess = eftl.dflt_kwargs("sess",requests.Session(),**kwargs)
    new_source = source.SourceAddressAdapter('0.0.0.0' if(src_addr==None) else src_addr)
    sess.mount('http://', new_source)
    sess.mount('https://', new_source)
    return(sess)
############


##################
def d2query(d):
    query = ""
    for k in d:
        query = query + str(k) + "=" + str(d[k]) +"&"
    query = query[:-1]
    return(query)
####################

####
def set_xlc_sess(headers,**kwargs):
    xlc_sess = eftl.dflt_kwargs("xlc_sess",None,**kwargs)
    if(xlc_sess == None):
        pass
    else:
        headers["X-LC-Session"]=xlc_sess
    return(headers)



####




#同步请求
def req(**kwargs):
    #
    method = eftl.dflt_kwargs("method",'get',**kwargs)
    paths = eftl.dflt_kwargs("paths",[],**kwargs) 
    query = eftl.dflt_kwargs("query",{},**kwargs)
    data = eftl.dflt_kwargs("data",{},**kwargs)
    data = json.dumps(data)
    cfg = kwargs['cfg']
    base_url = get_base_url_from_cfg(cfg)
    sess = set_sess(**kwargs) 
    ##############
    f = sess.__getattribute__(method)
    path = elel.join(paths,"/")
    urld = xuxu.u2d(base_url)
    query = d2query(query)
    urld['query'] = query
    urld['path'] = path
    url = xuxu.d2u(urld)
    ###############
    headers = {
        "X-LC-Id":cfg['appid'],
        "X-LC-Key":cfg['appkey']
    }
    ##############
    headers = set_xlc_sess(headers,**kwargs)
    ##############
    if(method == 'post'):
        headers["Content-Type"]="application/json"
        r = f(url,data=data,headers=headers)
    elif(method == 'delete'):
        r = f(url,data=data,headers=headers)
    elif(method == 'put'):
        headers["Content-Type"]="application/json"
        r = f(url,data=data,headers=headers)     
    else:
        headers["Content-Type"]="application/json"
        r = f(url,headers=headers)
    ###########
    keepalive = eftl.dflt_kwargs("keepalive",False,**kwargs)
    if(keepalive):
        return({'sess':sess,'res':r.json()})        
    else:
        sess.close()
        return(r.json())


#异步请求
async def areq(**kwargs):
    method = eftl.dflt_kwargs("method",'get',**kwargs)
    paths = eftl.dflt_kwargs("paths",[],**kwargs)
    query = eftl.dflt_kwargs("query",{},**kwargs)
    data = eftl.dflt_kwargs("data",{},**kwargs)
    #data = json.dumps(data)
    cfg = kwargs['cfg']
    base_url = get_base_url_from_cfg(cfg)
    ####
    src_addr = set_src_addr(**kwargs)
    conn = aiohttp.TCPConnector(local_addr=src_addr)  
    sess = eftl.dflt_kwargs("sess",aiohttp.ClientSession(connector=conn),**kwargs)
    ####
    keepalive = eftl.dflt_kwargs("keepalive",False,**kwargs)
    ####
    headers = {
        "X-LC-Id":cfg['appid'],
        "X-LC-Key":cfg['appkey']
    }
    ####
    path = elel.join(paths,"/")
    urld = xuxu.u2d(base_url)
    query = d2query(query)
    urld['path'] = path
    urld['query'] = query
    url = xuxu.d2u(urld)
    ####
    headers = set_xlc_sess(headers,**kwargs)
    ####
    if(method == 'post'):
        async with sess.post(url,json=data,headers=headers) as r:
           rslt = await r.json()
           if(keepalive):
               return({"sess":sess,"res":rslt})
           else:
               await sess.close()
               return(rslt)
    elif(method == 'delete'):
        async with sess.delete(url,headers=headers) as r:
           rslt = await r.json()
           if(keepalive):
               return({"sess":sess,"res":rslt})
           else:
               await sess.close()
               return(rslt)
    elif(method == 'put'):
        async with sess.put(url,json=data,headers=headers) as r:
           rslt = await r.json()
           if(keepalive):
               return({"sess":sess,"res":rslt})
           else:
               await sess.close()
               return(rslt)
    else:
        headers["Content-Type"]="application/json"
        async with sess.get(url,headers=headers) as r:
           rslt = await r.json()
           if(keepalive):
               return({"sess":sess,"res":rslt})
           else:
               await sess.close()
               return(rslt)

 
