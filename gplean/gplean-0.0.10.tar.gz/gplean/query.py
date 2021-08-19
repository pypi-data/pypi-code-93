from gplean.engine import areq,req
import edict.edict as eded
import efuntool.efuntool as eftl

#########
def get_count_kwargs(d,cond={}):
    cfg = d['cfg']
    cls = d['cls']
    query = cond
    query['limit'] = 0
    query['count'] = 1
    kwargs = {
        "cfg":cfg,
        "method":'get',
        "paths":['1.1','classes',cls],
        "query":{'limit':0,'count':1}
    }
    return(kwargs)


def count(d,cond={}):
    '''
    '''
    kwargs = get_count_kwargs(d,cond)
    rslt = req(**kwargs)
    return(rslt['count'])


async def acount(d,cond={}):
    '''
    '''
    kwargs = get_count_kwargs(d,cond)
    rslt = await areq(**kwargs)
    return(rslt['count'])


#########

#########

def _get_query_kwargs(d,cond={}):
    cfg = d['cfg']
    cls = d['cls']
    query = cond
    limit = d['limit'] if('limit' in d) else 100
    offset = d['offset'] if('offset' in d) else 0
    query['limit'] = limit
    query['skip'] = offset
    query['order'] = '-createdAt'
    kwargs = {
        "cfg":cfg,
        "method":'get',
        "paths":['1.1','classes',cls],
        "query":query,
        "cls":cls,
        "limit":limit,
        "offset":offset
    }
    return(kwargs)


def _query(d,cond={}):
    '''
    '''
    kwargs = _get_query_kwargs(d,cond)
    rslt = req(**kwargs)
    return(rslt['results'])


async def _aquery(d,cond={}):
    '''
    '''
    kwargs = _get_query_kwargs(d,cond)
    rslt = await areq(**kwargs)
    return(rslt['results'])



def query(d,cond={}):
    total = count(d,cond)
    limit = d['limit'] if('limit' in d) else 100
    offset = d['offset'] if('offset' in d) else 0
    howmany = d['howmany']
    offset = offset if(offset<total) else (total - 1)
    real_total = total - offset
    howmany = howmany if(howmany <= real_total) else real_total
    q = howmany // limit  #取多少轮,每轮取limit个
    r = howmany % limit   #最后一轮取多少个
    c = 0 
    d['offset'] = offset
    kwargs = d
    rslt = []
    while(c<q):
        kwargs = _get_query_kwargs(kwargs,cond)
        res = _query(kwargs,cond)
        kwargs['offset'] = kwargs['offset'] + limit
        c = c + 1
        rslt = rslt + res
    if(r>0):
        kwargs['limit'] = r
        kwargs = _get_query_kwargs(kwargs,cond)
        res = _query(kwargs,cond)
        rslt = rslt + res
    else:
        pass
    return(rslt)   
 
async def aquery(d,cond={}):
    total = await acount(d,cond)
    limit = d['limit'] if('limit' in d) else 100
    offset = d['offset'] if('offset' in d) else 0
    howmany = d['howmany']
    offset = offset if(offset<total) else (total - 1)
    real_total = total - offset
    howmany = howmany if(howmany <= real_total) else real_total
    q = howmany // limit  #取多少轮,每轮取limit个
    r = howmany % limit   #最后一轮取多少个
    c = 0 
    d['offset'] = offset
    kwargs = d
    rslt = []
    while(c<q):
        kwargs = _get_query_kwargs(kwargs,cond)
        res = await _aquery(kwargs,cond)
        kwargs['offset'] = kwargs['offset'] + limit
        c = c + 1
        rslt = rslt + res
    if(r>0):
        kwargs['limit'] = r
        kwargs = _get_query_kwargs(kwargs,cond)
        res = await _aquery(kwargs,cond)
        rslt = rslt + res
    else:
        pass
    return(rslt) 

########


