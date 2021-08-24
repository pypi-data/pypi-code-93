import datetime
import os
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from constants import *


class EmailSender:

    def __init__(self):
        self.summation_file = self.get_file()
        self.msg = None
        self.sender_email = None
        self.receiver_email = None
        self.password = None
        self.body = self.read_body()
        self.context = None
        self.establish_email_params()
        self.bool = self.send_email()

    @staticmethod
    def read_body():
        with open(os.path.dirname(os.path.realpath(__file__)) + "/Template/summation_file.txt") as file:
            return file.read()

    def get_file(self):
        initial_name = SUMMATION_FILE
        if OUTPUT_TYPE in ["csv", "json"]:
            initial_name += '.{}'.format(self.file_type_preference.lower())
        elif OUTPUT_TYPE == "excel":
            initial_name += '.xlsx'
        else:
            print("Invalid format given in Constants")
        return initial_name

    def establish_email_params(self):
        self.msg = MIMEMultipart()
        self.sender_email = EMAIL_FROM
        self.receiver_email = RECIPIENT
        self.password = PASSWORD
        self.msg['From'] = self.sender_email
        self.msg['To'] = self.receiver_email
        self.msg['Date'] = formatdate(localtime=True)
        self.msg['Subject'] = 'Here is the LPBI Views File for {}'.format(
            datetime.date.today())

    def send_email(self):
        email_sent_status = False
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(self.summation_file, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment',
                        filename=self.summation_file.split('/')[-1])
        self.msg.attach(part)
        self.msg.attach(MIMEText(self.body, "plain"))
        self.context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=self.context) as server:
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, self.receiver_email.split(
                    ","), self.msg.as_string())
        except Exception as e:
            print(type(e).__name__ + ': ' + str(e))
        else:
            email_sent_status = True
        finally:
            return email_sent_status


if __name__ == "__main__":
    EmailSender()
