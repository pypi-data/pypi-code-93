from .connect import Connection
from email.mime.text import MIMEText
from base64 import urlsafe_b64encode

"""
https://developers.google.com/gmail/api/guides/sending
"""

gm = Connection().gmail_too()


def body(message, subject, sender, recipients):
    email_txt = MIMEText("\n".join(message))
    email_txt["Subject"] = subject
    email_txt["Fromt"] = sender
    email_txt["To"] = "\n".join(recipients)
    return urlsafe_b64encode(bytes(email_txt.as_string(), "utf-8"))


msg = body(["this is a test"], "Test 1.0", "me", ["iverson.jace@gmail.com"])

info = gm.users().messages().send(userId="me", body=msg).execute()
