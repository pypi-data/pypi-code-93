from gplean.obj import update_one_row,aupdate_one_row
from gplean.query import query,aquery

def config_regis(params):
    cfg = params['cfg']
    arr = query({'cfg':cfg,'cls':'GlobalConfig','howmany':1})
    obj_id = arr[0]['objectId']
    data = params['data']
    d = {'cfg':cfg,'cls':'GlobalConfig','id':obj_id,'data':data}
    rslt = update_one_row(d)
    return(rslt)

async def aconfig_regis(params):
    cfg = params['cfg']
    arr = await aquery({'cfg':cfg,'cls':'GlobalConfig','howmany':1})
    obj_id = arr[0]['objectId']
    data = params['data']
    d = {'cfg':cfg,'cls':'GlobalConfig','id':obj_id,'data':data}
    rslt = await aupdate_one_row(d)
    return(rslt)
