# -*- coding: utf-8 -*-
# @Time    : 2019-09-10 09:40
# @Author  : xzr
# @File    : __init__.py
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    :
import datetime
import time

from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from framework.route import Route
from framework.serializer import ParamsSerializer, s
from framework.utils import TIMEFORMAT
from framework.validators import LetterValidator, PasswordValidator
from framework.views import api_view, notauth, notcheck, render_to_response, Request, Response, RspError, \
    RspErrorEnum, swagger_auto_schema
from myadmin.models import Role, User
from .. import settings


@notcheck
@Route('^myadmin/index$')
@api_view('get')
def index(request: Request):
    """
    主页
    """
    # todo 导航菜单
    from .menu import MenuSerializer
    root_menu_list = MenuSerializer(request.user.get_resource('menu').filter(parent_id=0, is_show=1), many=True).data
    parent_id = int(request.query_params.get('parent_id', '0'))

    now_timestamp = int(time.time())
    return Response(locals(), template_name='myadmin/index.html')


class LoginError(RspError): pass


class LoginErrors(RspErrorEnum):
    VERIFY_CODE_ERROR = RspError(_("验证码错误"), 1021)
    LOGIN_TIMES_ERROR = RspError(_("登录次数过多"), 1022)
    USERNAME_OR_PASSWORD_FAIL = RspError(_("账号密码错误"), 1023)
    SAME_PASSWORD = RspError(_('请联系管理员修改密码!'))
    ACCOUNT_NOT_EXIST = RspError(_('账户不存在!'), 1024)
    ACCOUNT_STATUS_ERROR = RspError(_('账户状态错误'), 1025)


class LoginRspSer(s.Serializer):
    url = s.URLField(label=_('跳转地址'))
    Errors = LoginErrors


def check_login_status(request):
    """登录状态检测
    """

    if settings.DEBUG:
        return
    now = datetime.datetime.now()
    err_count = request.session.setdefault('err_count', 0)
    max_count = 10

    if err_count >= max_count:
        lock_time = request.session.setdefault('lock_time', now + datetime.timedelta(minutes=max_count))
        if now < lock_time:
            request.session.clear()
            raise LoginRspSer.Errors.LOGIN_TIMES_ERROR('错误登录次数过多,请在  %s 后再登录！' % lock_time.strftime(TIMEFORMAT))
        else:
            del request.session['err_count']
            del request.session['lock_time']

    if request.POST.get('verify', '') != request.session.get('verify', ''):  # 验证码
        request.COOKIES.clear()
        raise LoginErrors.VERIFY_CODE_ERROR


class LoginSerializer(ParamsSerializer):
    username = s.CharField(label=_('登录用户名'), help_text=_('登录用户名'))
    password = s.CharField(label=_('用户密码'), help_text=_('用户密码'))
    verify = s.CharField(label=_('验证码'), required=False, allow_blank=True)


def ldap_login(request, username, password):
    from myadmin.backend.ldap import LDAPBackend
    ldap_backend = LDAPBackend(username, password)
    the_user: User = ldap_backend.authenticate()

    return the_user


@Route()
@notauth
@swagger_auto_schema('post', request_body=LoginSerializer, responses=LoginRspSer)
@api_view(['get', 'post'])
def login(request: Request):
    """登录
    """
    msg = ''
    now = datetime.datetime.now()
    if request.is_post():
        try:

            params = LoginSerializer(request.data).params_data

            request.COOKIES["username"] = params.username
            username = params.username
            password = params.password
            if not password:
                raise LoginError('密码错误 !')
            check_login_status(request)

            if not username or not password:
                raise LoginErrors.USERNAME_OR_PASSWORD_EMPTY
            is_pass = False
            if settings.USE_LDAP_AUTH:
                the_user = ldap_login(request, username, password)
                is_pass = the_user is not None

            if not is_pass:
                the_user: User = User.objects.filter(username=username).first()
                if not the_user and '@' in username:
                    user_info = UserInfo.objects.filter(email=username).first()
                    if user_info:
                        the_user = user_info.user
                if not the_user:
                    raise LoginErrors.ACCOUNT_NOT_EXIST
                is_pass = the_user.check_password(password)

            if the_user.status != User.Status.NORMAL:
                raise LoginErrors.ACCOUNT_STATUS_ERROR(_('账户已 %s') % the_user.get_status_display())

            if is_pass:
                User.login_user(request, the_user)
                redirect_url = request.query_params.get('from_url', settings.INDEX_URL)
                if request.is_ajax():
                    return Response(LoginRspSer(dict(url=redirect_url)))
                else:
                    return HttpResponseRedirect(redirect_url)
            else:
                raise LoginErrors.USERNAME_OR_PASSWORD_FAIL
        except RspError as error:
            request.session['err_count'] = request.session.get('err_count', 0) + 1
            raise error
    return render_to_response('myadmin/login.html', locals())


@Route()
@notauth
@api_view(['get', 'post'])
def phone_login(request):
    from .sms import check_sms_mobile_code
    from ..models import UserInfo
    now = datetime.datetime.now()
    code = 0
    msg = ''
    if request.is_post():

        try:
            phone = request.REQUEST.get('phone')
            sms_verify_code = request.REQUEST.get('smsVerifyCode')
            check_sms_mobile_code(request, phone, sms_verify_code)
            user_info = UserInfo.objects.filter(phone=phone)[:1]
            if user_info:
                user_info = user_info[0]
                the_user = user_info.user
                if the_user.status != User.Status.NORMAL:
                    raise LoginError('账户已  %s' % the_user.get_status_display())
                User.login_user(request, the_user)
                redirect_url = request.REQUEST.get('from_url', '/index')
                return HttpResponseRedirect(redirect_url)

            else:
                raise LoginError('%s 未绑定账号' % phone)

        except RspError as e:
            msg = e.msg
            code = e.code
            request.session['err_count'] = request.session.get('err_count', 0) + 1
            # raise e
    return Response(locals(), code=code, msg=msg, template_name='myadmin/phone_login.html')


@Route()
@notauth
def logout(request):
    """登出
    """
    from django.contrib.auth import logout
    plan_id = request.session.get('plan_id', None)  # 渠道登录的

    logout(request)
    request.session.clear()
    if plan_id:
        return HttpResponseRedirect("/channel/login")
    return HttpResponseRedirect("/myadmin/login")


from .user_info import UserInfoSerializer, UserInfo


class RegisterAdminReqSerializer(ParamsSerializer):
    username = s.CharField(label=_('登录名称'), validators=[LetterValidator], required=True)
    employee_id = s.CharField(label=_('工号'), required=False, default='')
    email = s.EmailField(label=_('邮箱地址'), required=True)
    qq = s.CharField(label=_('QQ'), required=False, default='')
    phone = s.CharField(label=_('手机号'), required=False, default='')
    alias = s.CharField(label=_('姓名'), required=True)
    password1 = s.CharField(label=_('密码'), required=True, validators=[PasswordValidator])
    password2 = s.CharField(label=_('确认密码'), required=True, validators=[PasswordValidator])
    verify = s.CharField(label=_('验证码'), required=True)
    default_group = s.CharField(label=_('默认组'), required=False)

    class Meta:
        model = UserInfo
        fields = '__all__'


@Route()
@notauth
@swagger_auto_schema('post', request_body=RegisterAdminReqSerializer)
@api_view(['get', 'post'])
def register(request: Request, **kwargs):
    """
    管理员注册
    """
    if request.is_post():
        params = RegisterAdminReqSerializer(request.data).params_data

        if request.session.get('verify', '') != params.verify:
            raise RspError('验证码错误')
        if params.password1 != params.password2:
            raise RspError({'password1': [_('两次密码不一致')]})

        if User.objects.filter(username=params.username).exists():
            raise RspError(_('%s 已被注册') % params.username)
        user_model = User()
        user_model.username = params.username
        user_model.alias = params.alias
        user_model.set_password(params.password1)
        user_model.reg_ip = request.real_ip
        user_model.clean_fields()
        user_model.save()

        user_info_model, _created = UserInfo.objects.get_or_create(user=user_model)
        user_info_model.email = params.email
        user_info_model.qq = params.qq
        user_info_model.phone = params.phone
        user_info_model.save()
        if settings.ALLOW_REGISTER_ROLE_CHOICE and params.default_group:
            role = Role.objects.filter(type=Role.RoleType.GROUP, name=params.default_group).first()
            if role:
                user_model.role.add(role)
        User.login_user(request, user_model)
        return Response(msg=_('注册成功'))
    return render_to_response('myadmin/register.html', locals())
