from __future__ import annotations

import aiosmtplib

from email.mime.text import MIMEText
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader, select_autoescape


class SmtpHtml:
    def __init__(self, path: str, file: str,
                 url_key: str = "url") -> None:
        """Configure SMTP html template

        Parameters
        ----------
        path : str
            Path to jinja2 templates.
        file : str
            Name of jinja2 template.
        url_key : str, optional
            Key for validation email url,
            by default "url"
        """

        self._jinja2 = Environment(
            loader=FileSystemLoader(path),
            autoescape=select_autoescape(["html", "xml"])
        )

        self._file = file
        self._url_key = url_key


class SmtpClient:
    def __init__(self, host: str, port: int, email: str,
                 **kwargs) -> None:
        """Used to configure SMTP.

        Parameters
        ----------
        host : str
        port : int
        email : str
            Email address to send as.

        Notes
        -----
        Kwargs are passed to aiosmtplib's
        SMTP client.

        https://aiosmtplib.readthedocs.io/en/stable/client.html
        """

        self._details = {
            "hostname": host,
            "port": port,
            **kwargs
        }

        self._email = email

        self._email_types = {
            "confirm": {
                "raw": "Please confirm your email\n{link}",
                "raw_place": True,
                "html": None,
                "subject": "Please confirm your email!",
                "url": "",
                "contains_code": False
            },
            "reset": {
                "raw": "Follow this link to reset your password\n{link}",
                "raw_place": True,
                "html": None,
                "subject": "Password reset request",
                "url": "",
                "contains_code": False
            }
        }

    def confirm_layout(self, url: str, html: SmtpHtml = None,
                       raw: str = None, subject: str = None
                       ) -> SmtpClient:
        """Used for confirm email layout.

        Parameters
        ----------
        url : str
            Url user follows for validation
            If it doesn't contain '{validation_code}'
            the validation code will be append
            to the end of the url

            e.g.
            https://example.com/validate?code={validation_code}
        html: SmtpHtml, optional
            by default None
        raw : str, optional
            Should contain 'link' otherwise
            appended at the end of the string,
            by default None
        subject : str, optional
            Used to set email subject for confirmations.
            by default None

        Returns
        -------
        SmtpClient
        """

        self._email_types["confirm"]["url"] = url
        self._email_types["confirm"][
            "contains_code"
        ] = "{validation_code}" in url

        if raw:
            self._email_types["confirm"]["raw"] = raw
            self._email_types["confirm"]["raw_place"] = (
                "{link}" in raw
                if raw else False
            )

        if html:
            self._email_types["confirm"]["html"] = html

        if subject:
            self._email_types["confirm"]["subject"] = subject

        return self

    def reset_layout(self, url: str, html: SmtpHtml = None,
                     raw: str = None, subject: str = None
                     ) -> SmtpClient:
        """Used for reset email layout.

        Parameters
        ----------
        url : str
            Url user follows for validation
            If it doesn't contain '{validation_code}'
            the validation code will be append
            to the end of the url

            e.g.
            https://example.com/validate?code={validation_code}
        html: SmtpHtml, optional
            by default None
        raw : str, optional
            Should contain 'link' otherwise
            appended at the end of the string,
            by default None
        subject : str, optional
            Used to set email subject for resets.
            by default None

        Returns
        -------
        SmtpClient
        """

        self._email_types["confirm"]["url"] = url
        self._email_types["confirm"][
            "contains_code"
        ] = "{validation_code}" in url

        if raw:
            self._email_types["reset"]["raw"] = raw
            self._email_types["reset"]["raw_place"] = (
                "{link}" in raw
                if raw else False
            )

        if html:
            self._email_types["reset"]["html"] = html

        if subject:
            self._email_types["reset"]["subject"] = subject

        return self

    async def _send(self, email: str, code: str, type_: str) -> None:
        """Used to send a email.

        Parameters
        ----------
        email : str
        code : str
        type_ : str
            email type
        """

        email_type = self._email_types[type_]

        if email_type["contains_code"]:
            link = email_type["url"].format(validation_code=code)
        else:
            link = email_type["url"] + code

        if email_type["html"]:
            message = MIMEText(email_type["html"]._jinja2.get_template(
                email_type["html"]._file
            ).render({email_type["html"]._url_key: link}), "html", "utf-8")
        else:
            message = EmailMessage()

            if email_type["raw"]:
                if email_type["raw_place"]:
                    content = email_type["raw"].format(link=link)
                else:
                    content = email_type["raw"] + link
            else:
                content = link

            message.set_content(content)

        message["From"] = self._email
        message["To"] = email
        message["Subject"] = email_type["subject"]

        await aiosmtplib.send(message, **self._details)
