"""
kelove_settings.py
By IT小强xqitw.cn <mail@xqitw.cn>
At 1/24/21 11:47 AM
"""

from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django import forms

from .setting_forms import Settings


class EmailSettings(Settings):
    """
    邮件配置
    """

    settings_title: str = _('邮件配置')

    fieldsets = (
        (_('基础配置'), {
            'fields': (
                'EMAIL_HOST',
                'EMAIL_PORT',
                'EMAIL_HOST_USER',
                'DEFAULT_FROM_EMAIL',
                'OTP_EMAIL_SENDER',
                'EMAIL_HOST_PASSWORD',
            ),
            'classes': ('extrapretty', 'wide')
        }),
        (_('安全链接'), {
            'fields': (
                'EMAIL_USE_TLS',
                'EMAIL_USE_SSL',
            ),
            'classes': ('extrapretty', 'wide')
        }),
        (_('配置信息'), {
            'fields': (
                'settings_title',
                'settings_key',
            ),
            'classes': ('extrapretty', 'wide')
        })
    )

    EMAIL_HOST = forms.CharField(
        initial=getattr(settings, 'EMAIL_HOST', 'smtp.qq.com'),
        empty_value=getattr(settings, 'EMAIL_HOST', 'smtp.qq.com'),
        required=False,
        label=_('邮件服务器域名'),
        help_text=_('例如：smtp.qq.com')
    )

    EMAIL_PORT = forms.IntegerField(
        initial=getattr(settings, 'EMAIL_PORT', 465),
        required=False,
        label=_('邮件服务器端口号，为数字'),
        help_text=_('例如：465')
    )

    EMAIL_HOST_USER = forms.CharField(
        initial=getattr(settings, 'EMAIL_HOST_USER', ''),
        required=False,
        label=_('发件人邮箱'),
    )

    DEFAULT_FROM_EMAIL = forms.CharField(
        initial=getattr(settings, 'DEFAULT_FROM_EMAIL', ''),
        required=False,
        label=_('发件人地址'),
        help_text=_('fred@example.com 和 Fred &lt;fred@example.com&gt; 形式都是合法的')
    )

    OTP_EMAIL_SENDER = forms.CharField(
        initial=getattr(settings, 'OTP_EMAIL_SENDER', ''),
        required=False,
        label=_('一次性验证码发件人地址'),
        help_text=_('留空自动使用发件人地址。fred@example.com 和 Fred &lt;fred@example.com&gt; 形式都是合法的')
    )

    EMAIL_HOST_PASSWORD = forms.CharField(
        widget=forms.PasswordInput(render_value=True),
        initial=getattr(settings, 'EMAIL_HOST_PASSWORD', ''),
        required=False,
        label=_('发件人授权码'),
        help_text=_('发件人授权码不一定是邮箱密码')
    )

    EMAIL_USE_TLS = forms.BooleanField(
        initial=getattr(settings, 'EMAIL_USE_TLS', False),
        required=False,
        label=_('是否启用安全链接TLS'),
        help_text=_('通常端口为587 TLS/SSL是相互排斥的，因此仅将其中一个设置设置为启用即可')
    )

    EMAIL_USE_SSL = forms.BooleanField(
        initial=getattr(settings, 'EMAIL_USE_SSL', True),
        required=False,
        label=_('是否启用安全链接SSL'),
        help_text=_('通常端口为465 TLS/SSL是相互排斥的，因此仅将其中一个设置设置为启用即可')
    )

    @classmethod
    def get(cls) -> dict:
        data = super().get()
        otp_email_sender_value = data.get('OTP_EMAIL_SENDER', '')
        if not otp_email_sender_value:
            otp_email_sender_value = data.get('DEFAULT_FROM_EMAIL', '')
        data['OTP_EMAIL_SENDER'] = otp_email_sender_value
        return data
