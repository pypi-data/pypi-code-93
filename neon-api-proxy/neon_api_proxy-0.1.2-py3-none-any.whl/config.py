# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
#
# Copyright 2008-2021 Neongecko.com Inc. | All Rights Reserved
#
# Notice of License - Duplicating this Notice of License near the start of any file containing
# a derivative of this software is a condition of license for this software.
# Friendly Licensing:
# No charge, open source royalty free use of the Neon AI software source and object is offered for
# educational users, noncommercial enthusiasts, Public Benefit Corporations (and LLCs) and
# Social Purpose Corporations (and LLCs). Developers can contact developers@neon.ai
# For commercial licensing, distribution of derivative works or redistribution please contact licenses@neon.ai
# Distributed on an "AS IS” basis without warranties or conditions of any kind, either express or implied.
# Trademarks of Neongecko: Neon AI(TM), Neon Assist (TM), Neon Communicator(TM), Klat(TM)
# Authors: Guy Daniels, Daniel McKnight, Regina Bloomstine, Elon Gasper, Richard Leeds
#
# Specialized conversational reconveyance options from Conversation Processing Intelligence Corp.
# US Patents 2008-2021: US7424516, US20140161250, US20140177813, US8638908, US8068604, US8553852, US10530923, US10530924
# China Patent: CN102017585  -  Europe Patent: EU2156652  -  Patents Pending

import json

from os import environ, path

# TODO: Consider moving these utils to neon_utils package


def get_proxy_config() -> dict:
    """
    Locates a valid configuration file for proxy service credentials
    :return: dict containing "SERVICES" key with proxy service configurations
    """
    config_path = environ.get('NEON_API_PROXY_CONFIG_PATH', 'config.json')
    if path.isfile(path.expanduser(config_path)):
        valid_config_path = path.expanduser(config_path)
    elif path.isfile(path.expanduser("~/.config/neon/credentials.json")):
        valid_config_path = path.expanduser("~/.config/neon/credentials.json")
    elif path.isfile(path.expanduser("~/.local/share/neon/credentials.json")):
        valid_config_path = path.expanduser("~/.local/share/neon/credentials.json")
    else:
        return dict()
    with open(valid_config_path) as input_file:
        proxy_service_config = json.load(input_file)
    return proxy_service_config


def get_mq_config() -> dict:
    """
    Locates a valid MQ config for MQ Authentication
    :return: dict containing "MQ" key with server and users configurations
    """
    if path.isfile(environ.get('NEON_MQ_CONFIG_PATH', 'config.json')):
        valid_config_path = environ.get('NEON_API_PROXY_CONFIG_PATH', 'config.json')
    elif path.isfile(path.expanduser("~/.config/neon/mq_config.json")):
        valid_config_path = path.expanduser("~/.config/neon/mq_config.json")
    elif path.isfile(path.expanduser("~/.local/share/neon/mq_config.json")):
        valid_config_path = path.expanduser("~/.local/share/neon/mq_config.json")
    else:
        return dict()
    with open(valid_config_path) as input_file:
        mq_config = json.load(input_file)
    return mq_config
