from gplean.user import get_all_users,aget_all_users
from efdir import fs
import argparse
from xdict.jprint import pobj
#######
parser = argparse.ArgumentParser()
parser.add_argument('-cfg','--cfg', default="cfg.json",help="config json file")
parser.add_argument('-mode','--mode', default="sync",help="mode")
#######

########
args = parser.parse_args()
cfg = fs.rjson(args.cfg)
mode = args.mode
##########

if(mode == 'sync'):
    def main():
        d = {'cfg':cfg}
        rslt = get_all_users(d)
        pobj(rslt)
else:
    import asyncio
    loop = asyncio.get_event_loop()
    async def a():
        d = {'cfg':cfg}
        rslt = await aget_all_users(d)
        pobj(rslt)
    
    def main():
        loop.run_until_complete(a())


##########

'''
@#gplean_user_get_all_users
{
 'results':
            [
             {
              'updatedAt': '2020-06-07T13:47:02.052Z',
              'objectId': '5edcefd645e7ff00083b7a34',
              'username': 'root',
              'createdAt': '2020-06-07T13:47:02.052Z',
              'emailVerified': False,
              'mobilePhoneVerified': False
             },
             {
              'updatedAt': '2020-06-07T13:58:53.176Z',
              'objectId': '5edcf29dba7dda00095206eb',
              'username': 'admin',
              'createdAt': '2020-06-07T13:58:53.176Z',
              'emailVerified': False,
              'mobilePhoneVerified': False
             },
             {
              'updatedAt': '2020-06-07T14:00:29.689Z',
              'objectId': '5edcf2fdc14134000666e779',
              'username': '张三',
              'createdAt': '2020-06-07T14:00:29.689Z',
              'emailVerified': False,
              'mobilePhoneVerified': False
             },
             {
              'updatedAt': '2020-06-07T14:01:27.993Z',
              'objectId': '5edcf33745e7ff00083b8147',
              'username': '李四',
              'createdAt': '2020-06-07T14:01:27.993Z',
              'emailVerified': False,
              'mobilePhoneVerified': False
             },
             {
              'updatedAt': '2020-06-07T14:21:55.620Z',
              'objectId': '5edcf803ba7dda000952119c',
              'username': '王五',
              'createdAt': '2020-06-07T14:21:55.620Z',
              'emailVerified': False,
              'mobilePhoneVerified': False
             },
             {
              'updatedAt': '2020-06-07T14:30:39.639Z',
              'objectId': '5edcfa0fc14134000666f34e',
              'username': '赵六',
              'createdAt': '2020-06-07T14:30:39.639Z',
              'emailVerified': False,
              'mobilePhoneVerified': False
             },
             {
              'updatedAt': '2020-06-07T14:35:31.653Z',
              'objectId': '5edcfb33ba7dda00095216e7',
              'username': '何七',
              'createdAt': '2020-06-07T14:35:31.653Z',
              'emailVerified': False,
              'mobilePhoneVerified': False
             },
             {
              'updatedAt': '2020-06-07T14:35:56.101Z',
              'objectId': '5edcfb4c45e7ff00083b8ed2',
              'username': '宋八',
              'createdAt': '2020-06-07T14:35:56.101Z',
              'emailVerified': False,
              'mobilePhoneVerified': False
             }
            ]
}

'''

