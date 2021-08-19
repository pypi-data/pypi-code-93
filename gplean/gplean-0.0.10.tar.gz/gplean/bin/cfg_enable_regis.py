from gplean.obj import update_one_row,aupdate_one_row
from gplean.query import query,aquery
from efdir import fs
import argparse
from xdict.jprint import pobj
import json
######

def fmt_json_argument(data):
    if(isinstance(data,str)):
        cond = fs.filexist(data)
        if(cond):
            data = fs.rjson(data)
        else:
            try:
                data = json.loads(data)
            except:
                data = eval(data)
            else:
                pass
    else:
        pass
    return(data)



######
def fmt_boolean(s):
    if(s):
        if(isinstance(s,str)):
            s = s.lower()
            if(s=='true'):
                return(True)
            else:
                return(False)
        else:
            return(s)           
    else:
        return(s)
######

#######
parser = argparse.ArgumentParser()
parser.add_argument('-cfg','--cfg', default="cfg.json",help="config json file")
parser.add_argument('-enable_regis','--enable_regis', default=False,help="enable regis")
parser.add_argument('-mode','--mode', default="sync",help="mode")
#######


########
args = parser.parse_args()
cfg = fs.rjson(args.cfg)
data = {"enable_regis":fmt_boolean(args.enable_regis)} 
mode = args.mode
##########

if(mode == 'sync'):
    def main():
        arr = query({'cfg':cfg,'cls':'GlobalConfig','howmany':1})
        obj_id = arr[0]['objectId']
        d = {'cfg':cfg,'cls':'GlobalConfig','id':obj_id,'data':data}
        rslt = update_one_row(d)
        pobj(rslt)
else:
    import asyncio
    loop = asyncio.get_event_loop()
    async def a():
        arr = await aquery({'cfg':cfg,'cls':'GlobalConfig','howmany':1})
        obj_id = arr[0]['objectId']
        d = {'cfg':cfg,'cls':'GlobalConfig','id':obj_id,'data':data}
        rslt = await aupdate_one_row(d)
        pobj(rslt)
    def main():
        loop.run_until_complete(a())


##########

'''

'''

