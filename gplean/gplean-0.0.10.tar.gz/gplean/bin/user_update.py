from gplean.user import update,aupdate 
from efdir import fs
import argparse
from xdict.jprint import pobj
#######
parser = argparse.ArgumentParser()
parser.add_argument('-cfg','--cfg', default="cfg.json",help="config json file")
parser.add_argument('-xlc_sess','--xlc_sess', default="",help="session id")
parser.add_argument('-mobile','--mobile', default="",help="mobile")
parser.add_argument('-mode','--mode', default="sync",help="mode")
#######

########
args = parser.parse_args()
cfg = fs.rjson(args.cfg)
xlc_sess = args.xlc_sess
mobile = str(args.mobile)
data = {"mobilePhoneNumber":mobile}
mode = args.mode
##########

if(mode == 'sync'):
    def main():
        d = {'cfg':cfg,'xlc_sess':xlc_sess,'data':data}
        rslt = update(d)
        pobj(rslt)
else:
    import asyncio
    loop = asyncio.get_event_loop()
    async def a():
        d = {'cfg':cfg,'xlc_sess':xlc_sess,'data':data}
        rslt = await aupdate(d)
        pobj(rslt)
    
    def main():
        loop.run_until_complete(a())


##########

'''
		@#gplean_user_update -xlc_sess igrtm006m3b0n1x2529nl82g6 -mobile 18614235077
@#

'''

