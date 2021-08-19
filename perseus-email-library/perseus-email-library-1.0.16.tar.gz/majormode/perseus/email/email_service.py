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

import abc

from majormode.perseus.model.email import Email


class EmailServiceBase(metaclass=abc.ABCMeta):
    def __init__(self):
        pass

    @staticmethod
    def _validate_emails(emails):
        if isinstance(emails, (list, set, tuple)):
            if any([not isinstance(email, Email) for email in emails]):
                raise ValueError("Items of argument 'emails' MUST be instances of 'Email'")
        else:
            if not isinstance(emails, Email):
                raise ValueError("Argument 'emails' MUST be an instance of 'Email'")
            emails = [emails]

        return emails

    @abc.abstractmethod
    def send_emails(self, emails):
        raise NotImplementedError()
