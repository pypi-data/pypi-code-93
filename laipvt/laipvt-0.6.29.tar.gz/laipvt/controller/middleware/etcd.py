from __future__ import absolute_import
from __future__ import unicode_literals

import requests
from laipvt.interface.middlewareinterface import MiddlewareInterface
from laipvt.handler.confighandler import CheckResultHandler
from laipvt.handler.middlewarehandler import EtcdConfigHandler
from laipvt.sysutil.util import ssh_obj, log, status_me


class EtcdController(MiddlewareInterface):
	def __init__(self, result: CheckResultHandler, handler: EtcdConfigHandler, template: str):
		super(EtcdController, self).__init__(result, handler, template)
		self.etcd_cfg = EtcdConfigHandler().get_config_with_check_result()
		self.etcd_cfg["etcd"]["ipaddress"] = self.handler.cfg["ipaddress"]

	def _generic_config(self):
		log.info("渲染 Etcd 配置文件")
		if len(self.master_server) == 1:
			log.info("使用单机模式部署")
			self.etcd_cfg["is_standalone"] = True
		elif len(self.master_server) == 3:
			log.info("使用集群模式部署")
			self.etcd_cfg["is_standalone"] = False
		else:
			log.info("集群模式需要3台主机,请检查前置检查配置是否正确")
			exit()
		for num_id in range(len(self.master_server)):
			self.etcd_cfg["etcd"]["etcd_num"] = "etcd%s" % (num_id + 1)
			self.etcd_cfg["etcd"]["ip"] = self.master_server[num_id].ipaddress
			self.generate_docker_compose_file(self.etcd_cfg)
			self._send_docker_compose_file(self.master_server[num_id])


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

	def _check(self):
		super().wait_for_service_start()
		for i in range(len(self.master_server)):
			try:
				log.info("检查 {IP}:{PORT} 上的 Etcd 健康性...".format(
					IP=self.master_server[i].ipaddress, PORT=self.etcd_cfg["etcd"]["http_port"]))
				requests.get(
					"http://{IP}:{PORT}/version".format(
						IP=self.master_server[i].ipaddress, PORT=self.etcd_cfg["etcd"]["http_port"]
					)
				)
				log.info("Etcd检查通过")
			except Exception as e:
				log.error(e)
				log.error("{IP}:{PORT} 上的 Etcd 服务异常".format(
					IP=self.master_server[i].ipaddress), PORT=self.etcd_cfg["etcd"]["http_port"])
				exit(2)

	@status_me("middleware")
	def deploy_etcd(self):
		self._generic_config()
		self.start()
		self._check()

	def deploy(self):
		self.deploy_etcd()
