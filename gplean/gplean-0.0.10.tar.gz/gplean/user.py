from gplean.engine import areq,req
import edict.edict as eded

def get_regis_kwargs(d):
    cfg = d['cfg']
    kl = list(d.keys())
    kl.remove('cfg')
    data = eded.sub_algo(d,kl)
    kwargs = {
        "cfg":cfg,
        "method":'post',
        "paths":['1.1','users'],
        "data":data
    }
    return(kwargs)

def regis(d):
    '''
    {
        'sessionToken': 'xa0fwryqs0xi07x2gkg9t3byd',
        'updatedAt': '2020-06-07T13:47:02.052Z',
        'objectId': '5edcefd645e7ff00083b7a34',
        'username': 'root',
        'createdAt': '2020-06-07T13:47:02.052Z',
        'emailVerified': False,
        'mobilePhoneVerified': False
    }
    '''
    kwargs = get_regis_kwargs(d)
    rslt = req(**kwargs)
    return(rslt)


async def aregis(d):
    '''
    '''
    kwargs = get_regis_kwargs(d)
    rslt = await areq(**kwargs)
    return(rslt)


####

def get_regis_corp_kwargs(d):
    cfg = d['cfg']
    data = d['data'] if('data' in d) else {}
    kwargs = {
        "cfg":cfg,
        "method":'post',
        "paths":['1.1','classes','Corp'],
        "data":data
    }
    return(kwargs)

def regis_corp(d):
    '''
    '''
    kwargs = get_regis_corp_kwargs(d)
    rslt = req(**kwargs)
    return(rslt)


async def aregis_corp(d):
    '''
    '''
    kwargs = get_regis_corp_kwargs(d)
    print("!@===>",kwargs)
    rslt = await areq(**kwargs)
    return(rslt)

####




def get_login_kwargs(d):
    cfg = d['cfg']
    data = eded.sub_algo(d,['username','password'])
    kwargs = {
        "cfg":cfg,
        "method":'post',
        "paths":['1.1','login'],
        "data":data
    }
    return(kwargs)

def login(d):
    '''
    '''
    kwargs = get_login_kwargs(d)
    rslt = req(**kwargs)
    return(rslt)


async def _alogin(d):
    '''
    '''
    kwargs = get_login_kwargs(d)
    rslt = await areq(**kwargs)
    return(rslt)

import copy

async def alogin(d):
    d =copy.deepcopy(d) 
    d['cfg']['appkey'] = d['cfg']['masterkey']
    users = await aget_all_users(d)
    users = users['results']
    openids = list(map(lambda r:r['openid'],users))
    if(not(d['username'] in openids)):
        return({'session_key': 'anonymous', 'openid': d['username'], 'errcode': 0, 'errmsg': '请求成功', 'is_admin': False})
    else:
        rslt = await _alogin(d);
        return(rslt)

#########
def get_me_kwargs(d):
    cfg = d['cfg']
    kwargs = {
        "cfg":cfg,
        "method":'get',
        "paths":['1.1','users','me'],
        "xlc_sess":d['xlc_sess']
    }
    return(kwargs)

def me(d):
    '''
    '''
    kwargs = get_me_kwargs(d)
    rslt = req(**kwargs)
    return(rslt)


async def ame(d):
    '''
    '''
    kwargs = get_me_kwargs(d)
    rslt = await areq(**kwargs)
    return(rslt)

##############

def update(d):
    '''
    '''
    kwargs = get_me_kwargs(d)
    rslt = req(**kwargs)
    obj_id = rslt['objectId']
    kwargs['method'] = 'put'
    kwargs['paths'] = ['1.1','users',obj_id]
    kwargs['data'] = d['data']
    rslt = req(**kwargs)
    return(rslt)

async def aupdate(d):
    '''
    '''
    kwargs = get_me_kwargs(d)
    rslt = await areq(**kwargs)
    obj_id = rslt['objectId']
    kwargs['method'] = 'put'
    kwargs['paths'] = ['1.1','users',obj_id]
    kwargs['data'] = d['data']
    rslt = await areq(**kwargs)
    return(rslt)

###################

def modify_password_via_xlc_sess(d):
    '''
    '''
    kwargs = get_me_kwargs(d)
    rslt = req(**kwargs)
    obj_id = rslt['objectId']
    kwargs['method'] = 'put'
    kwargs['paths'] = ['1.1','users',obj_id,'updatePassword']
    kwargs['data'] = d['data']
    rslt = req(**kwargs)
    return(rslt)

async def amodify_password_via_xlc_sess(d):
    '''
    '''
    kwargs = get_me_kwargs(d)
    rslt = await areq(**kwargs)
    obj_id = rslt['objectId']
    kwargs['method'] = 'put'
    kwargs['paths'] = ['1.1','users',obj_id,'updatePassword']
    kwargs['data'] = d['data']
    rslt = await areq(**kwargs)
    return(rslt)



###############

def get_all_users_kwargs(d):
    cfg = d['cfg']
    kwargs = {
        "cfg":cfg,
        "method":'get',
        "paths":['1.1','users'],
    }
    return(kwargs)

def get_all_users(d):
    '''
    '''
    kwargs = get_all_users_kwargs(d)
    rslt = req(**kwargs)
    return(rslt)


async def aget_all_users(d):
    '''
    '''
    kwargs = get_all_users_kwargs(d)
    rslt = await areq(**kwargs)
    return(rslt)



################
