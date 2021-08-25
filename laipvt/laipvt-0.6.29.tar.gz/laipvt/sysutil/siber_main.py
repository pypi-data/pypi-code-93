import json
import re
import grpc
import requests
from google.protobuf.json_format import MessageToJson
from laipvt.sysutil.dboperation_pb2 import DbOperationRequest
from laipvt.sysutil.dboperation_pb2_grpc import DbOperationServiceStub
from laipvt.sysutil.gvalue import LAIPVT_BASE_DIR
from laipvt.sysutil.conf import YamlConfig
from laipvt.sysutil.util import path_join
from laipvt.sysutil.conf import AccountIdConfig
from tenacity import retry, wait_fixed, stop_after_attempt, stop_after_delay


class Mage_test(object):
    def __init__(self, ip):
        self.cfg = YamlConfig(path_join(LAIPVT_BASE_DIR, "middleware"), suffix="yaml").read_dir()
        self.minio_port = self.cfg["minio"]["port"]
        self.mage_port = self.cfg["nginx"]["mage_proxy_port"]
        self.mage_url = "http://{}:{}".format(ip, self.mage_port)
        self.private_siber_host = "http://{}:88".format(ip)
        self.private_oss_url = "http://{}:{}/laiye-im-saas/document-mining-backend".format(ip, self.minio_port)
        self.grpc_url = "{}:31380".format(ip)
        self.account_id = AccountIdConfig().get()

    @retry(stop=stop_after_delay(300), wait=wait_fixed(2), reraise=True)
    def update_private_mage_env_info(self):
        env_info = {
            "manage_mode": "UPDATE",
            "env_info": {
                "env_name": "UiBotMage",
                "grpc": {"dev_envoy": "", "test_envoy": ""},
                "http": {
                    "dev_url": self.mage_url,
                    "test_url": self.mage_url,
                    "stage_url": self.mage_url,
                    "prod_url": self.mage_url,
                },
                "env_id": "5e940f347dcd1000016d8378",
                "insert_time": "1586761524",
                "env_mode": "interface",
                "secret_list": [],
            },
        }
        new_data = [
            {"secret_name": "通用文字识别—高速版", "app_name": "测试平台专用-文字-高速"},
            {"secret_name": "通用表格识别—高速版", "app_name": "测试平台专用-表格-高速"},
            {"secret_name": "通用多卡证识别——高速版", "app_name": "测试平台专用-智能-高速"},
            {"secret_name": "通用多票据识别——高速版", "app_name": "测试平台专用-票据-高速"},
            {"secret_name": "自定义模板识别-高速版", "app_name": "自定义模板识别-文字-高速"},
            {"secret_name": "验证码识别GENERAL", "app_name": "测试平台专用-GENERAL"},
            {"secret_name": "自定义模板识别-高精版", "app_name": "自定义模板识别-文字-高精"},
            {"secret_name": "通用文字识别—标准版", "app_name": "测试平台专用-文字-标准"},
            {"secret_name": "通用文字识别—经济版", "app_name": "测试平台专用-文字-经济"},
            {"secret_name": "通用文字识别—高精版", "app_name": "测试平台专用-文字-高精"},
            {"secret_name": "通用表格识别—标准版", "app_name": "测试平台专用-表格-标准"},
            {"secret_name": "通用表格识别—经济版", "app_name": "测试平台专用-表格-经济"},
            {"secret_name": "通用表格识别—高精版", "app_name": "测试平台专用-表格-高精"},
            {"secret_name": "文本匹配-标准版", "app_name": "测试平台专用-文本-标准"},
            {"secret_name": "验证码识别BCM", "app_name": "测试平台专用-BCM"},
            {"secret_name": "验证码识别CZB", "app_name": "测试平台专用-CZB"},
            {"secret_name": "验证码识别ICBC", "app_name": "测试平台专用-ICBC"},
            {"secret_name": "验证码识别PAB", "app_name": "测试平台专用-PAB"},
            {"secret_name": "验证码识别HZCB", "app_name": "测试平台专用-HZCB"},
            {"secret_name": "验证码识别GXRCU", "app_name": "测试平台专用-GXRCU"},
            {"secret_name": "标准地址-标准版", "app_name": "测试平台专用-地址-标准"},
            {"secret_name": "文本分类-基本版", "app_name": "测试平台专用-文本分类-基本"},
            {"secret_name": "文本分类-智能版", "app_name": "测试平台专用-文本分类-智能"},
            {"secret_name": "信息抽取—标准版", "app_name": "测试平台专用-抽取-标准"},
            {"secret_name": "语音合成-标准版", "app_name": "测试平台专用-语音合成-标准"},
            {"secret_name": "自定义模板识别-标准版", "app_name": "自定义模板识别-文字-标准"},
            {"secret_name": "自定义模板识别-高速版-表格", "app_name": "自定义模板识别-表格-高速"},
            {"secret_name": "自定义模板识别-高精版-表格", "app_name": "自定义模板识别-表格-高精"},
            {"secret_name": "通用多卡证识别—银行卡-高速版", "app_name": "测试平台专用-银行卡-高速"},
            {"secret_name": "通用多卡证识别—名片-高速版", "app_name": "测试平台专用-名片-高速"},
            {"secret_name": "通用多卡证识别—香港身份证-高速版", "app_name": "测试平台专用-香港身份证-高速"},
            {"secret_name": "通用多卡证识别—身份证-高速版", "app_name": "测试平台专用-身份证-高速"},
            {"secret_name": "通用多卡证识别—社保卡-高速版", "app_name": "测试平台专用-社保卡-高速"},
            {"secret_name": "通用多卡证识别—车辆登记证-高速版", "app_name": "测试平台专用-车辆登记证-高速"},
            {"secret_name": "通用多卡证识别—驾驶证-高速版", "app_name": "测试平台专用-驾驶证-高速"},
            {"secret_name": "通用多卡证识别—行驶证-高速版", "app_name": "测试平台专用-行驶证-高速"},
            {"secret_name": "通用多卡证识别—户口本-高速版", "app_name": "测试平台专用-户口本-高速"},
            {"secret_name": "通用多卡证识别—护照-高速版", "app_name": "测试平台专用-护照-高速"},
            {"secret_name": "通用多卡证识别—结婚证-高速版", "app_name": "测试平台专用-结婚证-高速"},
            {"secret_name": "通用多卡证识别—车辆合格证-高速版", "app_name": "测试平台专用-车辆合格证-高速"},
            {"secret_name": "通用多卡证识别—组织机构代码证-高速版", "app_name": "测试平台-组织机构代码证-高速"},
            {"secret_name": "通用多卡证识别—税务登记证-高速版", "app_name": "测试平台专用-税务登记证-高速"},
            {"secret_name": "通用多卡证识别—开户许可证-高速版", "app_name": "测试平台专用-开户许可证-高速"},
            {"secret_name": "通用多卡证识别—营业执照-高速版", "app_name": "测试平台专用-营业执照-高速"},
            {"secret_name": "通用多卡证识别—不动产证-高速版", "app_name": "测试平台专用-不动产证-高速"},
            {"secret_name": "通用多卡证识别—房产证-高速版", "app_name": "测试平台专用-房产证-高速"},
            {"secret_name": "通用多卡证识别—离婚证-高速版", "app_name": "测试平台专用-离婚证-高速"},
            {"secret_name": "自定义模板识别-经济版", "app_name": "自定义模板识别-文字-经济"},
            {"secret_name": "自定义模板识别-经济版-表格", "app_name": "自定义模板识别-表格-经济"},
            {"secret_name": "自定义模板识别-一键多值测试", "app_name": "一键多值测试"},
            {"secret_name": "自定义模板识别-预处理资源", "app_name": "自定义模板识别-预处理-高配"},
            {"secret_name": "通用多票据识别-票据-高级版CPU", "app_name": "测试平台专用-票据-CPU"},
            {"secret_name": "通用多票据识别-票据-高级版GPU", "app_name": "测试平台专用-票据-GPU"},
            {"secret_name": "通用多卡证识别-银行卡-高级版GPU", "app_name": "测试平台专用-银行卡-GPU"},
            {"secret_name": "通用多卡证识别-银行卡-高级版CPU", "app_name": "测试平台专用-银行卡-CPU"},
            {"secret_name": "通用多卡证识别-身份证-高级版CPU", "app_name": "测试平台专用-身份证-CPU"},
            {"secret_name": "通用多卡证识别-行驶证-高级版CPU", "app_name": "测试平台专用-行驶证-CPU"},
            {"secret_name": "通用多卡证识别-营业执照-高级版CPU", "app_name": "测试平台专用-营业执照-CPU"},
            {"secret_name": "通用多卡证识别-车辆登记证-高级版CPU", "app_name": "测试平台专用-车辆登记证CPU"},
            {"secret_name": "通用多卡证识别-身份证-高级版GPU", "app_name": "测试平台专用-身份证-GPU"},
            {"secret_name": "通用多卡证识别-行驶证-高级版GPU", "app_name": "测试平台专用-行驶证-GPU"},
            {"secret_name": "通用多卡证识别-营业执照-高级版GPU", "app_name": "测试平台专用-营业执照-GPU"},
            {"secret_name": "通用多卡证识别-车辆登记证-高级版GPU", "app_name": "测试平台专用-车辆登记证GPU"},
            {"secret_name": "印章识别-高级版", "app_name": "测试平台专用-印章识别-高级版"},
            {"secret_name": "印章识别-标准版", "app_name": "测试平台专用-印章识别-标准版"},
            {"secret_name": "通用文字识别-探智立方", "app_name": "测试平台专用-文字-探智立方"},
            {"secret_name": "通通用表格识别-探智立方", "app_name": "测试平台专用-表格-探智立方"},
            {"secret_name": "通用多票据识别-探智立方", "app_name": "测试平台-票据-探智立方GPU"},
            {"secret_name": "通用卡证-身份证-探智立方", "app_name": "通用卡证-身份证-探智立方"},
            {"secret_name": "自定义模板-探智立方", "app_name": "自定义模板-探智立方"},
            {"secret_name": "红头文件-高级版", "app_name": "红头文件-高级版"},
            {"secret_name": "招标公告-高级版", "app_name": "招标公告-高级版"},
            {"secret_name": "简历-高级版", "app_name": "简历-高级版"},
            {"secret_name": "简历-标准版", "app_name": "简历-标准版"},
            {"secret_name": "红头文件-标准版", "app_name": "红头文件-标准版"},
            {"secret_name": "招标公告-标准版", "app_name": "招标公告-标准版"},
            {"secret_name": "简历-高级版CPU", "app_name": "简历-高级版CPU"},
            {"secret_name": "简历-高级版GPU", "app_name": "简历-高级版GPU"},
            {"secret_name": "简历-探智立方GPU", "app_name": "简历-探智立方GPU"},
            {"secret_name": "红头文件-高级版CPU", "app_name": "红头文件-高级版CPU"},
            {"secret_name": "红头文件-高级版GPU", "app_name": "红头文件-高级版GPU"},
            {"secret_name": "红头文件-探智立方GPU", "app_name": "红头文件-探智立方GPU"},
            {"secret_name": "招标公告-高级版CPU", "app_name": "招标公告-高级版CPU"},
            {"secret_name": "招标公告-高级版GPU", "app_name": "招标公告-高级版GPU"},
            {"secret_name": "招标公告-探智立方GPU", "app_name": "招标公告-探智立方GPU"},
            {"secret_name": "合同比对-标准版", "app_name": "合同比对-标准版"},
            {"secret_name": "合同比对-高级版", "app_name": "合同比对-高级版"},
            {"secret_name": "合同比对-高级版-CPU", "app_name": "合同比对-高级版-CPU"},
            {"secret_name": "合同比对-高级版-GPU", "app_name": "合同比对-高级版-GPU"},
            {"secret_name": "合同比对-探智立方GPU", "app_name": "合同比对-探智立方GPU"},
            {"secret_name": "通用卡证-营业执照-探智立方", "app_name": "通用卡证-营业执照-探智立方"}
        ]
        # Connect to the database
        with grpc.insecure_channel(self.grpc_url) as channel:
            stub = DbOperationServiceStub(channel)
            response = stub.Operate(
                DbOperationRequest(
                    sql="SELECT name, app_key , app_secret  FROM tbl_docuds_app where is_deleted=0 and account_id = %s"
                    % self.account_id
                )
            )
            #docUnderstanding.DbOperationService
            #docUnderstanding.InnerService
            response = (
                MessageToJson(response, True, True, 2, True, False)
                .encode("ascii")
                .decode("unicode_escape")
            )
            response = json.loads(response)
            app_info_list = []
            for i in response["records"]:
                app_info = {}
                for j in range(len(response["fields"])):
                    (app_info.update({response["fields"][j]["key"]: i["values"][j]}))
                app_info_list.append(app_info)

        all_list = []
        for i in app_info_list:
            for j in new_data:
                if i["name"] == j["app_name"]:
                    secret_info = {
                        "secret_name": j["secret_name"],
                        "secret_info": {
                            "dev_secret": {
                                "pubkey": i["app_key"],
                                "secret": i["app_secret"],
                            },
                            "test_secret": {
                                "pubkey": i["app_key"],
                                "secret": i["app_secret"],
                            },
                            "stage_secret": {
                                "pubkey": i["app_key"],
                                "secret": i["app_secret"],
                            },
                            "prod_secret": {
                                "pubkey": i["app_key"],
                                "secret": i["app_secret"],
                            },
                        },
                    }
                    all_list.append(secret_info)
        env_info["env_info"].update({"secret_list": all_list})
        # print(env_info)
        response = requests.post(
            url=self.private_siber_host + "/siberhttp/manage/env", json=env_info
        )
        response_data = json.dumps(
            response.json(), sort_keys=True, indent=2, ensure_ascii=False
        )
        # print(response_data)
    # def download_oss_to_local_file():
    #     siber_host = "http://siber.wul.ai"
    #     directory = os.path.exists("../data")
    #     if not directory:
    #         os.mkdir(os.getcwd() + "/data")
    #     data = {"filter_content": {"content": "Mage", "page": "1", "page_size": "2000"}}
    #     response = requests.post(url=siber_host + "/siberhttp/list/case", json=data).json()
    #     case_info_list = response["case_info_list"]
    #     for i in case_info_list:
    #         data = {"manage_mode": "QUERY", "case_info": {"case_id": i["case_id"]}}
    #         response = requests.post(
    #             url=siber_host + "/siberhttp/manage/case", json=data
    #         ).json()
    #         for j in response["case_version"]:
    #             if "request_body" not in j.keys():
    #                 continue
    #             info = j["request_body"]
    #             if "{{FUNCTION.base_64" in info:
    #                 if download_file is True:
    #                     n = re.findall(r"{{FUNCTION.base_64\((.+?)\)}}", info)
    #                     file_name = n[0].split("/")[-1]
    #                     downloaded_obj = requests.get(n[0])
    #                     print(n[0])
    #                     with open("data/" + file_name, "wb") as file:
    #                         file.write(downloaded_obj.content)

    def replace_private_oss_url(self):
        data = {"filter_content": {"content": "Mage", "page": "1", "page_size": "2000"}}
        response = requests.post(
            url=self.private_siber_host + "/siberhttp/list/case", json=data
        ).json()
        case_info_list = response["case_info_list"]
        for i in case_info_list:
            data = {"manage_mode": "QUERY", "case_info": {"case_id": i["case_id"]}}
            response = requests.post(
                url=self.private_siber_host + "/siberhttp/manage/case", json=data
            ).json()
            # print(response)
            for j in response["case_version"]:
                if "request_body" not in j.keys():
                    continue
                info = j["request_body"]
                if "{{FUNCTION.base_64" in info:
                    n = re.findall(r"{{FUNCTION.base_64\((.+?)\)}}", info)
                    file_name = n[0].split("/")[-1]
                    new_oss_path = self.private_oss_url + "/" + file_name
                    # print(new_oss_path)
                    request_body = j["request_body"].replace(n[0], new_oss_path)
                    j["request_body"] = request_body
                    for case_version in response["case_version"]:
                        new_request = {
                            "manage_mode": "UPDATE",
                            "case_version": case_version,
                        }
                        # print("request_body:")
                        # print(new_request)
                        try:
                            response = requests.post(
                                url=self.private_siber_host + "/siberhttp/manage/case/version",
                                json=new_request,
                            )
                        except Exception as e:
                            print(e)
                        # print(response.status_code)
                        response_data = json.dumps(
                            response.json(), sort_keys=True, indent=2, ensure_ascii=False
                        )
                        # print(response_data)
