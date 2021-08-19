from gplean.user import modify_password_via_xlc_sess,amodify_password_via_xlc_sess 
from efdir import fs
import argparse
from xdict.jprint import pobj
#######
parser = argparse.ArgumentParser()
parser.add_argument('-cfg','--cfg', default="cfg.json",help="config json file")
parser.add_argument('-xlc_sess','--xlc_sess', default="",help="session id")
parser.add_argument('-old_password','--old_password', default="",help="old password")
parser.add_argument('-new_password','--new_password', default="",help="new password")
parser.add_argument('-mode','--mode', default="sync",help="mode")
#######

########
args = parser.parse_args()
cfg = fs.rjson(args.cfg)
xlc_sess = args.xlc_sess
data = {"old_password":args.old_password,'new_password':args.new_password}
mode = args.mode
##########

if(mode == 'sync'):
    def main():
        d = {'cfg':cfg,'xlc_sess':xlc_sess,'data':data}
        rslt = modify_password_via_xlc_sess(d)
        pobj(rslt)
else:
    import asyncio
    loop = asyncio.get_event_loop()
    async def a():
        d = {'cfg':cfg,'xlc_sess':xlc_sess,'data':data}
        rslt = await amodify_password_via_xlc_sess(d)
        pobj(rslt)
    
    def main():
        loop.run_until_complete(a())


##########

'''
@#gplean_user_modify_password_via_xlc_sess -xlc_sess igrtm006m3b0n1x2529nl82g6 -old_password xxx -new_password yyy
@#

'''

