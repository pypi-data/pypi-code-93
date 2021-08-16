import logging
import time
import uuid

from api.exceptions import IllegalArgumentException
from client import DataAlgorithmClient

log = logging.getLogger('Ficus')

def check_ficus_online() -> bool:
    """
    检查ficus服务是否存在
    :return:
    """
    from client import check_instance_avaliable
    from api.exceptions import ServiceNoInstanceException
    try:
        check_instance_avaliable()
        return True
    except ServiceNoInstanceException:
        return False

def build_param_def(conf_param_defs:list, is_input_param:bool) -> list:
    """
    构建出参入参
    :param conf_param_defs: 配置文件读取的出/入参
    :param is_input_param: 是否如此
    :return:
    """
    param_defs = list()
    for conf_param_def in conf_param_defs:
        # 获取配置文件读取的字段信息
        if "model" in conf_param_def and len(conf_param_def["model"]) > 0:
            param_def = {
                "type": conf_param_def.get("type").upper(),
                "description": conf_param_def.get("description"),
                "matchTags": conf_param_def.get("matchTags"),
                "matchParams": conf_param_def.get("matchParams"),
                "isInputParam": is_input_param,
                "createTime": time.strftime("%Y-%m-%d %H:%M:%S"),
                "metaModel": {
                    "site": "S1",
                    "project_code": "__NO_PROJECT__",
                    "code": str(uuid.uuid4()).replace('-', ''),
                    "description":"算法组件模型创建",
                    "fields": list()
                }
            }

            for conf_field in conf_param_def["model"]:
                meta_model_field = {
                    "fieldName": conf_field.get("fieldName"),
                    "description": conf_field.get("description"),
                    "dataType": conf_field.get("dataType").upper(),
                    "primaryKey": conf_field.get("primaryKey"),
                    "maxLength": conf_field.get("maxLength"),
                    "minLength": conf_field.get("minLength"),
                    "defaultValue": conf_field.get("defaultValue"),
                    "nullable": conf_field.get("nullable"),
                    "multiple": False
                }
                param_def["metaModel"]["fields"].append(meta_model_field)

            param_defs.append(param_def)

    return param_defs

def build_data_algorithm(conf_algorithm:dict) -> dict:
    data_algorithm = {
        "site": conf_algorithm.get("site"),
        "code": conf_algorithm.get("code"),
        "name": conf_algorithm.get("name"),
        "description": conf_algorithm.get("description"),
        "actorName": conf_algorithm.get("actorName"),
        "handler": conf_algorithm.get("handler"),
        "author": conf_algorithm.get("author"),
        "version": conf_algorithm.get("version"),
        "categories": conf_algorithm.get("categories"),
        "shardable": conf_algorithm.get("shardable"),
        "inputParamDefs": list(),
        "paramDefs": list(),
        "enable": True,
        "createTime": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    #为输入参数赋值
    if "inputParamDefs" in conf_algorithm and len(conf_algorithm["inputParamDefs"]) > 0:
        for conf_input_param_def in conf_algorithm["inputParamDefs"]:
            input_param_def = {
                "code" : conf_input_param_def.get("code"),
                "dataType": conf_input_param_def.get("dataType").upper(),
                "description": conf_input_param_def.get("description"),
                "required": conf_input_param_def.get("required")
            }
            data_algorithm["inputParamDefs"].append(input_param_def)

    #出参入参集合
    if "inputDefs" in conf_algorithm and len(conf_algorithm["inputDefs"]) > 0:
        data_algorithm["paramDefs"].extend(build_param_def(conf_algorithm["inputDefs"], True))

    if "outputDefs" in conf_algorithm and len(conf_algorithm["outputDefs"]) > 0:
        data_algorithm["paramDefs"].extend(build_param_def(conf_algorithm["outputDefs"], False))

    return data_algorithm

def register_algorithm(conf_algorithm:dict, task_handler_names:dict):
    """
    注册算法组件
    :param conf_algorithm:
    :param taskHandlerNames:
    :return:
    """
    # 数据校验
    if "code" not in conf_algorithm or conf_algorithm["code"] == "":
        raise IllegalArgumentException(f"自注册算法组件失败,code为空")

    if "name" not in conf_algorithm or conf_algorithm["name"] == "":
        raise IllegalArgumentException(f"自注册算法组件失败,name为空")

    if "actorName" not in conf_algorithm or conf_algorithm["actorName"] == "":
        raise IllegalArgumentException(f"自注册算法组件失败,actorName为空")

    if "categories" not in conf_algorithm or conf_algorithm["categories"] == "":
        raise IllegalArgumentException(f"自注册算法组件失败,categories为空")

    if "handler" not in conf_algorithm or conf_algorithm["handler"] == "":
        raise IllegalArgumentException(f"自注册算法组件失败,handler为空")
    if conf_algorithm["handler"] not in task_handler_names.keys():
        raise IllegalArgumentException(f"自注册算法组件失败,{conf_algorithm['handler']} 不存在")

    try:
        actor_name = conf_algorithm["actorName"]
        conf_algorithm["version"] = int(actor_name[actor_name.rindex('.v') + 2:])
    except Exception:
        raise IllegalArgumentException(f"自注册算法组件失败,actorName不满足规范,无法获取版本号")
    if conf_algorithm["version"] < 1:
        raise IllegalArgumentException(f"自注册算法组件失败,actorName不满足规范,版本小于1")

    #构建信息
    data_algorithm = build_data_algorithm(conf_algorithm)

    #增加/更新
    if DataAlgorithmClient.exists(data_algorithm["code"], data_algorithm["actorName"]):
        log.info(f"算法组件已存在，不做处理")
        # 暂时没有更新
        # exists_algorithm = DataAlgorithmClient.get(conf_algorithm["code"])
        # if data_algorithm["version"] > exists_algorithm["version"]:
        #     data_algorithm["id"] = exists_algorithm["id"]
        #     data_algorithm["paramDefIds"] = exists_algorithm["paramDefIds"]
        #     DataAlgorithmClient.update(data_algorithm)
        #     log.info(f"更新算法组件")
        # else:
        #     log.warning(f"更新的版本号小于或等于-原始数值:{exists_algorithm['version']}，不做算法组件的处理")
    else:
        DataAlgorithmClient.add(data_algorithm)
        log.info(f"自动注册算法组件")

def registry_after_started():
    """
    服务启动后,检测是否需要注册服务
    :return:
    """

    from registry import ALGORITHM_PROPERTIES
    conf_algorithm = ALGORITHM_PROPERTIES

    if conf_algorithm is None or len(conf_algorithm) == 0:
        # 说明没有yml文件,不进行注册处理
        log.info("没有配置algorithm.yml,不进行算法组件自动注册")
        return

    if not check_ficus_online():
        log.warning("启动时没有可用的ficus服务,忽略自动注册")
        return

    # 找到所有的 TaskHandler
    from api.annotation.annotation import TASK_HANDLERS
    if len(TASK_HANDLERS) == 0:
        log.info("无可用的算法组件,忽略自动注册")
        return

    # 找到所有的taskHandler的名称,key是名字,value是否是messageHandler
    task_handler_names = dict()
    from api.handler.message.IMessageHandler import IMessageHandler
    for name, handler in TASK_HANDLERS.items():
        task_handler_names[name] = isinstance(handler, IMessageHandler)
    register_algorithm(conf_algorithm, task_handler_names)
