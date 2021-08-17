import smtplib
import ssl
from os.path import basename
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage


def dictfetchall(cursor):
    "Return all rows from a cursor as a Python dictionary"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def build_email_message(message_object):
    """Creates message structure to pass to email

    Keyword arguments:
    message_object -- Dictionary that holds message information
    message = {
        'subject' : 'string',
        'from' : 'string',
        'to' : 'string',
        'text': 'string',
        'file': (csv file_type)
        }
    """
    message = MIMEMultipart()

    message["subject"] = message_object["subject"]
    message["from"] = message_object["from"]
    message["to"] = message_object["to"]

    text = message_object["text"]

    if text:
        message.attach(MIMEText(text))
    try:
        file = message_object['file']
        with open(file, "rb") as file_attachment:
            part = MIMEApplication(file_attachment.read(), Name=basename(file))
        part['Content-Disposition'] = f'attachment; filenames={basename(file)}'
        message.attach(part)
    except:
        print('No file found')

    return message


def send_email(smtp_config, message):
    """ Sends email to destination based off smtp_config

    Keyword arguments:
    smtp_config -- Dictionary that holds smpt account information
        smtp_config = {
            'username' : 'string',
            'password' : 'string',
            'server' : 'string',
            'port': int,
            }
    
    message - object returned from build_email_message
    """
    context = ssl.create_default_context()

    with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
            server.starttls(context=context)
            server.login(user=smtp_config['username'], password=smtp_config['password'])
            server.sendmail(from_addr=message['from'], to_addrs=message['to'], msg=message.as_string())
