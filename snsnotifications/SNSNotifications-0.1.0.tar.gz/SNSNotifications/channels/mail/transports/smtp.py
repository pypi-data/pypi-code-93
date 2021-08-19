import smtplib
from email.message import EmailMessage

from ..mailable import Mailable
from ..transport import Transport


class SmtpTransport(Transport):

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.username = None
        self.password = None
        self.encryption = False
        self.default_from_addr = None
        self.default_from_name = None

    def send(self, mailable: Mailable):
        if self.encryption:
            smtp = smtplib.SMTP_SSL(self.host, self.port)
        else:
            smtp = smtplib.SMTP(self.host, self.port)
        if self.username:
            smtp.login(self.username, self.password)
        from_addr = mailable.from_addr or self.default_from_addr
        from_name = mailable.from_name or self.default_from_name or from_addr
        to_addrs = mailable.to_addr
        msg = EmailMessage()
        if mailable.reply_to is not None:
            msg.add_header('reply-to', mailable.reply_to)

        msg['subject'] = mailable.subject
        msg['from'] = "{} <{}>".format(from_name, from_addr)
        msg['to'] = mailable.to_addr

        if mailable.cc is not None:
            msg['cc'] = list(mailable.cc)
            to_addrs += list(mailable.cc)
        if mailable.bcc is not None:
            msg['bcc'] = list(mailable.bcc)
            to_addrs += list(mailable.bcc)
        if mailable.attachments is not None:
            for attachment in mailable.attachments:
                content = attachment['content']
                filename = attachment['filename']
                attachment_kwarg = {}
                for (k, v) in attachment:
                    if k == 'content' or k == 'filename':
                        continue
                    attachment_kwarg[k] = v
                msg.add_attachment(content, filename=filename, **attachment_kwarg)
        if mailable.html:
            msg.set_content(mailable.html, subtype='html')
        else:
            msg.set_content(mailable.plain)
        smtp.sendmail(from_addr=from_addr,
                      to_addrs=to_addrs,
                      msg=msg.as_string())
