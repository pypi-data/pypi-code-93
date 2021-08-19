from gplean.user import login,alogin
from efdir import fs
import argparse
from xdict.jprint import pobj
#######
parser = argparse.ArgumentParser()
parser.add_argument('-cfg','--cfg', default="cfg.json",help="config json file")
parser.add_argument('-username','--username', default="admin",help="username")
parser.add_argument('-password','--password', default="admin",help="password")
parser.add_argument('-mode','--mode', default="sync",help="mode")
#######

########
args = parser.parse_args()
cfg = fs.rjson(args.cfg)
username = args.username
password = args.password
mode = args.mode
##########

if(mode == 'sync'):
    def main():
        d = {'cfg':cfg,'username':username,'password':password}
        rslt = login(d)
        pobj(rslt)
else:
    import asyncio
    loop = asyncio.get_event_loop()
    async def a():
        d = {'cfg':cfg,'username':username,'password':password}
        rslt = await alogin(d)
        pobj(rslt)
    
    def main():
        loop.run_until_complete(a())


##########

'''
		@#gplean_user_login -username admin -password admin
		{
		 'sessionToken': 'igrtm006m3b0n1x2529nl82g6',
		 'updatedAt': '2020-06-07T13:58:53.176Z',
		 'objectId': '5edcf29dba7dda00095206eb',
		 'username': 'admin',
		 'createdAt': '2020-06-07T13:58:53.176Z',
		 'emailVerified': False,
		 'mobilePhoneVerified': False
		}
		@#gplean_user_login -username admin -password admin
		{
		 'sessionToken': 'igrtm006m3b0n1x2529nl82g6',
		 'updatedAt': '2020-06-07T13:58:53.176Z',
		 'objectId': '5edcf29dba7dda00095206eb',
		 'username': 'admin',
		 'createdAt': '2020-06-07T13:58:53.176Z',
		 'emailVerified': False,
		 'mobilePhoneVerified': False
		}
		@#

'''

