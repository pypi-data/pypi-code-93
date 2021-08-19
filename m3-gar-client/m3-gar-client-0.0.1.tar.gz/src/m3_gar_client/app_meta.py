# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import m3_gar_client


def register_actions():
    m3_gar_client.config.backend.register_packs()
