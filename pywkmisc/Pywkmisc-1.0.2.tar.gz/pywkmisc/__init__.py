#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pywkmisc.config import Config
from pywkmisc.date_utils import DateUtils
from pywkmisc.file_utils import FileUtils
from pywkmisc.image_utils import ImageUtils
from pywkmisc.string_utils import StringUtils

_config = None

if _config is None:
    import os
    if os.path.exists('../conf/'):
        _config = Config('../conf/')
    if os.path.exists('conf/'):
        _config = Config('conf/')

@property
def config():
    global _config
    return _config


def get_config(key):
    global _config
    if _config is None:
        return _config
    return _config.get_basic(key)


def get_configs(key):
    global _config
    if _config is None:
        return _config
    return _config.gets_basic(key)


from pywkmisc.http_client_utils import HttpClientUtils
from pywkmisc.mimetype_utils import MimeTypeUtils
from pywkmisc.multipartform_data import MultipartFormData

