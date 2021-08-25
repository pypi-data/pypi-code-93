from __future__ import absolute_import
from __future__ import unicode_literals

import pymongo
import requests
from laipvt.interface.middlewareinterface import MiddlewareInterface
from laipvt.handler.middlewarehandler import SiberConfigHandler
from laipvt.handler.confighandler import CheckResultHandler
from laipvt.sysutil.template import FileTemplate
from laipvt.sysutil.util import path_join, ssh_obj, log, status_me
from laipvt.model.cmd import ComposeModel
from laipvt.sysutil.siber_main import Mage_test


class SiberController(MiddlewareInterface):
	def __init__(self, result: CheckResultHandler, handler: SiberConfigHandler, template: str):
		super(SiberController, self).__init__(result, handler, template)
		self.conf_tmp = path_join("/tmp")
		self.conf_template = path_join(self.template)
		self.conf_file = path_join(self.base_dir, "config")
		self.list_conf = ("siber.conf", "siber-web.conf", "siber-nginx.conf")
		self.mongo_data_source = path_join(self.template, "siber_mongo")
		self.mongo_data_remote = path_join(self.base_dir, "siber_mongo")
		self.siber_cfg = SiberConfigHandler().get_all_config_with_check_result()
		self.siber_cfg["siber"] = SiberConfigHandler().get_config_with_check_result()["siber"]
		self.siber_cfg["siber"]["ipaddress"] = self.handler.cfg["ipaddress"]
		self.siber_host = self.master_server[0].ipaddress
		self.tagid_list = []
		self.casid_list = []
		self.casid_basic_list = []

	def _generic_config(self):
		log.info("渲染 Siber 配置文件")
		for num_id in range(len(self.list_conf)):
			dest = path_join(self.conf_template, self.list_conf[num_id])
			src_tmp = path_join(self.conf_tmp, self.list_conf[num_id])
			src = path_join(self.conf_file, self.list_conf[num_id])
			FileTemplate(self.siber_cfg, dest, src_tmp).fill()
			self.send_config_file(self.master_server[0], src_tmp, src)
		self.send_config_file(self.master_server[0], self.mongo_data_source, self.mongo_data_remote)
		self.generate_docker_compose_file(self.siber_cfg)
		self._send_docker_compose_file(self.master_server[0])

	def _send_docker_compose_file(self, host):
		log.info("分发%s docker-compose配置文件至 %s" % (self.middleware_name, host.ipaddress))
		ssh_cli = ssh_obj(ip=host.ipaddress, user=host.username, password=host.password, port=host.port)
		try:
			ssh_cli.put(self.docker_compose_file_tmp, self.docker_compose_file)
		except Exception as e:
			log.error(e)
			exit(2)
		finally:
			ssh_cli.close()

	def _init_siber(self):
		super().wait_for_service_start()
		log.info("初始化 siber-mongo 数据")
		try:
			init_mongo_cmd = "docker exec siber-mongo mongorestore -u admin -p admin -d admin siber_mongo/siber"
			server = self.master_server[0]
			ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
			res = ssh_cli.run_cmd(init_mongo_cmd)
			if res["code"] != 0:
				log.error("初始化 siber-mongo 数据失败:{}".format(res["stderr"]))
			else:
				log.info("初始化 siber-mongo 数据成功")
		except Exception as e:
			log.error(e)
			log.error("初始化mongo数据失败")

	def _start(self):
		compose_cmd = ComposeModel(self.docker_compose_file)
		for server in self.master_server[:1]:
			log.info("启动 %s: %s服务" % (server.ipaddress, self.middleware_name))
			ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
			try:
				res = ssh_cli.run_cmd(compose_cmd.up())
				if res["code"] == 0:
					log.info("启动 %s %s 服务成功" % (server.ipaddress, self.middleware_name))
				else:
					log.error("启动 %s %s 服务失败: %s " % (server.ipaddress, self.middleware_name, res["stdout"]))
			except Exception as e:
				log.error(e)
			finally:
				ssh_cli.close()

	def _check(self):
		super().wait_for_service_start()
		for server in self.master_server[:1]:
			res = self.check_port(server.ipaddress, self.siber_cfg["siber"]["port"])
			if res:
				log.info("机器:{} Siber-nginx代理端口{}访问正常".format(server.ipaddress, self.siber_cfg["siber"]["port"]))
			else:
				log.error("机器:{} Siber-nginx代理端口{}访问异常".format(server.ipaddress, self.siber_cfg["siber"]["port"]))

	def send_request(self, url, data):
		resp = requests.post(url=url, json=data)
		result = resp.json()
		return result

	def run_plan(self, plan_id):
		data = {
			"plan_info": {
				"plan_id": plan_id
			},
			"trigger_condition": {
				"environment_name": "prod"
			}
		}
		url = "http://{}:{}/siberhttp/run/plan".format(self.siber_host, self.siber_cfg["siber"]["port"])

		return self.send_request(url, data)

	def update_planversion(self, plan_version):
		data = {
			"manage_mode": "UPDATE",
			"plan_info": {
				"plan_name": "私有部署定制化mage plan",
				"interface_type": "http",
				"environment_name": "测试环境",
				"environment_id": "5e940f347dcd1000016d8378",
				"threads": 0,
				"flow_list": [
					"5f1926a438cb970001f5a936"
				],
				"plan_id": "5f1926b438cb970001f5a93d",
				"version_control": plan_version
			}
		}
		url = "http://{}:{}/siberhttp/manage/plan".format(self.siber_host, self.siber_cfg["siber"]["port"])
		return self.send_request(url, data)

	def update_basic_planversion(self, plan_version):
		data = {
			"manage_mode": "UPDATE",
			"plan_info": {
				"plan_name": "【Mage】Basic测试",
				"interface_type": "http",
				"environment_name": "测试环境",
				"environment_id": "5e940f347dcd1000016d8378",
				"threads": 0,
				"flow_list": [
					"60f140a5300d210001320076"
				],
				"plan_id": "5f8ecd1cb2b9fd0001c31217",
				"version_control": plan_version
			}
		}
		url = "http://{}:{}/siberhttp/manage/plan".format(self.siber_host, self.siber_cfg["siber"]["port"])
		return self.send_request(url, data)

	def replace_mage_collection_tag(self, tag_id):
		'''
		根据tag列表到mongo中取出tagid
		根据tagid将case取出
		将case到如到指定的flow中
		'''
		try:
			self.mongo_client = pymongo.MongoClient("mongodb://{}:27027/".format(self.siber_host))
			self.my_db = self.mongo_client.admin
			self.auth = self.my_db.authenticate("admin", "admin", mechanism='SCRAM-SHA-1')
			for tag_id in self.my_db.collection_tag.find({"tagname": {"$in": tag_id}}):
				self.tagid_list.append(tag_id["tagid"])
			for cas_tags in self.tagid_list:
				for res in self.my_db.collection_case.find({"$and": [{"casetags": cas_tags}, {"invaliddate": 0}]}):
					if "BASIC" not in res["casename"]:
						self.casid_list.append(res["_id"])
					elif "BASIC" in res["casename"]:
						self.casid_basic_list.append(res["_id"])
			self.my_db.collection_flow.update({"flowid": "5f1926a438cb970001f5a936"}, {"$set": {"caselist": self.casid_list}})
			self.my_db.collection_flow.update({"flowid": "60f140a5300d210001320076"}, {"$set": {"caselist": self.casid_basic_list}})
			self.run_mage_siber_test()
		except Exception as e:
			log.error(e)
			exit(2)

	def run_mage_siber_test(self):
		try:
			log.info("替换 Siber env,oss 配置")
			Mage_test(self.siber_host).replace_private_oss_url()
			Mage_test(self.siber_host).update_private_mage_env_info()
			self.update_planversion("v1.15")
			self.update_basic_planversion("v1.15")
			self.run_plan("5f1926b438cb970001f5a93d")
			self.run_plan("5f8ecd1cb2b9fd0001c31217")
			log.info("请检查集成测试平台 '私有部署定制化mage plan' 运行结果")
			log.info("集成测试平台访问地址http://{}:88".format(self.siber_host))
		except Exception as e:
			log.error(e)
			exit(2)

	@status_me("middleware")
	def deploy_siber(self):
		self._generic_config()
		self._start()
		self._init_siber()
		self._check()
