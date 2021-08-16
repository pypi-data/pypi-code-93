default_app_config = 'ldap_account.apps.LdapAccountConfig'

from framework.utils import threadpoll

from .settings import LDAP_ACCOUNT_FOLLOW_START

if LDAP_ACCOUNT_FOLLOW_START:
    from .ldap_server import run_ldap_server

    threadpoll.async_func(run_ldap_server)()
