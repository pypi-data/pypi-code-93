from __future__ import absolute_import
from __future__ import unicode_literals

from laipvt.sysutil.conf import YamlConfig
from laipvt.sysutil.gvalue import PORT_MAP

module_require_tfserver = ("ocr_standard", "captcha", "nlp", "ocr_seal_server")
tfserver_name = {
    "ocr_standard": ["ocr-ctpn-tf-server", "ocr-text-recognition-tf-server",
                     "ocr-unet-table-tf-serving", "semantic-correct"],
    "captcha": ["verification-tf-serving"],
    "nlp": ["bert-service-tf"],
    "ocr_seal_server": ["ocr-seal-tf-serving"]
}

tfserver_image_name = {
    "ocr_standard": "tfserving",
    "captcha": "tfserving",
    "nlp": "tfserving",
    "ocr_seal_server": "tfserving"
}

service_module_relation = {
    "commander": [x for x in range(0, 11)],
    "mage": [x for x in range(31, 51)],
    "wulai": [x for x in range(11, 31)],
    "nlp": [33, 34, 35],
    "captcha": [32],
    "ocr_standard": [36, 37],
    "ocr": [x for x in range(51, 129)],
    "ocr_seal_server": [38, 39]
}

machine_module_relation = {
    "cpu": [x for x in range(34, 129) if x % 2 == 0],
    "gpu": [x for x in range(34, 129) if x % 2 != 0]
}
ocr_standard = range(36, 51)
ocr = range(51, 129)
module_info = {
    0: ("commander", "UiBot Commander"),
    11: ("wulai", "吾来对话机器人"),
    31: ("mage", "UiBot Mage"),
    32: ("captcha", "验证码识别"),
    33: ("geo", "标准地址"),
    34: ("nlp", "文本分类、信息抽取"),
    35: ("nlp", "文本分类、信息抽取(GPU)"),
    36: ("ocr_document_standard", "通用文字识别(标准版 CPU)"),
    37: ("ocr_document_standard_gpu", "通用文字识别(标准版 GPU)"),
    38: ("ocr_seal_server", "印章识别(标准版 CPU)"),
    39: ("ocr_seal_server_gpu", "印章识别(标准版 GPU)"),
    51: ("ocr_document_gpu", "通用文字识别(高级版 GPU)"),
    52: ("ocr_document", "通用文字识别(高级版 CPU)"),
    53: ("ocr_table_gpu", "通用表格识别(高级版 GPU)"),
    54: ("ocr_table", "通用表格识别(高级版 CPU)"),
    55: ("ocr_receipt_gpu", "通用票据识别(高级版 GPU)"),
    56: ("ocr_receipt", "通用票据识别(高级版 CPU)"),
    57: ("ocr_idcard_gpu", "通用卡证识别-身份证(高级版 GPU)"),
    58: ("ocr_idcard", "通用卡证识别-身份证(高级版 CPU)"),
    59: ("ocr_bankcard_gpu", "通用卡证识别-银行卡(高级版 GPU)"),
    60: ("ocr_bankcard", "通用卡证识别-银行卡(高级版 CPU)"),
    61: ("ocr_vehicle_gpu", "通用卡证识别-机动车登记证(高级版 GPU)"),
    62: ("ocr_vehicle", "通用卡证识别-机动车登记证(高级版 CPU)"),
    63: ("ocr_vehiclelicense_gpu", "通用卡证识别-机动车行驶证(高级版 GPU)"),
    64: ("ocr_vehiclelicense", "通用卡证识别-机动车行驶证(高级版 CPU)"),
    65: ("ocr_biz_gpu", "通用卡证识别-营业执照(高级版 GPU)"),
    66: ("ocr_biz", "通用卡证识别-营业执照(高级版 CPU)")
}

menu_relation = {
    1001: {
        36: 100101,
        37: 100102,
        51: 100103,
        52: 100104
    }
}

middleware_port_relation = {
    "minio": {
        "port": 9000,
        "nginx_proxy_port": 10000
    },
    "harbor": {
        "http_port": 8888,
        "nginx_harbor_proxy_port": 8889
    },
    "redis": {
        "port": 6379,
        "port_sentinel": 26379
    },
    "nginx": {
        "commander_port": 8080,
        "commander_tenant_port": 8081,
        "k8s_proxy_port": 6444,
        "mage_proxy_port": 8082
    },
    "mysql": {
        "port": 3306,
        "proxysql_cluster_port": 6032,
        "proxysql_port": 6033,
        "nginx_proxy_port": 6034
    },
    "elasticsearch": {
        "http_port": 9200,
        "tcp_port": 9300
    },
    "rabbitmq": {
        "port": 5672,
        "manage_port": 15672,
        "empd_port": 4369,
        "erlang_port": 25672
    },
    "etcd": {
        "http_port": 12379,
        "tcp_port": 12380
    },
    "identity": {
        "port": 6060,
        "nginx_proxy_port": 6061
    },
    "monitor": {
        "grafana_port": 3000,
        "prometheus_port": 9090,
        "mysql_exporter_port": 9104,
        "redis_exporter_port": 9121,
        "rabbitmq_exporter_port": 9419,
        "elasticsearch_exporter_port": 9114,
        "node_exporter_port": 9100,
        "k8s_metrics_port": 31388,
        "istio_prometheus_port": 31390
    },
    "siber": {
        "port": 88
    },
    "ocr": {
        "ocr_document_gpu": 30006,
        "ocr_table_gpu": 30007,
        "ocr_receipt_gpu": 30008,
        "ocr_idcard_gpu": 30009,
        "ocr_bankcard_gpu": 30013,
        "ocr_vehicle_gpu": 30010,
        "ocr_vehiclelicense_gpu": 30011,
        "ocr_biz_gpu": 30012,
        "ocr_passport_gpu": 30014
    }
}

def init_port_config():
    conf = YamlConfig(PORT_MAP, data=middleware_port_relation)
    conf.write_file(backup=False)

def find_module_by_key(module: str) -> list:
    l = []
    for id in module_info:
        if module_info[id][0] == module:
            res = {}
            res['id'] = id
            res['module'] = module
            res['description'] = module_info[id][1]
            l.append(res)
    return l

def get_module_description(module_id: int) -> str:
    return module_info[module_id][1]

def get_module_key(module_id: int) -> str:
    return module_info[module_id][0]

def get_module_keys(module_ids: list) -> list:
    return [get_module_key(x) for x in module_ids]

def get_all_ports(middleware="") -> list:
    ''':return list[str]'''
    l = []
    try:
        relation = YamlConfig(PORT_MAP).read_file()
    except Exception:
        relation = middleware_port_relation
    if middleware:
        try:
            for k in relation[middleware]:
                l.append(str(relation[middleware][k]))
        except KeyError:
            pass
    else:
        for mid in relation:
            for k in relation[mid]:
                l.append(str(relation[mid][k]))
    return l

def get_port(middleware: str, key: str) -> int:
    try:
        relation = YamlConfig(PORT_MAP).read_file()
    except Exception:
        relation = middleware_port_relation

    try:
        return relation[middleware][key]
    except KeyError:
        for k in relation[middleware].keys():
            if key in k:
                return relation[middleware][k]
        return 0