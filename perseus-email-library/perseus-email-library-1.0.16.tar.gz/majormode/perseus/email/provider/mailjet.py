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
import uuid

from mailjet_rest import Client

from majormode.perseus.email.email_service import EmailServiceBase
from majormode.perseus.model.email import Email

# api_key = '05d79dffe420a58a58c1438cb4dc667f'
# api_secret = '03979eb145eb1ecadec29718fe198942'


class MailjetService(EmailServiceBase):
    DEFAULT_MAILJET_VERSION = 'v3.1'

    ENVIRONMENT_KEY_NAME_MAILJET_API_KEY = 'MAILJET_API_KEY'
    ENVIRONMENT_KEY_NAME_MAILJET_API_SECRET = 'MAILJET_API_SECRET'

    def __init__(
            self,
            api_key=None,
            api_secret=None,
            api_version=None):
        super().__init__()

        api_key = api_key or os.getenv(self.ENVIRONMENT_KEY_NAME_MAILJET_API_KEY)
        if api_key is None:
            raise ValueError(f"An API Key must be passed or defined in the environment variable {self.ENVIRONMENT_KEY_NAME_MAILJET_API_KEY}")

        api_secret = api_secret or os.getenv(self.ENVIRONMENT_KEY_NAME_MAILJET_API_SECRET)
        if api_secret is None:
            raise ValueError(f"An API Secret must be passed or defined in the environment variable {self.ENVIRONMENT_KEY_NAME_MAILJET_API_SECRET}")

        self.__client = Client(
            auth=(api_key, api_secret),
            version=api_version or self.DEFAULT_MAILJET_VERSION)

    @staticmethod
    def __build_mailjet_data(emails):
        data = {
            'Messages': [
                {
                    'From': {
                        'Email': email.author.email_address,
                        'Name': email.author.name,
                    },
                    'To': [
                        {
                            'Email': recipient.email_address,
                            'Name': recipient.name
                        }
                        for recipient in email.recipients
                    ],
                    'Subject': email.subject,
                    'TextPart': email.text_content,
                    'HTMLPart': email.html_content,
                    'CustomID': uuid.uuid4().hex
                }
                for email in emails
            ]
        }

        return data

    def send_emails(self, emails):
        emails = self._validate_emails(emails)
        data = self.__build_mailjet_data(emails)
        result = self.__client.send.create(data=data)
        return result
