# Copyright (C) 2021 Majormode.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import smtplib

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from majormode.perseus.email.email_service import EmailServiceBase


class GmailService(EmailServiceBase):
    ENVIRONMENT_KEY_NAME_GMAIL_USERNAME = 'GMAIL_USERNAME'
    ENVIRONMENT_KEY_NAME_GMAIL_PASSWORD = 'GMAIL_PASSWORD'

    GMAIL_DEFAULT_HOSTNAME = 'smtp.gmail.com'
    GMAIL_DEFAULT_PORT_NUMBER = 587

    @staticmethod
    def __add_attached_files(message, file_path_names):
        """
        Attach the specified files to the message.


        :param message: An object `MIMEMultipart`.

        :param file_path_names: A path-like or a list of path-like objects
            giving the absolute pathname of the file(s) to be attached to the
            email.


        :return: The message argument passed to this function.
        """
        if file_path_names:
            if not isinstance(file_path_names, (list, set, tuple)):
                file_path_names = [file_path_names]

            for file_path_name in file_path_names or []:
                part = MIMEBase('application', 'octet-stream')

                with open(file_path_name, 'rb') as handle:
                    part.set_payload(handle.read())

                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path_name))
                message.attach(part)

        return message

    @staticmethod
    def __add_content(message, email):
        content_type, content = ('plain', email.text_content) if email.html_content is None \
            else ('html', email.html_content)

        message.attach(MIMEText(
            content.encode('utf-8'),
            _charset='utf-8',
            _subtype=content_type))

        return message

    @classmethod
    def __add_header_fields(cls, message, email):
        message['From'] = cls.__build_author_name_expr(email.author)
        message['To'] = ', '.join([
            recipient.email_address
            for recipient in email.recipients
        ])

        if email.cc_recipients:
            message['Cc'] = ', '.join([
                cc_recipient.email_addresses
                for cc_recipient in email.cc_recipients
            ])

        if email.bcc_recipients:
            message['Bcc'] = ', '.join([
                bcc_recipient.email_addresses
                for bcc_recipient in email.bcc_recipients
            ])

        message['Date'] = formatdate(localtime=True)
        message['Subject'] = email.subject

        if email.author.email_address:
            message.add_header('Reply-To', email.author.email_address)

        return message

    @staticmethod
    def __add_unsubscribe_methods(
            message,
            unsubscribe_mailto_link=None,
            unsubscribe_url=None):
        """"
        Add method(s) to unsubscribe a recipient from a mailing list at his
        request.


        :param message: An object `MIMEMultipart`.

        :param unsubscribe_mailto_link: an email address to directly
            unsubscribe the recipient who requests to be removed from the
            mailing list (https://tools.ietf.org/html/rfc2369.html).

            In addition to the email address, other information can be provided.
            In fact, any standard mail header fields can be added to the mailto
            link.  The most commonly used of these are "subject", "cc", and "body"
            (which is not a true header field, but allows you to specify a short
            content message for the new email). Each field and its value is
            specified as a query term (https://tools.ietf.org/html/rfc6068).

        :param unsubscribe_url: a link that will take the subscriber to a
            landing page to process the unsubscribe request.  This can be a
            subscription center, or the subscriber is removed from the list
            right away and gets sent to a landing page that confirms the
            unsubscribe.


        :return: The message argument passed to this function.
        """
        if unsubscribe_mailto_link or unsubscribe_url:
            unsubscribe_methods = [
                unsubscribe_url and f'<{unsubscribe_url}>',
                unsubscribe_mailto_link and f'<mailto:{unsubscribe_mailto_link}>',
            ]

            message.add_header('List-Unsubscribe', ', '.join([
                method
                for method in unsubscribe_methods
                if method]))

        return message

    @staticmethod
    def __build_all_destination_email_addresses(email):
        email_addresses = [
            recipient.email_address
            for recipient in email.recipients
        ]

        if email.cc_recipients:
            email_addresses += [
                recipient.email_address
                for recipient in email.cc_recipients
            ]

        if email.bcc_recipients:
            email_addresses += [
                recipient.email_address
                for recipient in email.bcc_recipients
            ]

        return email_addresses

    @staticmethod
    def __build_author_name_expr(author):
        """
        Build the name of the author of a message as described in the Internet
        Message Format specification: https://tools.ietf.org/html/rfc5322#section-3.6.2


        :param author: An object `EmailUser`.


        :return: a string representing the author of the message, that is, the
            mailbox of the person or system responsible for the writing of the
            message.  This string is intended to be used as the "From:" field
            of the message.
        """
        assert author.name is not None or author.email_address is not None, "Both arguments MUST NOT be bull"

        # Use the specified name of the author or the username of his email
        # address.
        author_name_expr = author.name \
            or author.email_address[:author.email_address.find('@')]

        # Escape the name of the author if it contains a space character.
        if ' ' in author_name_expr:
            author_name_expr = f'"{author_name_expr}"'

        # Complete the name of the author with his email address when specified.
        if author.email_address:
            author_name_expr = f"{author_name_expr} <{author.email_address}>"

        return author_name_expr

    @classmethod
    def __build_email_message(
            cls,
            email):
        """
        Build the message to be sent.


        :param email: An object `Email`.


        :return: An object `MIMEMultipart`.
        """
        message = MIMEMultipart()
        cls.__add_header_fields(message, email)

        if email.are_unsubscribe_methods_available:
            message = cls.__add_unsubscribe_methods(
                message,
                unsubscribe_mailto_link=email.unsubscribe_mailto_link,
                unsubscribe_url=email.unsubscribe_url)

        cls.__add_content(message, email)
        if email.attached_files:
            cls.__add_attached_files(message, email.attached_files)

        return message

    def __init__(
            self,
            hostname=GMAIL_DEFAULT_HOSTNAME,
            port_number=GMAIL_DEFAULT_PORT_NUMBER,
            username=None,
            password=None):
        """

        :param port_number: Internet port number on which the remote SMTP
            server is listening at.

            SMTP communication between mail servers uses TCP port 25.  Mail
            clients on the other hand, often submit the outgoing emails to a mail
            server on port 587.  Despite being deprecated, mail providers
            sometimes still permit the use of nonstandard port 465 for this
            purpose.
        """
        super().__init__()
        self.__hostname = hostname
        self.__port_number = port_number

        self.__username = username or os.getenv(self.ENVIRONMENT_KEY_NAME_GMAIL_USERNAME)
        if self.__username is None:
            raise ValueError("A Gmail username must be passed or defined in the environment "
                             f"variable {self.ENVIRONMENT_KEY_NAME_GMAIL_USERNAME}")

        self.__password = password or os.getenv(self.ENVIRONMENT_KEY_NAME_GMAIL_PASSWORD)
        if self.__password is None:
            raise ValueError("The password of the Gmail user must be passed or defined in the "
                             f"environment variable {self.ENVIRONMENT_KEY_NAME_GMAIL_PASSWORD} "
                             "(not recommended)")

    def __send_email(self, email):
        message = self.__build_email_message(email)

        # Connect the remote mail server and send the message.
        smtp_server = smtplib.SMTP_SSL(self.__hostname) if self.__port_number == 465 \
            else smtplib.SMTP(self.__hostname, self.__port_number)
        smtp_server.ehlo()

        if self.__port_number != 465:
            smtp_server.starttls()
            smtp_server.ehlo()

        smtp_server.login(self.__username, self.__password)
        email_addresses = self.__build_all_destination_email_addresses(email)
        smtp_server.sendmail(email.author.email_address, email_addresses, message.as_string())
        smtp_server.close()

    def send_emails(self, emails):
        emails = self._validate_emails(emails)
        for email in emails:
            self.__send_email(email)