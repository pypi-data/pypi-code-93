#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : ses.py
@Time    : 2021/8/25 14:50
@Author  : ZENKR
@Email   : zenkr@qq.com
@Software: PyCharm
@Desc    :
@license : Copyright (c) 2021 WingEase Technology Co.,Ltd. All Rights Reserved.
"""
import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

import boto3
from botocore.exceptions import ClientError


class Attachment:
    _file_name: str
    _att: MIMEApplication


class SesMail:

    def __init__(self,
                 recipient: str = None,
                 subject: str = None,
                 body_text: str = None,
                 body_html: str = None,
                 charset: str = None,
                 attachments: List[Attachment] = None,
                 sender: str = None,
                 ses_region: str = None,
                 ses_user: str = None,
                 ses_secret: str = None
                 ):
        self._recipient: str = recipient if recipient else ''
        self._subject: str = subject if subject else ''
        self._body_text: str = body_text if body_text else ''
        self._body_html: str = body_html if body_html else ''
        self._charset: str = charset if charset else 'utf-8'
        self._attachments: List[Attachment] = attachments if attachments else []
        self._sender: str = sender if sender else os.getenv('SES_SENDER', 'Amazon <notice@cy-mail.itool.co>')
        self._init_client(ses_region, ses_user, ses_secret)
        self._init_msg()

    def _init_client(self,
                     ses_region: str = None,
                     ses_user: str = None,
                     ses_secret: str = None,
                     ):
        _SES_REGION: str = ses_region if ses_region else os.getenv('SES_REGION', 'us-west-2')
        _SES_USER: str = ses_user if ses_user else os.getenv('SES_USER', '')
        _SES_SECRET: str = ses_secret if ses_secret else os.getenv('SES_SECRET', '')
        self._client: boto3.client = boto3.client(
            service_name='ses',
            region_name=_SES_REGION,
            aws_access_key_id=_SES_USER,
            aws_secret_access_key=_SES_SECRET
        )

    def _init_msg(self):
        self._msg: MIMEMultipart = MIMEMultipart('mixed')
        self._msg['Subject'] = self._subject
        self._msg['From'] = self._sender
        self._msg['To'] = self._recipient
        msg_body = MIMEMultipart('alternative')
        text_part = MIMEText(self._body_text.encode(self._charset), 'plain', self._charset)
        html_part = MIMEText(self._body_html.encode(self._charset), 'html', self._charset)
        msg_body.attach(text_part)
        msg_body.attach(html_part)
        self._msg.attach(msg_body)
        for attachment in self._attachments:
            att = attachment._att
            file_name = attachment._file_name
            att.add_header('Content-Disposition', 'attachment', filename=file_name)
            self._msg.attach(att)

    def send(self):
        try:
            response = self._client.send_raw_email(
                Source=self._sender,
                Destinations=[self._recipient],
                RawMessage={
                    'Data': self._msg.as_string(),
                },
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print('Email sent! Message ID:'),
            return response['ResponseMetadata']['RequestId']
