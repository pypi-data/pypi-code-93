from django.apps import AppConfig
from framework.translation import _

class LdapAccountConfig(AppConfig):
    name = 'ldap_account'
    verbose_name = _('Ldap 账号系统')
