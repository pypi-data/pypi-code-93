
import smtplib
import ssl
from . import config
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
import asgiref.sync

DEFAULT_PORT = 465


class Message :

    def __init__ ( self, subject : str,
                   fromAddress : str, recipients : [], plaintext : str = None, html : str = None ) :

        self.html        = html
        self.plaintext   = plaintext
        self.subject     = subject
        self.fromAddress = fromAddress
        self.recipients  = recipients

    def asMultipart ( self ) :

        # message = MIMEMultipart('alternative')
        message = EmailMessage()
        message['Subject'] = self.subject
        message['From'] = self.fromAddress
        message['To'] = ', '.join(self.recipients)

        if self.plaintext:
            # message.attach( MIMEText(self.plaintext, 'plain'))
            message.preamble = "Preamble: " + self.plaintext
            message.set_content( self.plaintext + "\n\n\nplain" )
        if self.html:
            # message.attach( MIMEText(self.html, 'html'))
            message.add_alternative( self.html, subtype='html')
        # return message.as_string()
        return message


class Mailer :

    def __init__ ( self, configuration : {} ):

        self.port        = config.dictread( configuration, "MailPort", DEFAULT_PORT )
        self.host        = config.forceread( configuration, "MailHost" )
        self.password    = config.forceread( configuration, "MailPassword" )
        self.user        = config.forceread( configuration, "MailUser" )
        self.fromAddress = config.forceread( configuration, "MailFrom" )

    async def sendMail ( self, subject : str, recipients : [], plaintext : str = None, html : str = None ):

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL( self.host, self.port, context=context ) as server:
            server.login( self.user, self.password )
            message = Message(subject, self.fromAddress, recipients, plaintext, html )

            # server.sendmail( self.fromAddress, recipients, message.asMultipart() )
            await asgiref.sync.sync_to_async(server.send_message)(message.asMultipart())
