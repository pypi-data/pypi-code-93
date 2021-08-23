# coding=utf-8
import ast
import hashlib
import json
import logging
import sys
import shutil
import time
import traceback
import os
import arrow
import uuid

from django.conf import settings
from django.contrib import admin
from django.db import models
from django.utils.translation import ugettext_lazy as _
from tfduck.common.extendEncoder import DatetimeJSONEncoder
from django.apps import apps


class Et(Exception):
    """
    @author: yuanxiao
    @date: 2010-6-10
    @des: 自定义事物中的错误
    """

    def __init__(self, state=95635, v="default error", *args, **kwas):
        """
        """
        super(Et, self).__init__(*args, **kwas)
        self._msg = v
        self.state = state

    @property
    def msg(self):
        return json.dumps(self._msg)

    def getmsg(self):
        return self._msg


class CeleryRetryError(Et):
    pass


class BaseMethod(object):
    """
    @des:一些基础方法
    """

    def __init__(self):
        """
        @des:保持一些全局变量
        """
        self.logger_django = logging.getLogger('django')
        self.logger_dadian = logging.getLogger('dadian')

    def get_current_env(self):
        current_env = 'server'
        try:
            ddd = settings.DEBUG
        except:
            current_env = "local"
        return current_env

    def remove_file(self, file_path):
        """
        @des: 删除文件
        """
        try:
            os.remove(file_path)
        except:
            pass

    def remove_folder(self, folder_path):
        """
        @des: 删除文件夹
        """
        try:
            shutil.rmtree(folder_path)
        except:
            pass

    def get_file_path(self, path):
        """
        @des: 文件的真实路径
        """
        try:
            return os.path.join(settings.BASE_DIR, os.path.join("dags/sptasks/p_code", path))
        except:
            local_path = os.path.normpath(path)
            paths = local_path.split("/")
            if paths[0] == ".":
                real_path = "/".join(paths[2:])
            else:
                real_path = "/".join(paths[1:])
            return real_path
    
    def gen_local_unique_file(self, pre_path="", pre_name="", ext="csv"):
        """
        @des:生成本地文件唯一路径
        """
        # media_root = settings.MEDIA_ROOT
        media_root = "/mydata/media"
        base_dir = os.path.join(media_root, "docs", pre_path)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        real_name = "%s%s_%s.%s" % (pre_name, uuid.uuid1().hex, arrow.now().format("YYYYMMDD_HHmmSS"), ext)
        file_path = os.path.join(base_dir, real_name)
        return file_path
    
    def gen_local_unique_path(self, pre_path="", pre_name="", is_create=False):
        """
        @des:生成本地目录唯一路径
        """
        # media_root = settings.MEDIA_ROOT
        media_root = "/mydata/media"
        base_dir = os.path.join(media_root, "docs", pre_path)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        real_name = "%s%s_%s" % (pre_name, uuid.uuid1().hex, arrow.now().format("YYYYMMDD_HHmmSS"))
        folder_path = os.path.join(base_dir, real_name)
        if is_create:
            os.makedirs(folder_path)
        return folder_path
    
    def get_var(self, name):
        """
        @des: 获取变量
        """
        if self.get_current_env() == "local":
            return None
        else:
            VarConfig = apps.get_model("gconfig", 'VarConfig')
            try:
                obj = VarConfig.objects.get(name=name)
                return obj.contents
            except:
                return None

    def clog(self, ctx, *log_values):
        """
        @des: 向数据库中记录日志
        """
        try:
            pd_logs = [str(item) for item in log_values]
            pd_logs = "".join(pd_logs)
            if len(pd_logs) > 1024*1024*50:  # 大于5M
                log_values = ["log data too long"]
        except:
            pass
        if self.get_current_env() == "local":
            #
            real_values = []
            for log_value in log_values:
                try:
                    value = str(log_value)
                    real_values.append(value)
                except:
                    value = "log value must be string"
                    real_values.append(value)
            print(*real_values)
        else:
            task_type = ctx['task_type']
            trid = ctx['trid']
            index = ctx['index']
            #
            real_values = []
            for log_value in log_values:
                try:
                    value = str(log_value)
                    real_values.append(value)
                except:
                    value = "log value must be string"
                    real_values.append(value)

            Record = None
            if task_type == "dtask":
                Record = apps.get_model("dtask", 'RunRecord')
            elif task_type == "retask":
                Record = apps.get_model("retask", 'RETaskRecord')
            elif task_type == "sptask":
                Record = apps.get_model("sptask", 'DPTaskRecord')
            if Record is not None:
                try:
                    Record.objects.add_records(
                        lock_id=trid, task_index=index, recs=real_values)
                except Exception as e:
                    self.log_error("clog error ----- :")
                    self.logerr(e)
        # 防止过度写入日志
        time.sleep(0.5)

    def get_record_now(self, ctx={}, tz="UTC"):
        """
        @des: 获取执行任务记录的创建时间，方便dag里面取根据现在时间去执行part_date
        start = arrow.now(tz="Asia/Shanghai")
        @ return: datetime 带时区
        """
        if self.get_current_env() == "local":
            root_create_time = arrow.now(tz=tz)
        else:
            # 如果是查看任务，而不是任务记录，是不会有这两个参数的
            task_type = ctx.get('task_type', None)
            trid = ctx.get('trid', None)
            if trid is None:
                root_create_time = arrow.now(tz=tz)
            else:
                Record = None
                if task_type == "dtask":
                    Record = apps.get_model("dtask", 'RunRecord')
                elif task_type == "retask":
                    Record = apps.get_model("retask", 'RETaskRecord')
                elif task_type == "sptask":
                    Record = apps.get_model("sptask", 'DPTaskRecord')
                if Record is not None:
                    obj = Record.objects.get(id=trid)
                    #
                    root_create_time = obj.extras.get("root_create_time", None)
                    if root_create_time is None:  # 如果拿不到，那么obj肯定是根节点
                        root_create_time = arrow.get(obj.create_time).to(tz)
                    else:  # 读取extra的信息，即根节点
                        # root_create_time带有时区信息，可以直接get
                        root_create_time = arrow.get(root_create_time).to(tz)
        # 返回
        return root_create_time.datetime

    def jsonloads(self, data):
        """
        @des: 自动jsonload
        """
        try:
            data = json.loads(data)
        except Exception as e:
            try:
                data = ast.literal_eval(data)
            except Exception as e:
                raise Et(2, u"参数格式不正确")
        return data

    def jsondumps(self, data, mode=1, sort_keys=False):
        """
        @des:返回值dumps
        """
        #data = json.dumps(data, ensure_ascii=False, cls=DatetimeJSONEncoder)
        data = json.dumps(data, separators=(',', ':'), cls=DatetimeJSONEncoder)
        return data

    def text_tran_html(self, text):
        """
        @des:将文本转换为html,比如help_text
        """
        text = text.replace("\n", "<br/>")
        text = text.replace(" ", "&nbsp")
        return text

    def tran(self, text):
        """
        @des:翻译
        """
        tran_text = _("%s" % text)
        return tran_text

    # 日志记录
    def logerr(self, e):
        errorMeg = ''
        try:
            for file, lineno, function, text in traceback.extract_tb(sys.exc_info()[2]):
                errorMeg += '%s\n%s, in %s\n%s:                %s!' % (
                    str(e), file, function, lineno, text)
            self.log_error("error"+"*"*50)
            for error in errorMeg.split("\n"):
                self.log_error(error, "error")
            try:
                self.log_error(getattr(e, '_msg', 'exception'))
            except Exception as e1:
                self.log_error(getattr(e, 'msg', 'exception'))
        except Exception as e2:
            self.log_error(e2)

    def geterr(self, e):
        result = []
        errorMeg = ''
        try:
            for file, lineno, function, text in traceback.extract_tb(sys.exc_info()[2]):
                errorMeg += '%s\n%s, in %s\n%s:                %s!' % (
                    str(e), file, function, lineno, text)
            result.append("error"+"*"*50)
            for error in errorMeg.split("\n"):
                result.append(error)
                result.append('error')
            try:
                result.append(getattr(e, '_msg', 'exception'))
            except Exception as e1:
                result.append(getattr(e, 'msg', 'exception'))
        except Exception as e2:
            result.append(str(e2))
        return "\n".join(result)

    def get_log_str(self, *msgs):
        try:
            msg_str = " ".join([str(msg) for msg in msgs])
        except Exception as _:
            msg_str = msgs
        return msg_str

    def log_debug(self, *msgs):
        msg_str = self.get_log_str(*msgs)
        self.logger_django.debug(msg_str)

    def log_info(self, *msgs):
        msg_str = self.get_log_str(*msgs)
        self.logger_django.info(msg_str)

    def log_error(self, *msgs):
        msg_str = self.get_log_str(*msgs)
        self.logger_django.error(msg_str)

    def log_warning(self, *msgs):
        msg_str = self.get_log_str(*msgs)
        self.logger_django.warning(msg_str)
    # end--日志记录


BMOBJ = BaseMethod()
