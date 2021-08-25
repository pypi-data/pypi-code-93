import os, re
import socket
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from multiprocessing import Process
import boto3

default_address_book = {
    'jneto': {'email': 'joao.filipe.neto@gmail.com', 'phone': '+351966221506'},
    'jranito': {'email': 'joao.vasco.ranito@gmail.com', 'phone': '+351966221505'},
}

def read_address_book():
    try:
        with open('./.addressbook') as f: d = json.loads(f.read())
    except IOError:
        return None
    return d

# SendGrid
def send_mail(api_key, to, subject='NO SUBJECT', msg=None, html=None, files=[]):
    html2 = html or msg
    msg = Mail(from_email='ops@dl2050.com', to_emails=to, subject=subject, html_content=html2)
    try:
        sg = SendGridAPIClient(api_key)
        res = sg.send(msg)
    except Exception as e:
        return f'SendGrid ERROR: {str(e)}'
    if res.status_code!=202: return f'SendGrid ERROR: status code={res.status_code}'
    return None

def send_mail_async(api_key, to, subject=None, msg=None, html=None, files=[]):
    p = Process(target=send_mail, args=(api_key, to, subject, msg, html, files), daemon=True)
    p.start()

def send_sms_aws(sms_id, sms_passwd, to, msg):
    MessageAttributes={'AWS.SNS.SMS.SenderID': {'DataType': 'String','StringValue': 'DLOPS'}}
    client = boto3.client('sns', aws_access_key_id=sms_id, aws_secret_access_key=sms_passwd, region_name="eu-west-1")
    client.publish(PhoneNumber=to, Message=msg, MessageAttributes=MessageAttributes)
    return None

#from twilio.rest import Client
#def send_sms_twilio(sms_id, sms_passwd, to, msg):
#    #account_sid, auth_token
#    client = Client(sms_id, sms_passwd)
#    message = client.messages.create(to=to, from_='DLbot', body=msg)
#    #print(message.sid)
#    return None

def send_sms(sms_id, sms_passwd, to, msg):
    return send_sms_aws(sms_id, sms_passwd, to, msg)

class Notify():
    def __init__(self, cfg=None, api_key=None, sms_id=None, sms_passwd=None, address_book=None):
        self.address_book = address_book if address_book is not None else default_address_book
        if cfg is not None:
            try:
                api_key = cfg['email']['sendgrid_api_key']
                sms_id = cfg['aws']['aws_access_key_id']
                sms_passwd = cfg['aws']['aws_secret_access_key']
            except Exception as e:
                print(f'Config ERROR: cant find variable: {e}')
        self.api_key = api_key
        self.sms_id = sms_id
        self.sms_passwd = sms_passwd
        
    def __call__(self, how, who, subject=None, msg=None, html=None, files=[]):
        if how not in ['email', 'email_async', 'sms']: return 'Invalid method, options are email, email_async or sms'
        if who is None or who not in self.address_book: return 'Destination not found in address book'
        if msg is None: return 'Nothing to notify'
        if how=='email' or how=='email_async':
            if self.api_key is None: return 'email credentials not defined'
            if 'email' not in self.address_book[who]: return f'email address not found for {who}'
        if how == 'email_async':
            return self.send_mail_async(self.address_book[who]['email'], subject=subject, msg=msg, html=html, files=files)
        if how == 'email':
            return self.send_mail(self.address_book[who]['email'], subject=subject, msg=msg, html=html, files=files)
        if how=='sms':
            if self.sms_id is None or self.sms_passwd is None: return 'sms credentials not defined'
            if 'phone' not in self.address_book[who]: return f'phone number not found for {who}'
            return send_sms(self.sms_id, self.sms_passwd, self.address_book[who]['phone'], msg)
    
    def send_mail_async(self, to, subject=None, msg=None, html=None, files=[]):
        send_mail_async(self.api_key, to, subject=subject, msg=msg, html=html, files=files)
    
    def send_mail(self, to, subject=None, msg=None, html=None, files=[]):
        return send_mail(self.api_key, to, subject=subject, msg=msg, html=html, files=files)

    def send_sms(self, to, msg):
        return send_sms(self.sms_id, self.sms_passwd, to, msg)

EMAIL_TEMPLATE = \
"""
<html>
<head>
    <link href="https://fonts.googleapis.com/css?family=Muli::100,200,300,400,500,600,700,800" rel="stylesheet">
</head>
    <body style="position: relative; float: left; width: 100%; height: 100%;  text-align: center; font-family: 'Muli', sans-serif;">
        <h2 style="float: left; width: 100%; margin: 40px 0px 10px 0px; font-size: 16px; text-align: center; color: #555555;">{msg}</h2>
        <h2 style="float: left; width: 100%; margin: 0px 0px 40px 0px; font-size: 24px; text-align: center; color: #61C0DF; font-weight: bold;">{otp}</h2>
    </body>
</html>
"""

def send_otp_by_email(notify, product, email, otp):
    try:
        subject = f'{product} OTP'
        msg = f'{product} OTP: '
        html = EMAIL_TEMPLATE
        html = re.sub(r'{msg}', msg, html)
        html = re.sub(r'{otp}', f'{otp}', html)
        notify.send_mail_async(email, subject=subject, html=html)
    except Exception as e:
        return str(e)
    return None

def send_otp_by_phone(notify, product, phone, otp):
    msg = f'{product} OTP: {otp}'
    try:
        notify.send_sms(phone, msg)
    except Exception as e:
        return str(e)
    return None

def send_otp(notify, mode, product, email, phone, otp):
    if mode=='phone': return send_otp_by_phone(notify, product, phone, otp)
    return send_otp_by_email(notify, product, email, otp)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP