from typing import *

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from quicly.logutils import QxLogging


logging = QxLogging.get_logger('QxMail')


class QxMail(object):
  def __init__(self):
    self._from_addr = None
    self._to_addrs = []
    self._cc_addrs = []
    self._bcc_addrs = []
    self._subject = None
    self._content = None
    self._attachments = []

  def __str__(self) -> str:
    return f'{self._subject} -> {self._to_addrs}'

  @property
  def from_addr(self) -> str:
    return self._from_addr

  @property
  def to_addrs(self) -> List[str]:
    return self._to_addrs

  @property
  def msg(self) -> str:
    ret = MIMEMultipart()
    ret['From'] = self._from_addr
    ret['To'] = ';'.join(self._to_addrs)
    if self._cc_addrs:
      ret['Cc'] = ';'.join(self._cc_addrs)
    if self._bcc_addrs:
      ret['Bcc'] = ';'.join(self._bcc_addrs)
    ret['Subject'] = self._subject
    if isinstance(self._content, MIMEText):
      ret.attach(self._content)
    if isinstance(self._attachments, list):
      for attach in self._attachments:
        if isinstance(attach, MIMEApplication):
          ret.attach(attach)
    return ret.as_string()

  def set_from_addr(self, from_addr: str):
    self._from_addr = from_addr
    return self  # type: QxMail

  def add_to_addrs(self, *to_addrs):
    if not isinstance(self._to_addrs, list):
      self._to_addrs = list()
    self._to_addrs += to_addrs
    return self  # type: QxMail

  def add_cc_addrs(self, *cc_addrs):
    if not isinstance(self._cc_addrs, list):
      self._cc_addrs = list()
    self._cc_addrs += cc_addrs
    return self  # type: QxMail

  def add_bcc_addrs(self, *bcc_addrs):
    if not isinstance(self._bcc_addrs, list):
      self._bcc_addrs = list()
    self._bcc_addrs += bcc_addrs
    return self  # type: QxMail

  def set_subject(self, subject: str):
    self._subject = subject
    return self  # type: QxMail

  def set_text_content(self, content: str, charset: str = 'utf-8'):
    self._content = MIMEText(content, _charset=charset)
    return self  # type: QxMail

  def set_html_content(self, content: str, charset: str = 'utf-8'):
    self._content = MIMEText(content, _subtype='html', _charset=charset)
    return self  # type: QxMail

  def add_attachment(self, filename: str):
    with open(filename, 'rb') as fo:
      data = fo.read()
    attach = MIMEApplication(data)
    attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filename))
    self._attachments.append(attach)
    return self  # type: QxMail


class QxMailClient(object):
  def __init__(self, username: str, password: str, host: str = None, port: int = None, ssl: bool = True):
    self._username = username
    self._password = password
    default_host = 'smtp.{}'.format(username.split('@', maxsplit=1)[1])
    default_port = smtplib.SMTP_SSL_PORT if ssl else smtplib.SMTP_PORT
    self._host = host if host else default_host
    self._port = port if port else default_port
    self._ssl = bool(ssl)
    self._smtp_client = None
    self._mails = list()

  def __enter__(self):
    self._mails = list()
    self._login()

  def __exit__(self, exc_type, exc_val, exc_tb):
    for mail in self._mails:
      self._send(mail)
    self._logout()
    self._mails = list()

  def _login(self):
    if not isinstance(self._smtp_client, smtplib.SMTP):
      smtp_client = smtplib.SMTP_SSL(host=self._host, port=self._port) if self._ssl else smtplib.SMTP(host=self._host, port=self._port)
      try:
        smtp_client.login(user=self._username, password=self._password)
      except smtplib.SMTPException:
        smtp_client.quit()
        smtp_client.close()
        smtp_client = None
      self._smtp_client = smtp_client

    if isinstance(self._smtp_client, smtplib.SMTP):
      logging.info(f'邮箱登录成功: {self._username}')
    else:
      logging.fatal(f'邮箱登录失败: {self._username}')

    return self  # type: QxMailClient

  def _logout(self):
    if isinstance(self._smtp_client, smtplib.SMTP):
      self._smtp_client.quit()
      self._smtp_client.close()
      logging.info(f'邮箱登出成功: {self._username}')
    self._smtp_client = None

  def _send(self, mail: QxMail):
    if isinstance(self._smtp_client, smtplib.SMTP):
      if mail.to_addrs:
        try:
          self._smtp_client.sendmail(
            from_addr=mail.from_addr if mail.from_addr else self._username,
            to_addrs=mail.to_addrs,
            msg=mail.msg,
          )
          logging.error(f'邮件发送成功: {mail}')
        except smtplib.SMTPException as e:
          logging.error(f'邮件发送失败: {mail}')
          logging.error(e)
      else:
        logging.error(f'邮件发送失败: {mail}, 没有指定收件人地址')
    else:
      logging.error(f'邮箱未成功登录,无法发送邮件: {mail}')

  def new_mail(self) -> QxMail:
    self._mails.append(QxMail().set_from_addr(self._username))
    return self._mails[-1]
