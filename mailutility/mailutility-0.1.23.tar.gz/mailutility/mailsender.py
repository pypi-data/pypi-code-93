import getpass
import smtplib
import warnings
from typing import Union, List
from pathlib import Path
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate


QUIT_ERROR = "Fail to quit"


class ConnectionFailed(Exception):
    pass


class MailSender(object):

    # noinspection PyUnresolvedReferences
    """Utils to send mails, supports attaching files. Only compatible with an sending account that does not use a
        double authentification method.

    Examples
    --------

    >>> from mailutility import MailSender  # doctest: +SKIP
    >>> from transparentpath import TransparentPath as Tp  # doctest: +SKIP
    >>> some_directory_path = Tp("gs://my_bucket/some_dir")  # doctest: +SKIP
    >>> # If the password is not provided, you will asked to provide it interactively
    >>> ms = MailSender(sender="chien@chat.com", passwd="thepasswd")  # doctest: +SKIP
    >>> ms.test_mail_server()  # doctest: +SKIP
    >>> ms.send_mail(  # doctest: +SKIP
    >>>    adresses=["foo@bar.com", "foo2@bar2.com"],  # doctest: +SKIP
    >>>    subject=f"the mail subject",  # doctest: +SKIP
    >>>    files=[some_directory_path / "some_file_name.pdf",  # doctest: +SKIP
    >>>           some_directory_path / "some_other_file_name.csv"],  # doctest: +SKIP
    >>> )  # doctest: +SKIP

        """

    hostname = ""
    default_mail = ""
    logger = None

    def __init__(self, sender: str = None, passwd: str = None, do_raise: bool = True):
        """
        If sender or password is not specified, you will be prompted for
        them when trying to connect.

        Parameters
        ----------

        sender: str
            The username or full address of the sender. Must match a valid email account

        passwd: str
            The password matching the sender

        do_raise: bool
            If True, will raise exception. Else, log them and pass

        """
        self.sender = sender
        self.passwd = passwd
        self.do_raise = do_raise
        self.smtp = None

    def set_mail_server(self) -> bool:
        """ Will set self.smtp
        If the login and passwd are already known, just try to reconnect.
        Else, will prompt for username and passwd. If connection fails,
        will prompt again in case a typo was made, and that up to three
        times. After, will return False.

        Returns
        -------
        bool
            True if connection is successful, False if not. If self.do_raise is
            True, will not return False but will raise an error instead.

        """
        if self.sender is not None and self.passwd is not None and self.smtp is not None:
            if MailSender.hostname is None:
                if self.do_raise:
                    raise ValueError("You must specify the histname attribute of MailSender (like "
                                     "outlook.office365.com for example)")
                MailSender.log("You must specify the histname attribute of MailSender (like outlook.office365.com for "
                               "example)", "error")
                return False

            try:
                self.smtp = smtplib.SMTP(MailSender.hostname, port=587)
                self.smtp.connect(MailSender.hostname, 587)
                self.smtp.starttls()
                self.smtp.login(self.sender, self.passwd)
            except Exception as e:
                if self.do_raise:
                    raise e
                MailSender.log(e, "error")
                return False
            return True
        else:
            if self.sender is None:
                self.sender = input("Account mail or username:\r\n")

            if "@" not in self.sender:
                self.sender += f"@{MailSender.default_mail}"
            attempt = 0
            while not self.sender.endswith(f"{MailSender.default_mail}") and attempt < 3:
                attempt += 1
                if attempt == 3:
                    if self.do_raise:
                        raise ConnectionFailed
                    return False
                MailSender.log("The address you specified is not a valid Advestis email", "error")
                self.sender = input("email adress:\r\n")

            if self.passwd is None:
                self.passwd = getpass.getpass("Password:\r\n")

            self.smtp = None
            logged_in = False
            # Set up server
            try:
                self.smtp = smtplib.SMTP(MailSender.hostname, port=587)
                self.smtp.connect(MailSender.hostname, 587)
                self.smtp.starttls()
            except Exception as e:
                if self.do_raise:
                    raise e
                MailSender.log(e, "error")
                return False
            # login to server
            attempt = 0
            while attempt < 3 and not logged_in:
                try:
                    self.smtp.login(self.sender, self.passwd)
                    logged_in = True
                except Exception as e:
                    attempt += 1
                    if attempt == 3:
                        if self.do_raise:
                            raise ConnectionFailed
                        return False
                    MailSender.log(e, "error")
                    MailSender.log("Identificatin failed. Try again!", "error")
                    self.sender = input("email adress or username:\r\n")
                    if "@" not in self.sender:
                        self.sender += f"@{MailSender.default_mail}"
                    sub_attempt = 0
                    while not self.sender.endswith(f"{MailSender.default_mail}") and sub_attempt < 3:
                        sub_attempt += 1
                        if sub_attempt == 3:
                            if self.do_raise:
                                raise ConnectionFailed
                            return False
                        MailSender.log("The adress you specified is not a valid Advestis email", "error")
                        self.sender = input("email adress:\r\n")
                    self.passwd = getpass.getpass("Password:\r\n")
        return True

    def test_mail_server(self) -> bool:
        """Tests the connection
        Calls, self.set_mail_server, so will prompt for username and passwd
        if they are not known.

        Returns
        -------
        bool
            True if connection successful, False otherwise. If self.do_raise is
            True, will not return False but will raise an error instead.

        """
        logged_in = self.set_mail_server()
        if not logged_in or self.smtp is None:
            return False

        print("Connection successful!\n")
        # noinspection PyBroadException
        try:
            self.smtp.quit()
        except Exception:
            MailSender.log(QUIT_ERROR, "debug")
        return True

    # noinspection PyUnresolvedReferences
    def send_mail(
        self,
        adresses: Union[str, List],
        subject: str,
        text: str = "",
        files: List[Union["TransparentPath", Path, str]] = None,
    ) -> bool:
        """Send a mail to a list of recepients. Can include files.

        Parameters
        ----------
        adresses: Union[str, List]
            One recipient or a list of recipient

        subject: str
            The mail subject

        text: str
            The mail main body

        files: List[Union[TransparentPath, Path, str]]
            The paths to the attachment to join to the mail

        Returns
        -------
        bool
            True if mail was sent to at least one recipient, else False

        """

        if files is None:
            files = []
        if not isinstance(adresses, list):
            adresses = [adresses]

        # server connection can be already opened. In any case, close it
        # and reopen it.
        # noinspection PyBroadException
        try:
            self.smtp.quit()
        except Exception:
            MailSender.log(QUIT_ERROR, "debug")

        if not self.set_mail_server():
            return False

        message = MIMEMultipart()
        message["From"] = self.sender
        message["Date"] = formatdate(localtime=True)
        message["To"] = ", ".join(adresses)
        message["Subject"] = subject
        message.attach(MIMEText(f"{text}.\n\n   Sent by AdUtils' MailSender."))

        # Attach files if any
        for filepath in files:
            with open(filepath, "rb") as fil:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(fil.read())
                encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{filepath.name}"')
            message.attach(part)

        refused = self.smtp.sendmail(self.sender, adresses, message.as_string())
        accepted = [item for item in adresses if item not in refused]

        print("Mail successfully sent to:")

        if len(accepted) == 0:
            print("No one!")
            return False
        else:
            for item in accepted:
                print(item)

        if len(refused) > 0:
            MailSender.log("  Mail failed to be sent to:", "error")
            for item in refused:
                MailSender.log(f"{item} because {refused[item]}", "error")
        # noinspection PyBroadException
        try:
            self.smtp.quit()
        except Exception:
            MailSender.log(QUIT_ERROR, "debug")
        return True

    @classmethod
    def log(cls, message, type_):
        if cls.logger is None:
            if type_ == "error" or type_ == "critical":
                if isinstance(message, BaseException):
                    raise message
                else:
                    raise ValueError(message)
            elif type_ == "warning":
                warnings.warn(message)
            else:
                print(message)
        else:
            getattr(cls.logger, type_)(message)
