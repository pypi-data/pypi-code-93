from functools import wraps
from flask import make_response,g,current_app
# import requests
from mwsdk import Rightmanage,Rightmanage_inner
import logging
class PermissionError(Exception):
    pass

class Permission(object):
    def __init__(self,sysname=None,app=None,version='v1.0'):
        '''
        :param sys: 系统名称，如:maxguideweb
        :param app:
        :param auth: 认证方式，如：jwt
        :param version: 权限的版本，通过url取permission
        '''
        super(Permission, self).__init__()
        # 权限的版本
        self.version = version
        self.sys = sysname
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.sys = app.config.get('SYSTEM_NAME')

    def _get_permission(self):
        if current_app.config.get('DEVELOPMENT',False):
            return []
        # _,result = Rightmanage.cur_permissions(self.sys, g.jwt,self.version )
        _,result = Rightmanage_inner().permissions(self.sys, g.user_id,self.version)
        return result

    def check(self, subsystem3s , actions):
        '''
        检查某个模块的权限，装饰器
        :param subsystem3s: 权限名称，比如："vehicle" or "vehicle,car" or ["vehicle","car"] 等
        :param actions: 是list，内容为 ['insert','edit','delete',...]
        :return: True 代表有权限，false 代表没有权限
        '''
        def decorate(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if current_app.config.get('DEVELOPMENT', False):
                    return func(*args, **kwargs)
                # 除appuser外，employee,member用户跳过权限检查
                if g.current_user.type!='appuser':
                    return func(*args, **kwargs)
                if isinstance(subsystem3s, str):
                    subsystem3list = subsystem3s.split(',')
                elif isinstance(subsystem3s, list):
                    subsystem3list = subsystem3s
                else:
                    raise Exception(f'the subsystem{subsystem3s} is not support,example:"vehicle" or "vehicle,car" or ["vehicle","car"]')
                try:
                    # 获取到用户下所有的权限
                    permissions = self._get_permission()
                except Exception as e:
                    # 避免第一次訪問時出錯，再次重試訪問權限
                    logging.error(f'第一次訪問權限服務出錯，錯誤：{str(e)}')
                    try:
                        permissions = self._get_permission()
                    except Exception as e:
                        # 避免出500錯誤，返回403
                        logging.error(f'第二次訪問權限服務出錯，錯誤：{str(e)}')
                        permissions = {}
                # 没有指定 subsystem 和actions ，表示允许访问，但没有指定任何权限时，则报403
                if permissions and not subsystem3list and not actions:
                    return func(*args, **kwargs)
                acts_sup = set()
                for subsysntem3 in subsystem3list:
                    permission = permissions.get(subsysntem3)
                    if permission is None:
                        # 支持同时检测多个权限后，有些权限可能不会在当前项目中
                        logging.warning('the subsystem(%s) is not in %s'%(subsysntem3,self.sys))
                        continue
                        # raise Exception('the subsystem(%s) is not in %s'%(subsysntem3,self.sys))
                    # 获取权限的操作
                    ops = permission.get('ops')
                    acts_sup.update({act for act in actions if act in ops})
                # 权限没有操作时，则拒绝
                if not acts_sup:
                    response = make_response()
                    response.status_code = 403
                    return response
                return func(*args, **kwargs)
            return wrapper
        return decorate

    def check_permission(self,subsystem3 , action, msg=''):
        _, permissions_js = Rightmanage_inner().permissions(self.sys, g.user_id)
        permission = permissions_js.get(subsystem3)
        if permission is None:
            raise Exception('the subsystem(%s) is not exist in %s' % (subsystem3,self.sys))
        ops = permission.get('ops',[])
        if action not in ops:
            if not msg:
                msg = 'The user(%s) have no this (%s) right!' % (g.user_name, ops)
            raise PermissionError(msg)
        return True



