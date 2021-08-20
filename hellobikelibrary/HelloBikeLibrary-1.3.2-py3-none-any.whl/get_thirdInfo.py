# -*- coding: utf-8 -*-
# @Author: yongfanmao
# @Date:   2020-08-19 16:30:39
# @E-mail: maoyongfan@163.com
# @Last Modified by:   yongfanmao
# @Last Modified time: 2021-07-16 21:23:38

from robot.api import logger
from HelloBikeLibrary.request import Request
from HelloBikeLibrary.con_mysql import UseMysql
import json
import traceback


"""
采集第三方信息
"""

class ThirdInfo(object):

	def get_container_ip(self,service_name,env="uat",tag="group1"):

		"""
			获取指定服务容器的对应IP地址,没有容器时,返回ecs ip地址
			env 不传默认为uat 支持(fat,uat,pre)
			tag 不传默认为group1  当传入的tag不存在,走默认group1
			
			返回内容为:
				ip地址

			例:
			|$(ip) |get container ip | AppHellobikeOpenlockService | env="uat" | tag="group1"
		"""
		try:
			ttGetEcsIpUrl = "https://tt.hellobike.cn/v1/api/{}".format(service_name)
			if env == "fat":
				groupsUrl = "https://hke.hellobike.cn/container-business-service/api/v1/apps/groups/appname/{}/env/6".format(service_name)
				
			elif env == "pre":
				groupsUrl = "https://hke.hellobike.cn/container-business-service/api/v1/apps/groups/appname/{}/env/9".format(service_name)
				
			else:
				groupsUrl = "https://hke.hellobike.cn/container-business-service/api/v1/apps/groups/appname/{}/env/2".format(service_name)
				
			# print(groupsUrl)
			us = UseMysql()
			headerInfos = us.getTokenInfos()
			headers = {"token": headerInfos[0],"user-agent":headerInfos[1],"x-access-token":headerInfos[0]}
			# print(headers)
			# print(env,groupsUrl)
			if env != "pre":
				grRep = Request().request_client(url=groupsUrl,method='get',headers=headers)
			else:
				grRep = (200,{"code":"ok","message":"查询成功","data":None})
			# print(grRep)
			if grRep[0] == 200:
				dataResult = grRep[1].get('data')
				if dataResult:
					if tag not in dataResult.get('groupList',[]):
						tag = "group1"
					groupList = dataResult.get('groupList',[])
					for group in groupList:
						if group == tag:
							break
					else:
						raise Exception("group1不存在")

				else:
					data = {"page":1,
					"env":env.upper(),
					"action":"tt.application.info.resource",
					"page_size":20,
					"type":"ECS"}
					ttRep = Request().request_client(url=ttGetEcsIpUrl,method='post',data=data,headers=headers)	
					# print(ttRep)
					if ttRep[0] == 200 and ttRep[1].get('data',[]):
						# 没有容器时 ，返回ecs_ip,没有ecs信息时，会往下获取容器IP
						ip = ttRep[1].get('data',[])[0].get('ip',{}).get('intranet','') 
						print(ip)
						return ip
						
			if env == "fat":
				containerUrl = "https://hke.hellobike.cn/container-business-service/api/v1/apps/pods/appname/{service_name}/env/6/group/{tag}".format(
				service_name=service_name,tag=tag)
			elif env == "pre":
				containerUrl = "https://hke.hellobike.cn/container-business-service/api/v1/apps/pods/appname/{service_name}/env/9/group/{tag}".format(
				service_name=service_name,tag=tag)
			else:
				containerUrl = "https://hke.hellobike.cn/container-business-service/api/v1/apps/pods/appname/{service_name}/env/2/group/{tag}".format(
				service_name=service_name,tag=tag)


			# print(containerUrl)

			cnRep = Request().request_client(url=containerUrl,method='get',headers=headers)
			# print (cnRep)

			if cnRep[0] == 200:
				ip = cnRep[1].get('data').get('appPodList',[])[0].get("ipAddress")
				print(ip)
				return ip

			return False
		except Exception as e:
			print(traceback.format_exc())
			raise Exception("请联系管理员")


	def exe_redis(self,name,command,env="uat",database=None):

		"""
			执行redis 命令
			env 不传默认为uat
			支持 pre,fat,uat
			自动分区的redis可不传database 
			
			返回内容为:
				执行结果

			例:
			|$(result) |exe redis | bikeAlias | get bikeServiceIp:2100170725 | env="uat"
		"""
		try:
			if env == "pre":
				getAllRedisNamesUrl = "https://basicconf-admin-server.hellobike.cn/redisConf/getAllRedisNames"
				getSelfRedisUrl = "https://basicconf-admin-server.hellobike.cn/redisQuery/getRedisList"
				addRedisTokenUrl = "https://basicconf-admin-server.hellobike.cn/redisQuery/addRedisTokenApplication"
				executeRedisUrl = "https://basicconf-admin-server.hellobike.cn/redisQuery/execute"
			else:
				getAllRedisNamesUrl = "https://{}-basicconf-admin-server.hellobike.cn/redisConf/getAllRedisNames".format(env)
				getSelfRedisUrl = "https://{}-basicconf-admin-server.hellobike.cn/redisQuery/getRedisList".format(env)
				addRedisTokenUrl = "https://{}-basicconf-admin-server.hellobike.cn/redisQuery/addRedisTokenApplication".format(env)
				executeRedisUrl = "https://{}-basicconf-admin-server.hellobike.cn/redisQuery/execute".format(env)
			
			selfHaveRedis = False

			us = UseMysql()
			headerInfos = us.getTokenInfos()
			headers = {"token": headerInfos[0],"user-agent":headerInfos[1]}

			allRedisRep = Request().request_client(url=getAllRedisNamesUrl,method='get',headers=headers)

			if allRedisRep[0] == 200:
				redisList = allRedisRep[1].get('data',[])
				for redisName in redisList:
					if name == redisName:
						break
				else:
					return  False#("没有传入的redis信息,请联系管理员")


			getSelfRedisRep = Request().request_client(url=getSelfRedisUrl,method='get',headers=headers)

			if getSelfRedisRep[0] == 200:
				selfRedisList = getSelfRedisRep[1].get('data',[])
				for selfRedis in selfRedisList:
					if selfRedis.get("redisName","") == name:
						selfHaveRedis = True

			if not selfHaveRedis:

				data = {"redisNameList":[name],
						"expireTime":2160,
						"commandList":["set","setnx","setex","psetex","del","incr","decr","lpush","lpop","rpush","rpop","lrem","sadd","srem","zadd","zrem","hset","hmset","hdel","hkeys","incrby","incrbyfloat","geoadd","get","exists","lrange","lindex","sismember","scard","smembers","zrange","zrangebyscore","hget","hmget","hkeys","hgetall","georadius","ttl","pttl","pexpire","pexpireat","persist","expire","expireat","scriptexists","eval","evalsha","scriptload","sadd","scard","sdiff","sdiffstore","sinter","sinterstore","sismember","smembers","spop","srandmember","srem","sscan","sunion","sunionstore","append","decrby","decr","del","exists","getrange","get","getset","incrbyfloat","incrby","incr","mget","msetnx","mset","psetex","scanbatch","scan","setex","setnx","setrange","set","strlen","geoadd","geodist","geohash","geopos","georadiusbymember","georadius","publish","type","info","lindex","llen","lrange","brpoplpush","blpop","brpop","linsert","lpop","lpush","lpushx","lrem","lset","ltrim","rpoplpush","rpop","rpush","rpushx","hexists","hgetall","hget","hkeys","hlen","hmget","hvals","hdel","hincrbyfloat","hincrby","hmset","hsetnx","hset","hscan","zadd","zcard","zcount","zincrby","zinterstore","zlexcount","zrangebylex","zrangebyscore","zrangebyscorewithscores","zrange","zrank","zremrangebylex","zremrangebyrank","zremrangebyscore","zrem","zrevrangebylex","zrevrangebyscore","zrevrangebyscorewithscores","zrevrange","zrevrank","zscan","zscore","zunionstore","pfadd","pfcount","pfmerge"]
						}

				addRedisRep = Request().request_client(url=addRedisTokenUrl,method='patch',data=data,headers=headers)

				print(addRedisRep)

				if addRedisRep[0] == 200:
					if addRedisRep[1]['code'] == 0:
						pass
					else:
						return False # 添加redis权限失败

			if database:
				executData = {"database":database,"redisName":name,"command":command}
			else:
				executData = {"redisName":name,"command":command}

			executRep = Request().request_client(url=executeRedisUrl,method='post',data=executData,headers=headers)

			print(executRep)

			if executRep[0] == 200:
				return executRep[1]

			return False
		except Exception as e:
			raise Exception("请联系管理员")


	# 查看到服务对应机器时，返回第一台机器对应的端口号(因为其他机器端口号一致)
	def get_server_port(self,service_name,env="pre"):
		"""
		获取指定服务对应的端口号
		service_name 服务名
		env 环境(fat,uat,pre) 不传默认pre
		"""
		print(env)
		requestUrl = "https://tt.hellobike.cn/v1/gateway"
		data = {"env": env.upper(), "action": "tt.soa.manage.group_list", "app_name": service_name}
		# if env == "pre":
		# 	# requestUrl = "https://soa-management.hellobike.com/group/listByName?serviceName={service_name}".format(service_name=service_name)
			
			
		# elif env =="uat":
		# 	# requestUrl = "https://{env}-soa-management.hellobike.com/group/listByName?serviceName={service_name}".format(env=env,service_name=service_name)
		# 	requestUrl = "http://hke.hellobike.cn/container-business-service/api/v1/soa/2/{service_name}/list".format(service_name=service_name)
		# elif env == "fat":
		# 	requestUrl = "http://hke.hellobike.cn/container-business-service/api/v1/soa/6/{service_name}/list".format(service_name=service_name)
		# else:
		# 	return "你输入的环境名不正确"

		us = UseMysql()
		headerInfos = us.getTokenInfos()

		headers = {"token": headerInfos[0],"user-agent":headerInfos[1]}

		rep = Request().request_client(url=requestUrl,method='post',data=data,headers=headers)
		# print (rep)
		if rep[0] == 200:
			data = rep[1]['data']
			if data:
				for sub in data: 
					#sub {serviceGuid: null, serviceName: "AppHellobikeRideApiService", groupName: "pre", groupStatus: 0,…}
					if sub.get('groupName','') == env:
						return sub['serverNodes'][0]['port']
				else:
					return "该服务没有pre信息"
			else:
				return "该服务没有查询到数据"
		else:
			return "请联系管理员"



if __name__ == '__main__':
	td = ThirdInfo()
	# print(td.get_container_ip("AppEvBizProcessService"))
	# print(td.get_container_ip("AppHellobikeRideApiService",env="uat",tag="djy-ac12abf4"))
	# print(td.get_container_ip("AppHellobikeBikeStateService",env="uat",tag="djy-ac12abf4"))
	# print(td.get_container_ip("AppHellobikeBikeStateService",env="uat")) #没有容器的服务
	# print(td.exe_redis("bikeAlias","get bikeServiceIp:2100170725",env="fat"))
	print(td.get_server_port("AppEvBizProcessService",env="pre"))
	# print(td.exe_redis("ride-support",'lpush userHistoryOrder:008b8de2351e40da89d3341c77069a4d   \"ill|{\\"orderType\\":0,\\"orderGuid\\":\\"15992962240511200169456\\",\\"createTime\\":1599296224051,\\"endPointLng\\":\\"85.2351789094\\",\\"endTime\\":1599296224051,\\"endPointLat\\":\\"29.3257264646\\",\\"inForbiddenType\\":3}\"'))
	# print(td.exe_redis("bikeuser-cluster",
	# 			"hmset sms:{phone} code 1234".format(phone="17051258210"),
	# 			env="pre"))
	# url = "http://uat-admin.hellobike.com:40001/systemUser/getLoginUserInfo"
	# headers={'token':"accb5e22aab633bf034b74598a154614",'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"}
	# rep = Request().request_client(url=url,method='post',headers=headers)
	# print(rep)



