import types
from abc import ABC
from math import ceil
from typing import Any

from tornado import httputil
from tornado.web import StaticFileHandler

from shangqi_cloud_lib.frame.BaseHandler import BaseHandler
from shangqi_cloud_lib.utils.CommonUtil import get_host_ip, sys_date_format, generate_random_key, get_default_args, get_command, \
    parse_val
from shangqi_cloud_lib.utils.DataClient import DataClient
from shangqi_cloud_lib.utils.FileUtil import read_json, write_json
from shangqi_cloud_lib.utils.JwtUtil import generate_session
from shangqi_cloud_lib.utils.MysqlUtil import *


def insert_params_sql(params: list):
    sql = "INSERT INTO doc_record ({}) VALUES ({})"
    value_list = ["%({})s".format(x) for x in params]
    return sql.format(",".join(params), ",".join(value_list))


def save_records(record_list: list):
    if record_list and len(record_list) > 0:
        sql = insert_params_sql(["key_type", "old_val", "new_val", "record_time", "key_owner", "record_type", "anchor"])
        with SqlSession() as session:
            session.execute_update(sql, record_list, True)


def add_record(record_list: list, record: dict):
    if record and len(record.keys()) > 0:
        record_list.append(record)


def create_record(key_type, old_val, new_val, key_owner, anchor):
    if old_val == new_val or str(old_val) == str(new_val):
        return {}
    record_type = "修改"
    if old_val is None:
        record_type = "新增"
    elif new_val is None:
        record_type = "删除"
    record = {
        "key_type": key_type,
        "old_val": str(old_val) if old_val is not None else old_val,
        "new_val": str(new_val) if new_val is not None else new_val,
        "key_owner": key_owner,
        "anchor": anchor,
        "record_time": sys_date_format(),
        "record_type": record_type
    }
    return record


def methods(target):
    method_list = list(filter(
        lambda m: not m.startswith("__") and not m.startswith("_") and callable(getattr(target, m)) and
                  type(getattr(target, m, None)) == types.FunctionType,
        dir(target)))
    base_method_list = []
    for base in target.__bases__:
        base_method_list.extend(list(filter(
            lambda m: not m.startswith("__") and not m.startswith("_") and callable(getattr(base, m)) and
                      type(getattr(base, m, None)) == types.FunctionType,
            dir(base))))
    self_method_list = []
    for method in method_list:
        if method not in base_method_list:
            self_method_list.append(method)
    return self_method_list


def filter_req_methods(target, method_names):
    method_list = []
    for i in range(len(method_names)):
        method = getattr(target, method_names[i])
        if getattr(method, "__req__", None):
            method_list.append(method)
    return method_list


def record_handler(record_list, api_item: dict, path, comment):
    # 添加记录 path & desc
    add_record(record_list, create_record("请求路径", api_item.get("path", None), path, path, comment))
    add_record(record_list, create_record("路径描述", api_item.get("desc", None), comment, path, comment))


def record_method(record_list: list, old_method_dict: dict, new_method_dict: dict):
    for method_item in new_method_dict.values():
        old_item = {}
        command = method_item.get("command")
        if command in old_method_dict.keys():
            old_item = old_method_dict.get(command).copy()
            del old_method_dict[command]
        key_owner = method_item.get("path") + '?command=' + command
        anchor = method_item.get("id")
        add_record(record_list,
                   create_record("请求方法", old_item.get("http_method", None), method_item.get("http_method"), key_owner,
                                 anchor))
        add_record(record_list, create_record("Command", old_item.get("command", None), command, key_owner, anchor))
        add_record(record_list,
                   create_record("方法说明", old_item.get("desc", None), method_item.get("desc"), key_owner, anchor))
        record_params(record_list, old_item.get("", {}), method_item.get("", {}), key_owner, anchor)
    if len(old_method_dict.keys()) > 0:
        for old_method in old_method_dict.values():
            command = old_method.get("command")
            key_owner = old_method.get("path") + '?command=' + command
            anchor = old_method.get("id")
            add_record(record_list, create_record("Command", command, None, key_owner, anchor))


def record_params(record_list: list, old_params: dict, new_params: dict, key_owner, anchor):
    for param in new_params.values():
        param_name = param.get("param_name")
        owner_new = key_owner + "[{}]".format(param_name)
        old_param = {}
        if param_name in old_params.keys():
            old_param = old_params.get(param_name).copy()
            del old_params[param_name]
        add_record(record_list, create_record("参数名", old_param.get("param_name", None), param_name, owner_new, anchor))
        add_record(record_list,
                   create_record("默认值", old_param.get("default_val", None), param.get("default_val"), owner_new,
                                 anchor))
        add_record(record_list,
                   create_record("数据类型", old_param.get("data_type", None), param.get("data_type"), owner_new, anchor))
    if len(old_params.keys()) > 0:
        for old_param in old_params.values():
            param_name = old_param.get("param_name")
            owner_new = key_owner + "[{}]".format(param_name)
            add_record(record_list,
                       create_record("参数名", param_name, None, owner_new, anchor))


form_session_map = {}


def init_session_map(size):
    for i in range(size):
        create_session()


def create_session():
    key = generate_random_key(12)
    session = generate_session(key)
    form_session_map[session] = key


def query_record_data(offset=0, limit=20):
    with SqlSession() as session:
        record_data = session.query_all(
            "SELECT * FROM doc_record ORDER BY record_time DESC, id DESC LIMIT {}, {}".format(offset, limit))
        return record_data


class DocHandler(BaseHandler, ABC):
    def __init__(self, application: "Application", request: httputil.HTTPServerRequest, **kwargs: Any):
        super().__init__(application, request, **kwargs)
        self.api_map = {}
        self.method_size = 0
        self.client = DataClient("http://{}:{}".format(get_host_ip(), config.server_port))
        rules = self.application.wildcard_router.rules
        record_list = []
        index = 1
        for rule in rules:
            target = rule.target
            if target == self.__class__ or target == StaticFileHandler:
                continue
            if getattr(target, "__comment__", None) is None:
                continue
            comment = target.__comment__
            path = rule.matcher._path
            api_item = read_json(path[1:] + ".json", config.doc_path)
            if len(api_item.keys()) == 0:
                # 新增handler记录
                add_record(record_list, create_record("Handler", None, target.__name__, path, comment))
            # 更新handler记录
            record_handler(record_list, api_item, path, comment)
            api_item["path"] = path
            api_item["desc"] = comment
            method_names = methods(target)
            method_list = filter_req_methods(target, method_names)
            method_info_dict = {}
            method_dict = api_item.get("method_dict", {})
            for method in method_list:
                old_method_item = method_dict.get(method.__command__, {})
                method_item = {
                    "http_url": "http://{}:{}{}".format(get_host_ip(), config.server_port, path),
                    "http_method": method.__req__,
                    "command": method.__command__,
                    "desc": method.__comment__,
                    "path": path,
                    "id": str(index)
                }
                index = index + 1
                args = get_default_args(method)
                func_params = method.__code__.co_varnames
                request_params = old_method_item.get("request_params", {})
                for i in range(1, method.__code__.co_argcount):
                    required = func_params[i] not in args.keys()
                    default_val = "" if required else str(args.get(func_params[i]))
                    if func_params[i] not in request_params.keys():
                        request_params[func_params[i]] = {
                            "param_name": func_params[i],
                            "sample_data": default_val,
                            "default_val": default_val,
                            "data_type": type(default_val).__name__,
                            "required": "是" if required else "否",
                            "comment": default_val,
                        }
                    else:
                        request_params[func_params[i]]["default_val"] = default_val
                        request_params[func_params[i]]["required"] = "是" if required else "否"
                method_item["request_params"] = request_params
                method_info_dict[method_item["command"]] = method_item
                self.method_size = self.method_size + 1
            # 更新方法记录
            record_method(record_list, method_dict, method_info_dict)
            api_item["method_dict"] = method_info_dict
            self.api_map[path] = api_item
            if len(record_list) > 0:
                # 有修改更新本地文件，同时插入修改记录
                write_json(path[1:] + ".json", api_item, config.doc_path)
                save_records(record_list)

    def get(self):
        record_data = query_record_data()
        if not record_data:
            record_data = []
        self.render("doc.html", api_list=self.api_map.values(), record_data=record_data,
                    project_name=config.project_name,
                    edit=False, anchor="record")

    def post(self):
        # 表单参数
        command, params, is_json = get_command(self, "post")
        func = eval(f"self.{command}")
        default_args = get_default_args(func)
        func_params = func.__code__.co_varnames
        params_list = []
        for i in range(1, func.__code__.co_argcount):
            val_type = type(default_args.get(func_params[i], None))
            if func_params[i] in params.keys():
                val = params.get(func_params[i])
                if not is_json:
                    val = parse_val(val, val_type)
                params_list.append(val)
            elif func_params[i] in default_args.keys():
                params_list.append(default_args.get(func_params[i]))
            else:
                return self.write_custom_error(-1,
                                               "{}请求方法缺少必要的参数:{}".format(str(func.__name__).upper(),
                                                                         func_params[i]))
        res = func(*params_list)
        if res:
            self.write_json_data(res)

    # @PostMapping("编辑页面")
    def edit(self, auth="", anchor=""):
        if auth == config.doc_auth:
            init_session_map(self.method_size)
            self.render("doc.html", api_list=self.api_map.values(), record_data=[],
                        project_name=config.project_name, edit=True, anchor=anchor,
                        session_list=list(form_session_map.keys()))
        else:
            return self.result_err("验证信息错误！")

    # @PostMapping("修改接口信息")
    def update(self, param_name, sample_data, comment, data_type, path="", method="", anchor="", session=""):
        if session not in form_session_map.keys():
            init_session_map(self.method_size)
            self.render("doc.html", api_list=self.api_map.values(), record_data=[], project_name=config.project_name,
                        edit=True, anchor=anchor, session_list=list(form_session_map.keys()))
            return
        record_data = []
        if param_name:
            record_list = []
            old_method_dict = self.api_map.get(str(path)).get("method_dict").get(str(method))
            params = old_method_dict.get("request_params", {})
            for i, name in enumerate(param_name):
                key_owner = path + '?command=' + method + "[{}]".format(name)
                param_item = params.get(name)
                if len(sample_data) > i:
                    add_record(record_list,
                               create_record("样例数据", param_item.get("sample_data"), sample_data[i], key_owner, anchor))
                    param_item["sample_data"] = sample_data[i]
                if len(comment) > i:
                    add_record(record_list,
                               create_record("参数说明", param_item.get("comment"), comment[i], key_owner, anchor))
                    param_item["comment"] = comment[i]
                if len(data_type) > i:
                    add_record(record_list,
                               create_record("数据类型", param_item.get("data_type"), data_type[i], key_owner, anchor))
                    param_item["data_type"] = data_type[i]
            if len(record_list) > 0:
                # 有修改更新本地文件，同时插入修改记录，删除当前session防止表单重复提交
                del form_session_map[session]
                create_session()
                write_json(path[1:] + ".json", self.api_map.get(str(path)), config.doc_path)
                save_records(record_list)
                record_data = query_record_data()
        self.render("doc.html", api_list=self.api_map.values(), record_data=record_data,
                    project_name=config.project_name,
                    edit=True, anchor=anchor, session_list=list(form_session_map.keys()))


class RecordHandler(BaseHandler, ABC):
    def get(self):
        limit = 25
        page_number = int(self.get_argument("page_number", "1"))
        offset = (page_number - 1) * limit
        count = 0
        with SqlSession() as session:
            count = session.query_one("select count(*) from doc_record", "first")
        total_page = ceil(count / limit)
        record_data = query_record_data(offset, limit)
        self.render("record.html", record_data=record_data,
                    project_name=config.project_name,
                    curr_page=page_number,
                    total_page=total_page,
                    last_page=max(page_number - 1, 0),
                    next_page=min(page_number + 1, total_page)
                    )
