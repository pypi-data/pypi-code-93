# -*- coding: utf-8 -*-
#
# 认证,和自定request的中间件
#
# django 常用导入
# =========================================
import json
import logging
import traceback

from django.core.cache import cache
from django.shortcuts import HttpResponseRedirect

import settings
from framework.middleware import BaseMiddleware
from framework.response import Response
from framework.translation import _
from framework.views import is_notauth, is_notcheck
from framework.utils import md5
from .models.user import User
from django.contrib.auth import SESSION_KEY
# ==========================================

# 日志记录
_log = logging.getLogger('root')


def get_real_ip(request):
    """获取真实ip
    """
    return request.META.get('HTTP_REMOTE_ADDR2', '') or request.META.get('HTTP_X_FORWARDED_FOR',
                                                                         '') or request.META.get('REMOTE_ADDR')


class AuthMiddleware(BaseMiddleware):
    """认证的中间件
    """

    def process_request(self, request):

        pass

    def is_pass(self, view_func):
        return view_func.__module__ == 'django.views.static' or view_func.__module__ == 'framework.static' or view_func.__module__.find('debug_toolbar')>=0

    def process_view(self, request, view_func, view_args, view_kwargs):
        """静态文件及有"notauth" 属性view_func 免认证
        """

        # 获取原始代码的属性
        check_view_func = self.get_check_view_func(request, view_func)

        # 视图类没有权限设置,则使用path找出function检查
        if hasattr(check_view_func, 'as_view') and (
                not is_notauth(check_view_func) or not is_notcheck(check_view_func)
        ):
            if 'path' in view_kwargs:
                check_view_func = getattr(check_view_func, view_kwargs['path'], None) or check_view_func

        # 不需要登陆
        if is_notauth(check_view_func) or self.is_pass(view_func) :  # 不需处理的函数不管
            is_allow = True

            if ((request.path_info.find('/login') == 0 or request.path_info.find(
                    '/phone_login') == 0) and request.method == 'POST'):
                request.user = request.admin = User()
                request.user.id = 0
                self.save_operate_log(request, '登录后台')
        else:

            user_id = request.session.get(SESSION_KEY, None)
            the_user = User.objects.filter(id=user_id, status__in=(User.Status.NORMAL, User.Status.NotActive)).first()
            request.user = request.admin = the_user
            if not request.user:
                if request.is_ajax() or request.is_json():
                    return Response(request=request, code=-1, msg=_('请重新登录'))
                login_url = settings.LOGIN_URL
                return HttpResponseRedirect('%s?from_url=%s' % (login_url, request.get_full_path()))

            user_menus = request.user.resource.menu.using('read')

            class UserAllowMenu(dict):
                def __init__(self, user):
                    self.user = user
                    super(UserAllowMenu, self).__init__()

                def __getattr__(self, name):
                    try:
                        menu_obj = self.get(name, None)
                        if not menu_obj and self.user.is_root:
                            return True
                        return menu_obj
                    except KeyError:
                        raise AttributeError(name)

            _user_menu_map = UserAllowMenu(request.user)
            for m in user_menus.all():
                menu_name = m.name
                _user_menu_map[menu_name] = m
            request.allow_menu = _user_menu_map
            request.allow = _user_menu_map
            is_allow = self.check_url_permsssion(request)

            if is_notcheck(check_view_func):
                is_allow = True

        if not is_allow:
            return Response(request=request, code=1, msg=_('没有权限'), template_name='myadmin/block.html')

    def process_response(self, request, response):
        return response

    def process_exception(self, request, exception):
        pass

    def check_url_permsssion(self, request):
        """检查请求URL的权限
        """
        is_allow = False
        match_menu = None

        url_path = request.path_info
        params = request.REQUEST

        # 管理员的菜单里查询匹配项目
        for k, menu in request.allow_menu.items():
            if url_path == menu.url_path and menu.is_match_url_parmas(params):
                match_menu = menu
                is_allow = True
                break

        if match_menu:
            if match_menu.is_log:
                self.save_operate_log(request, match_menu.alias, match_menu.id)
        if request.user.is_root:  # 管理员直接过
            return True
        return is_allow

    def cache_view(self, request, view_func, view_args, view_kwargs):
        """页面级别的缓存
        """
        cache_method_list = ['']
        _mc = cache
        params = str(request.GET)
        view_func_name = view_func.__name__
        key = md5('%s_%s_%s' % (request.user.id, view_func.__name__, params))
        response = _mc.get(key)
        if not response:
            response = view_func(request, *view_args, **view_kwargs)
            _mc.set(key, response, 1800)
        return response

    def save_operate_log(self, request, msg, log_type=29):
        """写操作日志
        """
        try:
            from .models.operate import OperateLog
            operate_log = OperateLog()
            operate_log.type = log_type
            operate_log.user_id = request.user.id
            operate_log.msg = msg
            operate_log.post_params = '%s \n %s' % (json.dumps(request.REQUEST, ensure_ascii=False), request.body)
            operate_log.ip = request.real_ip
            operate_log.full_path = request.get_full_path()
            operate_log.user_agent = request.user_agent
            operate_log.save(using='write')
        except Exception as e:
            traceback.print_exc()
