#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import json
from laipvt.sysutil.gvalue import CHECK_FILE, PROJECT_INFO_FILE
from laipvt.sysutil.util import find
from laipvt.handler.confighandler import CheckResultHandler
from laipvt.handler.packagehandler import DeployPackageHandler
from laipvt.controller.kubernetes.kube import KubeController
from laipvt.controller.middleware.harbor import HarborController
from laipvt.controller.middleware.nginx import NginxController
from laipvt.controller.middleware.etcd import EtcdController
from laipvt.controller.middleware.minio import MinioController
from laipvt.controller.middleware.redis import RedisController
from laipvt.controller.middleware.mysql import MysqlController
from laipvt.controller.middleware.elasticsearch import EsController
from laipvt.controller.middleware.rabbitmq import RabbitmqController
from laipvt.controller.middleware.identity import IdentityController
from laipvt.controller.middleware.siber import SiberController
from laipvt.controller.service.license import LicenseController
from laipvt.controller.service.mage import MageController
from laipvt.controller.service.ocr_standard import OcrStandardController
from laipvt.controller.service.nlp import NlpController
from laipvt.controller.service.seal import SealController
from laipvt.controller.service.captcha import CaptchaController
from laipvt.controller.service.commander import CommanderController
from laipvt.controller.service.ocr import OcrController
from laipvt.controller.middleware.monitor import MonitorController
from laipvt.controller.middleware.keepalived import KeepalivedController
from laipvt.handler.middlewarehandler import EtcdConfigHandler, MysqlConfigHandler, EsConfigHandler, \
    MinioConfigHandler, RabbitmqConfigHandler, RedisConfigHandler, HarborConfigHandler, NginxConfigHandler, \
    IdentityConfigHandler, SiberConfigHandler, OcrConfigHandler, MonitorConfigHandler, KeepalivedConfigHandler
from laipvt.sysutil.relation import module_require_tfserver, tfserver_name, tfserver_image_name
from laipvt.sysutil.util import write_to_file, read_form_json_file, gen_https_self_signed_ca
from laipvt.sysutil.kube_common import wait_pod_running
from laipvt.sysutil.check import is_pre_check, check_use_https_ca, check_https_ca_self_signed

def deploy_main(args):
    if not args.isCheck:
        if not is_pre_check():
            print("ERROR: 未执行前置检查或前置检查失败")
            exit(1)

    if not check_use_https_ca():
        print("Error: 使用https部署，选择的是客户提供证书，证书路径不正确")
        exit(1)

    if check_https_ca_self_signed():
        gen_https_self_signed_ca()

    # 获取前置检查结果
    check_result_file = CHECK_FILE
    check_result = CheckResultHandler(check_result_file)

    if args.targzFile:
        pkg_path = False
        if not os.path.exists(args.targzFile):
            cwd = [os.getcwd(), check_result.deploy_dir]
            for d in cwd:
                pkg_path = find(d, args.targzFile, file=True)
                if pkg_path:
                    break
        else:
            pkg_path = os.path.join(os.getcwd(), args.targzFile)
        if not pkg_path:
            print("未找到文件")
            exit(1)
        PKG = os.path.dirname(pkg_path)
        ID = os.path.basename(pkg_path).split(".")[0]
        PKG_DIR = pkg_path.split(".")[0]

        # 将项目ID和path写入文件缓存
        project_dict = { "PKG": PKG, "ID": ID }
        write_to_file(PROJECT_INFO_FILE, json.dumps(project_dict, indent=4))

        deploy_package = DeployPackageHandler(PKG, ID)
        if not os.path.exists(PKG_DIR):
            deploy_package.unpack()
        # 解析
        parse_package = deploy_package.parse()
        kubernetes_package = parse_package.kubernetes
        middleware_package = parse_package.middleware
        harbor_package = parse_package.harbor

        if not os.path.exists(os.path.join(PKG_DIR, "kubernetes")):
            kubernetes_package.kubernetes_unpack()
        if not os.path.exists(os.path.join(PKG_DIR, "middleware")):
            middleware_package.unpack()
        if not os.path.exists(os.path.join(PKG_DIR, "harbor")):
            harbor_package.unpack()

        # install harbor
        haror_path = harbor_package.parse().harbor
        harbor_config = HarborConfigHandler()
        harbor = HarborController(check_result, harbor_config, haror_path)
        harbor.install_harbor()

        # install nginx
        nginx_package = middleware_package.parse().nginx
        nginx_config = NginxConfigHandler()
        nginx = NginxController(check_result, nginx_config, nginx_package)
        nginx.install_nginx()

        # install kubernetes
        kube_info = kubernetes_package.parse()
        kube = KubeController(check_result, kube_info)
        kube.add_hosts()
        kube.system_prepare()
        kube.init_primary_master()
        kube.cp_kube_config()
        kube.kube_completion()
        kube.install_network_plugin()
        kube.join_master()
        kube.join_node()
        kube.install_helm()
        kube.install_istio()
        # 更新nginx服务tcp代理apiserever cluster
        nginx.renew_apiserver_config()


        # install service
        services = {
            "mage": MageController,
            "commander": CommanderController,
            "nlp": NlpController,
            "captcha": CaptchaController,
            "ocr_standard": OcrStandardController,
            "ocr": OcrController,
            "ocr_seal_server": SealController
        }

        middlewares = {
            "etcd": (EtcdConfigHandler, EtcdController),
            "minio": (MinioConfigHandler, MinioController),
            "redis": (RedisConfigHandler, RedisController),
            "mysql": (MysqlConfigHandler, MysqlController),
            "es": (EsConfigHandler, EsController),
            "rabbitmq": (RabbitmqConfigHandler, RabbitmqController),
            # "identity": (IdentityConfigHandler, IdentityController)
        }

        for s in parse_package.service:
            if not os.path.exists(os.path.join(PKG_DIR, s.project_name)):
                s.unpack()
            service_path = s.parse()

            # 遍历服务需要的中间件，依次安装
            middleware_list = service_path.config.middleware
            middleware_list.insert(0, "etcd")

            for mid in middleware_list:
                path = middleware_package.parse()[mid]
                config = middlewares[mid][0]()
                middleware = middlewares[mid][1](check_result, config, path)
                middleware.deploy()

            # install identity
            identity_path = middleware_package.parse().identity
            identity_config = IdentityConfigHandler()
            identity = IdentityController(check_result, identity_config, identity_path)
            identity.deploy_identity()

            # install license
            license_package = parse_package.license
            if not os.path.exists(os.path.join(PKG_DIR, "license")):
                license_package.unpack()
            license_path = license_package.parse()
            license = LicenseController(check_result, license_path)
            license.deploy_license()

            if s.project_name == "ocr":
                ocr_handler = OcrConfigHandler()
                deploy_service = services[s.project_name](service_path, check_result, ocr_handler, s.root_dir)
            else:
                deploy_service = services[s.project_name](check_result, service_path)
            if s.project_name == "commander":
                identity_path = middleware_package.parse().identity
                identity_config = IdentityConfigHandler()
                identity = IdentityController(check_result, identity_config, identity_path)
                identity.update_identity_config()
            deploy_service.run()

            # tf-server
            if s.project_name in module_require_tfserver:
                for module_name in tfserver_name[s.project_name]:
                    deploy_service.deploy_tf_service(module_name, tfserver_image_name[s.project_name])

        # check all pod status
        if not wait_pod_running:
            print("kubernetes集群中有pod启动状态异常，请检查: kubectl get pod -A")
            exit(2)

        # install siber
        siber_path = middleware_package.parse().siber
        siber_config = SiberConfigHandler()
        siber = SiberController(check_result, siber_config, siber_path)
        siber.deploy_siber()
        for s in parse_package.service:
            if s.project_name == "mage":
                siber.replace_mage_collection_tag(parse_package.config.siber_tags)
            elif s.project_name == "commander":
                exit()

    if args.which == "license":
        if args.LicenseFile:
            if os.path.exists(args.LicenseFile):
                # print(args.LicenseFile)
                project_dict = read_form_json_file(PROJECT_INFO_FILE)

                # 解析大包
                deploy_package = DeployPackageHandler(project_dict["PKG"], project_dict["ID"])
                parse_package = deploy_package.parse()
                license_package = parse_package.license
                # license_package.unpack()
                license_path = license_package.parse()
                license = LicenseController(check_result, license_path)
                license.renew_license(license_file=args.LicenseFile)
            else:
                print("请检查指定的新授权文件是否存在: {}".format(args.LicenseFile))
                exit(1)

        if args.OcrLicenseFile:
            if os.path.exists(args.OcrLicenseFile):
                project_dict = read_form_json_file(PROJECT_INFO_FILE)

                deploy_package = DeployPackageHandler(project_dict["PKG"], project_dict["ID"])
                parse_package = deploy_package.parse()
                renew_flag = False
                for s in parse_package.service:
                    if s.project_name == "ocr":
                        service_path = s.parse()
                        ocr_handler = OcrConfigHandler()
                        deploy_ocr = OcrController(service_path, check_result, ocr_handler, s.root_dir)
                        deploy_ocr.renew_license(license_file=args.OcrLicenseFile)
                        renew_flag = True

                if not renew_flag:
                    print("OCR license未更新成功，请检查是否存在合合服务")
                    exit(2)

    if args.which == "add":
        if args.Monitor:
            project_dict = read_form_json_file(PROJECT_INFO_FILE)
            deploy_package = DeployPackageHandler(project_dict["PKG"], project_dict["ID"])
            parse_package = deploy_package.parse()
            middleware_package = parse_package.middleware

            monitor_path = middleware_package.parse().monitor
            monitor_config = MonitorConfigHandler()
            monitor = MonitorController(check_result, monitor_config, monitor_path)
            monitor.deploy_monitor()

        if args.Keepalive:
            project_dict = read_form_json_file(PROJECT_INFO_FILE)
            deploy_package = DeployPackageHandler(project_dict["PKG"], project_dict["ID"])
            parse_package = deploy_package.parse()
            middleware_package = parse_package.middleware

            keepalive_path = middleware_package.parse().keepalived
            keepalive_config = KeepalivedConfigHandler()
            keepalive = KeepalivedController(check_result, keepalive_config, keepalive_path)
            keepalive.deploy_keepalived()
