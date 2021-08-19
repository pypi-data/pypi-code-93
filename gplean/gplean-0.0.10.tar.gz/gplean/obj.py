from gplean.engine import areq,req
import edict.edict as eded
import efuntool.efuntool as eftl

#########
def get_del_one_row_kwargs(d):
    cfg = d['cfg']
    cls = d['cls']
    obj_id = d['id']
    kwargs = {
        "cfg":cfg,
        "method":'delete',
        "paths":['1.1','classes',cls,obj_id],
    }
    return(kwargs)


def del_one_row(d):
    '''
    '''
    kwargs = get_del_one_row_kwargs(d)
    rslt = req(**kwargs)
    return(rslt)


async def adel_one_row(d):
    '''
    '''
    kwargs = get_del_one_row_kwargs(d)
    rslt = await areq(**kwargs)
    return(rslt)


#########



#########
def get_cls_kwargs(d):
    cfg = d['cfg']
    cls = d['cls']
    data = d['data'] if('data' in d) else {} 
    kwargs = {
        "cfg":cfg,
        "method":'post',
        "paths":['1.1','classes',cls],
        "data":data
    }
    return(kwargs)

def creat_cls(d):
    '''
    '''
    kwargs = get_cls_kwargs(d)
    rslt = req(**kwargs)
    obj_id = rslt['objectId']
    d['id'] = obj_id
    rslt = del_one_row(d)
    return(rslt)


async def acreat_cls(d):
    '''
    '''
    kwargs = get_cls_kwargs(d)
    rslt = await areq(**kwargs)
    obj_id = rslt['objectId']
    d['id'] = obj_id
    rslt = adel_one_row(d)
    return(rslt)
##############



def get_insert_one_row_kwargs(d):
    cfg = d['cfg']
    cls = d['cls']
    data = d['data'] if('data' in d) else {}
    kwargs = {
        "cfg":cfg,
        "method":'post',
        "paths":['1.1','classes',cls],
        "data":data
    }
    return(kwargs)


def insert_one_row(d):
    '''
    '''
    kwargs = get_insert_one_row_kwargs(d)
    rslt = req(**kwargs)
    return(rslt)

async def ainsert_one_row(d):
    '''
    '''
    kwargs = get_insert_one_row_kwargs(d) 
    rslt = await areq(**kwargs)
    return(rslt)


######

def get_update_one_row_kwargs(d):
    cfg = d['cfg']
    cls = d['cls']
    obj_id = d['id']
    data = d['data']
    kwargs = {
        "cfg":cfg,
        "method":'put',
        "paths":['1.1','classes',cls,obj_id],
        "data":data
    }
    return(kwargs)


def update_one_row(d):
    '''
    '''
    kwargs = get_update_one_row_kwargs(d)
    rslt = req(**kwargs)
    return(rslt)


async def aupdate_one_row(d):
    '''
    '''
    kwargs = get_update_one_row_kwargs(d)
    rslt = await areq(**kwargs)
    return(rslt)


######
def get_fetch_one_row_kwargs(d):
    cfg = d['cfg']
    cls = d['cls']
    obj_id = d['id']
    kwargs = {
        "cfg":cfg,
        "method":'get',
        "paths":['1.1','classes',cls,obj_id],
    }
    return(kwargs)

def fetch_one_row(d):
    '''
    '''
    kwargs = get_fetch_one_row_kwargs(d)
    rslt = req(**kwargs)
    return(rslt)


async def afetch_one_row(d):
    '''
    '''
    kwargs = get_fetch_one_row_kwargs(d)
    rslt = await areq(**kwargs)
    return(rslt)


######
