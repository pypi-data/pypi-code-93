from gplean.obj import creat_cls,acreat_cls
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


#######
parser = argparse.ArgumentParser()
parser.add_argument('-cfg','--cfg', default="cfg.json",help="config json file")
parser.add_argument('-cls','--cls', default="",help="class name")
parser.add_argument('-data','--data', default={},help="data")
parser.add_argument('-mode','--mode', default="sync",help="mode")
#######

########
args = parser.parse_args()
cfg = fs.rjson(args.cfg)
cls= args.cls
data = args.data
data = fmt_json_argument(data)
mode = args.mode
##########

if(mode == 'sync'):
    def main():
        d = {'cfg':cfg,'cls':cls,'data':data}
        rslt = creat_cls(d)
        pobj(rslt)
else:
    import asyncio
    loop = asyncio.get_event_loop()
    async def a():
        d = {'cfg':cfg,'cls':cls,'data':data}
        rslt = await acreat_cls(d)
        pobj(rslt)
    
    def main():
        loop.run_until_complete(a())


##########

'''
    @#gplean_obj_creat_cls -cls YearConserv
    {
        'objectId': '5edf4273a05dc80009f1345f',
        'createdAt': '2020-06-09T08:04:03.583Z'
    }
    @#

'''

