from ease_sqlite import Sqdb

import importlib
import glob
import json
import sys
import os
import time
from . import _config_table
from ._config_table import config


def Log(e):
    Msg = "[%s] Msg: %s" % (time.strftime("%H:%M:%S"), e)
    print(Msg)


class Plugin:
    def __init__(self, plugin_dir, plugin_init_args=None):
        if not os.path.exists('PluginDB'):
            os.mkdir("PluginDB")

        self._config_db = Sqdb.DataBase('PluginConfig.db', [_config_table])

        self._module_dict = {}
        self._plugin_path = plugin_dir
        self._plugin_start = True
        self._plugin_states = {}
        self._plugin_func_dict = {}
        self._load_vaild_plugins()
        self._plugin_init_args = ()
        self._plugin_init_kwargs = {}
        if plugin_init_args is not None:
            if 'args' in plugin_init_args:
                self._plugin_init_args = plugin_init_args['args']

            if 'kwargs' in plugin_init_args:
                self._plugin_init_kwargs = plugin_init_args['kwargs']

        for p_name, p_state in self._plugin_states.items():
            if p_state:
                self.SetPluginState(p_name, p_state)

    def _get_plugin_config(self):
        config = self._config_db.select_table(_config_table.config, '*')
        return config

    def __del__(self):
        if self._plugin_start:
            self._plugin_start
            nameLst = []
            for PluginName in self._plugin_func_dict.keys():  # 先把插件名列表单独提取出来
                nameLst.append(PluginName)

            for it in nameLst:  # 原因是枚举字典的key时不能删除，而ClosePlugin包含删除操作
                self._close_plugin(it)

        self._save_plugin_config()

    def _save_plugin_config(self):
        for name, state in self._plugin_states.items():
            self._config_db.update_table(
                config, {config.plugin_state: state}, where='plugin_name="%s"' % name)

    def _load_vaild_plugins(self):
        self._plugin_states = {key: False for key in self.list_plugin()}
        PluginConf = self._get_plugin_config()  # 获取当前插件状态配置
        for PlugName, state in PluginConf:
            if PlugName in self._plugin_states:
                self._plugin_states[PlugName] = bool(state)
            else:
                self._config_db.delete_item(
                    config, where='plugin_name="%s"' % PlugName)

        PluginConf = [PlugName for PlugName, _ in PluginConf]
        for key in self._plugin_states:
            if key not in PluginConf:
                self._config_db.insert_table(config, key, 0)

    def _close_plugin(self, plg_name: str):
        if plg_name in self._plugin_func_dict:  # 关闭插件应该把插件从列表中删除
            callback = self._plugin_func_dict[plg_name]
            if 'Delete' in callback and callback['Delete'] != None:
                # 调用插件的close函数，让插件有所反应
                close = callback['Delete']
                close()

            self._plugin_func_dict.pop(plg_name)

            for it in self._module_dict[plg_name]:
                sys.modules.pop(it)  # 也从系统模块列表中删除，释放应用
            self._module_dict.pop(plg_name)

    def _plugin_register(self, PlugModule, PluginName):
        if hasattr(PlugModule, 'Init'):  # 所有插件必须包含初始化函数，否则不认为其是一个插件
            if callable(PlugModule.Init):  # 是否可调用
                try:
                    callback = PlugModule.Init(
                        *self._plugin_init_args, **self._plugin_init_kwargs)
                except:
                    self._plugin_states[PluginName] = False
                    Log("注册插件[%s]失败...因为插件初始化函数调用失败" % PluginName)
                    return
                self._plugin_func_dict[PluginName] = callback if callback is not None else {
                }
                self._module_dict[PluginName] = ["%s.%s" % (self._plugin_path, PluginName), "%s.%s.plugin" % (
                    self._plugin_path, PluginName)]  # 插件系统本身维护，用于reload
                self._plugin_states[PluginName] = True  # 设置开启
        else:
            Log("注册插件[%s]失败...因为该插件不可用" % PluginName)
            self._close_plugin(PluginName)

    def list_plugin(self):  # 枚举插件路径下的所有插件
        res = glob.glob('%s/*/plugin.py' % self._plugin_path)
        ret = []
        for it in res:
            filepath, filename = os.path.split(it)
            _, filename = os.path.split(filepath)
            ret.append(filename)
        return ret

    def reload_all(self):
        nameLst = []
        for PluginName in self._plugin_dict.keys():
            nameLst.append(PluginName)
        for it in nameLst:
            self.close_plugin(it)
        # 上方为先关闭所有插件

        # 再重新加载所有插件就是reload，当然，最重要的是close时要把插件从sys.modules里面pop掉
        self._load_vaild_plugins()

        for p_name, p_state in self._plugin_states.items():
            if p_state:
                self.SetPluginState(p_name, p_state)

    def SetPluginState(self, PluginName, IsUsing=True):
        # 设置插件是否开启
        if IsUsing == False:
            if PluginName in self._plugin_func_dict:  # 当前插件在当前插件列表中，也就是已开启
                self._plugin_states[PluginName] = False
                self._close_plugin(PluginName)  # 物理关闭插件 O(∩_∩)O
                Log("关闭插件[%s]成功...." % PluginName)
            else:
                Log("关闭插件[%s]失败，因为该插件未被加载...." % PluginName)
        else:
            try:
                if PluginName not in self._plugin_func_dict:  # 不在列表中，则 import
                    mod_name = "%s.%s.plugin" % (self._plugin_path, PluginName)
                    module = importlib.import_module(mod_name)
                    self._plugin_register(module, PluginName)
            except KeyError:
                Log("启动插件失败，因为插件[%s]不存在...." % PluginName)

        self._save_plugin_config()

    def get_plugin_state(self, plugin_name):
        try:
            return self._plugin_states[plugin_name]
        except KeyError:
            return None

    def get_plugin_funcs(self, plugin_name):
        try:
            return self._plugin_func_dict[plugin_name]
        except KeyError:
            return None
