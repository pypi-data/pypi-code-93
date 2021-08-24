"""
command 路由封装，支持get、post请求
请求方法调度command_mapper
"""
import tornado.web
import tornado.ioloop
from shangqi_cloud_lib import router

from shangqi_cloud_lib.context import config

import shangqi_cloud_lib.context as context
from shangqi_cloud_lib.utils.CacheUtil import get_cache, set_cache
from shangqi_cloud_lib.utils.CommonUtil import get_default_args, get_command, parse_val


def copy_properties(wrapper, func):
    wrapper.__name__ = func.__name__
    wrapper.__qualname__ = func.__qualname__


# 权限校验
def check_auth(func):
    def wrapper(self, *args, **kwargs):
        # 校验token
        self.set_default_header()
        handler_name = str(self.__class__.__name__)
        command, _, _ = get_command(self, func.__name__)
        url = f'{handler_name}.{command}'
        need_auth = True
        for white_url in config.white_list:
            if url == white_url:
                need_auth = False
                break
            elif "*" in white_url:
                arr = white_url.split(".")
                if len(arr) != 2:
                    continue
                if (arr[0] == "*" and arr[1] == command) or (arr[1] == "*" and handler_name == arr[0]):
                    need_auth = False
                    break

        # 权限校验
        if config.check_auth and need_auth and not self.auth_login():
            # 缺少登录信息，返回401
            self.write_401()
            return self.write(self.result_err("权限验证不通过！"))
        else:
            return func(self, *args, **kwargs)

    copy_properties(wrapper, func)
    return wrapper


def Handler(desc, path=None):
    def class_proxy(ins):
        key = path
        if path is None:
            key = ins.__name__
        ins.__comment__ = desc
        router.router.append((key, ins))
        if ins.__name__ in context.dynamic_handler_names:
            raise Exception("handler名称重复：{}, detail: {}".format(ins.__name__, str(ins)))
        context.dynamic_handler_names.append(ins.__name__)
        return ins

    return class_proxy


def GetMapping(desc, command=None, minute_desc=None, pre_handler=None, is_cache=False, ex=None):
    def func_proxy(func):
        return deal_request(func, desc, command, minute_desc, pre_handler, is_cache, ex, 'get')

    return func_proxy


def PostMapping(desc, command: str = None, minute_desc=None, pre_handler=None, is_cache=False, ex=None):
    def func_proxy(func):
        return deal_request(func, desc, command, minute_desc, pre_handler, is_cache, ex, 'post')

    return func_proxy


# 添加请求信息
def deal_request(ins, desc, command, minute_desc, pre_handler, is_cache, ex, req):
    ins.__req__ = req
    ins.__is_cache = is_cache
    ins.__pre_handler = pre_handler
    ins.__ex = ex
    if minute_desc:
        ins.__minute_comment__ = minute_desc
    if isinstance(command, str):
        ins.__command__ = command
    else:
        ins.__command__ = ins.__name__
    if desc:
        ins.__comment__ = desc
    else:
        ins.__comment__ = ""
    return ins


# command接口映射
def command_mapper(func):
    async def wrapper(self, *args, **kwargs):
        # 校验token
        self.set_default_header()
        func_name = func.__name__
        command, params, is_json = get_command(self, func_name)
        # 校验command的请求方式
        command_func = self.command_map.get(command, None)
        if command_func:
            params_list = []
            if command_func.__pre_handler:
                params_list = command_func.__pre_handler(self, command_func)
            else:
                request_method = command_func.__req__
                args = get_default_args(command_func)
                func_params = command_func.__code__.co_varnames
                if request_method != func_name:
                    return self.write_custom_error(405, "{}请求方法不允许访问Command:{}".format(str(func_name).upper(), command))
                if params:
                    for i in range(1, command_func.__code__.co_argcount):
                        val_type = type(args.get(func_params[i], None))
                        if func_params[i] in params.keys():
                            val = params.get(func_params[i])
                            if not is_json:
                                val = parse_val(val, val_type)
                            params_list.append(val)
                        elif func_params[i] in args.keys():
                            params_list.append(args.get(func_params[i]))
                        else:
                            return self.write_custom_error(406,
                                                           "{}请求方法缺少必要的参数:{}".format(str(func_name).upper(),
                                                                                     func_params[i]))
                else:
                    arguments = self.request.arguments
                    for i in range(1, command_func.__code__.co_argcount):
                        val_type = type(args.get(func_params[i], None))
                        if func_params[i] in arguments.keys():
                            params_list.append(parse_val(self.get_argument(func_params[i]), val_type))
                        elif func_params[i] in args.keys():
                            params_list.append(parse_val(args.get(func_params[i]), val_type))
                        else:
                            return self.write_custom_error(406,
                                                           "{}请求方法缺少必要的参数:{}".format(str(func_name).upper(),
                                                                                     func_params[i]))
            # 缓存
            res = None
            update = True
            read_cache = self.can_read_cache()  # 请求中设置是否读取缓存，False说明强制刷新
            key = f"{self.request.path}&{command}&{str(params_list)}"
            if read_cache and config.use_local_cache and command_func.__is_cache:
                cache_res = get_cache(key)
                if cache_res:
                    res = cache_res
                    update = False
            # 异步调用
            if not res:
                res = await tornado.ioloop.IOLoop.current().run_in_executor(None, command_func, *params_list)
            if res is not None:
                # 添加缓存
                if config.use_local_cache and update and command_func.__is_cache:
                    set_cache(key, res, ex=command_func.__ex)
                try:
                    self.write_json_data(res)
                except TypeError as e:
                    self.write_data(res)
        else:
            self.write_custom_error(404, "没有找到Command对应的方法：{}".format(command))

    copy_properties(wrapper, func)
    return wrapper
