from gplean.user import regis,aregis
from efdir import fs
import argparse
from xdict.jprint import pobj
#######
#   用户名唯一 username
#   每个个用户关联一个企业 corp
#   这样一个企业可以有多个用户 
#   企业名称与用户名管理员分配,也就是注册接口只能管理员使用
#   加一个允许注册开关,管理员如果把这个开关打开,任何人都可以注册
#   管理员如果把这个开关关闭,只有管理员可以替别人注册
#   注册完毕以后管理员把用户名和密码告诉相关企业负责人,可以防止无关人员注册
#   lean的接口 _User 表不需要事先添加列字段  
#######
parser = argparse.ArgumentParser()
parser.add_argument('-cfg','--cfg', default="cfg.json",help="config json file")
parser.add_argument('-username','--username', default="",help="username")
parser.add_argument('-corp','--corp', default="",help="corp name")
parser.add_argument('-password','--password', default="",help="password")
parser.add_argument('-mode','--mode', default="sync",help="mode")
#######

########
args = parser.parse_args()
cfg = fs.rjson(args.cfg)
username = args.username
password = args.password
mode = args.mode
corp = username if(args.corp.strip() == "") else args.corp
##########

if(mode == 'sync'):
    def main():
        d = {'cfg':cfg,'username':username,'password':password,'corp':corp}
        rslt = regis(d)
        pobj(rslt)
else:
    import asyncio
    loop = asyncio.get_event_loop()
    async def a():
        d = {'cfg':cfg,'username':username,'password':password,'corp':corp}
        rslt = await aregis(d)
        pobj(rslt)
    
    def main():
        loop.run_until_complete(a())


##########

'''
		@#gplean_user_regis -username "李四" -password "lisi"
		{
		 'sessionToken': 'xlupcd1b93cec5mbz338jlvgk',
		 'updatedAt': '2020-06-07T14:01:27.993Z',
		 'objectId': '5edcf33745e7ff00083b8147',
		 'username': '李四',
		 'createdAt': '2020-06-07T14:01:27.993Z',
		 'emailVerified': False,
		 'mobilePhoneVerified': False
		}

        @gplean_user_regis -mode async -username "何七" -password "heqi"
'''

