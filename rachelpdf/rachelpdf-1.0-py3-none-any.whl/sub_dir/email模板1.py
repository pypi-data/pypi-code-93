#!/usr/bin/python

import smtplib
sender = 'rachelhanlj@outlook.com'
receivers = ['rachelhanlj@163.com']

#smtp
smtpHost = 'smtp.office365.com'
smtpPort = 587
password = "Anhan12!" 

subject = "outlook email test"
# Add the From: and To: headers at the start!
message = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
       % (sender, ", ".join(receivers), subject))

message += """This is a test e-mail message."""

print (message)

try:
    smtpObj = smtplib.SMTP(smtpHost, smtpPort)
    #smtpObj.set_debuglevel(1)
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.ehlo()    

    smtpObj.login(sender,password)
    smtpObj.sendmail(sender, receivers, message)
    smtpObj.quit()
    print ("Successfully sent email")
except SMTPException:
    print ("Error: unable to send email")

