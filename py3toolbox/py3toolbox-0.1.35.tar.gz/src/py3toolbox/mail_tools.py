import os
import sys
import re
import smtplib
import email  
import ssl

from email import encoders
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email.mime.image import MIMEImage

def send_mail(config=None):
  """
  sample usage : 
    config = {
        "Subject"     : "This is Mail subject",
        "From"        : "test_12345@tpg.com.au",
        "To"          : "chgpnt@gmail.com",
        "Attachments"  : ["R:/panda.jpg", "R:/tiger.jpg", "R:/baby.jpg"],
        "Body"        : "This is Mail subject",
        "smtp_host"   : "mail.tpg.com.au",
        "smtp_port"   : 465
    }

  """

  msg = MIMEMultipart()
  msg['Subject'] = config["Subject"] 
  msg['From'] = config["From"]
  msg['To'] =  config["To"]

  msg.attach(MIMEText(config["Body"], 'plain'))

  for filename in config["Attachments"]:
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(filename, "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename=' + os.path.basename(filename))
    msg.attach(part)

  context = ssl.create_default_context()
  with smtplib.SMTP_SSL(config["smtp_host"] , config["smtp_port"] , context=context) as server:
    server.sendmail(config["From"], config["To"], msg.as_string())


  pass


def send_gmail (sender_account, sender_password, smtp,smtp_port,senders,receivers,subject,body,attachments):
  msg               = MIMEMultipart()
  msg["From"]       = senders
  msg["To"]         = receivers
  msg["Subject"]    = subject
  
  msg.attach(MIMEText(body, 'plain'))

  for filename in attachments:
    with open(filename, 'rb') as fp:
      part = MIMEBase("application", "octet-stream")
      part.set_payload(fp.read())
    encoders.encode_base64(part)
    attachment_name = os.path.basename(filename)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename={attachment_name}",
    )
    msg.attach(part)

  text = msg.as_string()


  context = ssl.create_default_context()
  with smtplib.SMTP_SSL(smtp, smtp_port, context=context) as server:
    server.login(sender_account, sender_password)
    server.sendmail(senders, receivers, text)



if __name__ == "__main__":
  config = {
      "Subject"     : "test_icc_group_email",
      "From"        : "test_icc_group_email@gmail.com",
      "To"          : "fan.yang36@tafensw.edu.au",
      "Attachments" : [],
      "Body"        : "This is a test of ICC group email",
      "smtp_host"   : "mail.tpg.com.au",
      "smtp_port"   : 465
  }
  send_mail(config)
  """
  send_gmail('xxxxxx@gmail.com',
            'xxxxxx',
            'smtp.gmail.com', 
            465, 
            'xxxxx@gmail.com',
            'xxxxx@test.com',
            'System Monitor ' ,
            'blablabla',
            ["R:/car.jpg", "R:/car.rar", "R:/1.cat"]
            )
  """