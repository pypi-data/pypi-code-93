from abc import ABC
from typing import Optional
import smtplib
from pydantic import BaseModel
from lgt.common.python.lgt_logging import log
from .basejobs import BaseBackgroundJobData, BaseBackgroundJob
from .env import smtp_login, smtp_password, smtp_host

"""
Send email
"""
class SendMailJobData(BaseBackgroundJobData, BaseModel):
    html: str
    subject: str
    recipient: str
    sender: Optional[str]

class SendMailJob(BaseBackgroundJob, ABC):
    @property
    def job_data_type(self) -> type:
        return SendMailJobData

    def exec(self, data: SendMailJobData):
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        import ssl

        sender = "noreply@leadguru.co" if not data.sender else data.sender
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = data.subject
        msg['From'] = sender
        msg['To'] = data.recipient
        part = MIMEText(data.html, 'html')
        msg.attach(part)
        server = smtplib.SMTP(smtp_host, port=587)
        server.ehlo()
        server.starttls(context=context)
        server.login(smtp_login, smtp_password)

        server.sendmail(sender, data.recipient, msg.as_string())
        server.quit()
        log.info('email message has been sent')