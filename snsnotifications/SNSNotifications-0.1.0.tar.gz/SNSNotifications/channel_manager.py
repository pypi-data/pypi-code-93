import warnings
from os import environ
from typing import Dict, Optional, Any

import pydash as __

from .types import NotificationChannel

__all__ = ['create_channel']


def create_channel(name: str, configs: Dict[str, Dict]) -> Optional[NotificationChannel]:
    if name not in configs:
        configs = {}
    configs = _inherit_global_config(name, configs.get(name, {}))
    try:
        create_func_name = '_create_{}_channel'.format(name)
        module = globals()
        if create_func_name not in module:
            raise Exception("Channel is not supported")
        channel = module[create_func_name](**configs)
        return channel
    except Exception as e:
        warnings.warn("An error while create {} channel: {}".format(name, e))


def _inherit_global_config(prefix: str, configs: Dict[str, Any]) -> Dict[str, Any]:
    prefix = prefix.upper() + '_'
    prefix_length = len(prefix)
    envs = {}
    for key in environ.keys():
        if not key.startswith(prefix):
            continue
        conf_name = key[prefix_length:].lower()
        envs[conf_name] = environ[key]

    return __.assign(envs, configs)


def _create_mail_channel(driver='smtp', **kwargs) -> NotificationChannel:
    from SNSNotifications.channels.mail import Mailer
    return Mailer(driver, **kwargs)


def _create_slack_channel(token, **kwargs) -> NotificationChannel:
    from SNSNotifications.channels.slack import SlackClient
    return SlackClient(token, **kwargs)
