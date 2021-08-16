#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2020/6/30 9:36
@Author  : WaveletAI-Product-Team Janus
@license : (C) Copyright 2019-2022, Visionet(Tianjin)Information Technology Co.,Ltd.
@Site    : plus.xiaobodata.com
@File    : __init__.py.py
@Desc    : The ``waveletai.entities`` module defines entities
"""

from waveletai.entities import mqtt_repo, minio_repo, minio_bucket, mqtt_topic

__all__ = [
    "mqtt_repo",
    "minio_repo",
    "minio_bucket",
    "mqtt_topic"
]
