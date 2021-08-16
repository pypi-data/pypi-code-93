from typing import Iterable, List, Union
import datetime
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP_SSL
from jinja2 import Environment, BaseLoader
import os
from Core.Log import Log


class EmailHelper:
    def __init__(
            self,
            to: str,
            subject,
            html_content,
            files=None,
            cc: str = None,
            mime_subtype='mixed',
            mime_charset='utf-8',
            *args, **kwargs):
        self.to = to
        self.subject = subject
        self.html_content = html_content
        self.files = files or []
        self.cc = cc
        self.mime_subtype = mime_subtype
        self.mime_charset = mime_charset
        self.host_server = kwargs.get('host_server', os.getenv('EMAIL_HOST_SERVER', ''))
        self.sender = kwargs.get('sender', os.getenv('EMAIL_SENDER', ''))
        self.password = kwargs.get('password', os.getenv('EMAIL_PASSWORD', ''))
        self.log = kwargs.get('log', Log(self.__class__.__name__))

    def send_email(self):
        success = False
        retry = 0
        while not success and retry < 5:
            retry += 1
            try:
                msg = MIMEMultipart(self.mime_subtype)
                msg['Subject'] = self.subject
                msg['From'] = self.sender
                to = self.get_email_list_from_str(self.to)
                msg['To'] = ", ".join(to)
                recipients = to
                if self.cc:
                    cc = self.get_email_list_from_str(self.cc)
                    msg['CC'] = ", ".join(cc)
                    recipients = recipients + cc
                msg['Date'] = str(datetime.datetime.now())
                mime_text = MIMEText(self.html_content, 'html', self.mime_charset)
                msg.attach(mime_text)

                smtp = SMTP_SSL(self.host_server)
                smtp.set_debuglevel(0)
                smtp.ehlo(self.host_server)
                smtp.login(self.sender, self.password)
                smtp.sendmail(self.sender, recipients, msg.as_string())
                smtp.quit()
                success = True
            except Exception as e:
                self.log.info(e)
                time.sleep(10)
                self.log.info('retry to send email:', retry)

    @staticmethod
    def get_mail_content(template_str, data):
        template = Environment(loader=BaseLoader()).from_string(template_str)
        return template.render(**data)

    @staticmethod
    def get_email_list_from_str(addresses):  # type: (str) -> List[str]
        delimiters = [",", ";"]
        for delimiter in delimiters:
            if delimiter in addresses:
                return [address.strip() for address in addresses.split(delimiter)]
        return [addresses]


class QaEmailHelper(EmailHelper):
    def __init__(self, **kwargs):
        kwargs['sender'] = 'qacenter@72degreedata.cn'
        kwargs['host_server'] = 'smtp.mxhichina.com'
        kwargs['password'] = os.getenv('QA_EMAIL_PASSWORD')
        super(QaEmailHelper, self).__init__(**kwargs)


class QaErrorEmailHelper(QaEmailHelper):
    def __init__(self, **kwargs):
        super(QaErrorEmailHelper, self).__init__(**kwargs)


class BotEmailHelper(EmailHelper):
    def __init__(self, **kwargs):
        kwargs['sender'] = 'botcenter@72degreedata.cn'
        kwargs['host_server'] = 'smtp.mxhichina.com'
        kwargs['password'] = os.getenv('BOT_EMAIL_PASSWORD')
        super(BotEmailHelper, self).__init__(**kwargs)


class BotErrorEmailHelper(BotEmailHelper):
    def __init__(self, **kwargs):
        super(BotErrorEmailHelper, self).__init__(**kwargs)
