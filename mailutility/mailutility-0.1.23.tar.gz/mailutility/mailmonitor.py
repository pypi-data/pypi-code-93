# -*- coding:utf-8 -*-
import imaplib
import email
import getpass
import chardet
import sys
import traceback
import socket
import atexit
import warnings

from time import sleep, time
from pathlib import Path
from typing import Union, List
from datetime import datetime
import threading


class MailException(Exception):
    """ Any kind of mail error """

    def __init__(self, msg: str = None):
        self.message = msg or "There is a problem with the mails..."
        super().__init__(self.message)

    def __str__(self):
        return self.message


def get_datetime_now(fmt: str = "%d%m%Y %H:%M:%S") -> str:
    """

    Parameters
    ----------
    fmt: str
         The date format to use (Default value = "%d%m%Y %H:%M:%S")

    Returns
    -------
    str

    """

    date = datetime.now()
    return date.strftime(fmt)


# noinspection PyBroadException, PyUnresolvedReferences
def persist_file(filepath: "TransparentPath", part) -> None:
    """

    Parameters
    ----------
    filepath: TransparentPath

    part:


    Returns
    -------
    None

    """
    data = part.get_payload(decode=True)
    filepath.write_bytes(data)
    print(f"SAVING FILE to : {filepath}.")


# noinspection PyUnresolvedReferences
def rename_file(
    filename, to_path: Union[str, Path, "TransparentPath"], overwrite: bool = True
) -> Union[Path, "TransparentPath"]:
    """

    Parameters
    ----------
    filename: str

    to_path: Union[str, Path, "TransparentPath"]

    overwrite: bool
        If True, will overwrite any file with the same name. Else rename it
        appending to now's datetime.


    Returns
    -------
    Union[str, Path, "TransparentPath"]

    """
    date_ref = datetime.today()

    try:
        filepath = to_path / filename
    except TypeError:
        to_path = Path(to_path)
        filepath = to_path / filename
    ext = filepath.suffix
    if filepath.is_file() and overwrite is False:
        filepath = type(to_path)(f"{to_path / filepath.stem}_{date_ref}{ext}")
    return filepath


# noinspection PyUnresolvedReferences
def save_attachment(part, to_path: Union["TransparentPath", Path, str], overwrite: bool = True) -> None:
    """

    Parameters
    ----------
    part:

    to_path: Union[TransparentPath, Path, str]
        The directory to save the file in

    overwrite: bool
        If True, will overwrite any file with the same name. Else rename it
        appending to now's datetime.


    Returns
    -------
    None

    """
    if part.get("Content-Disposition") is None:
        return

    if part.get_content_maintype() != "multipart":
        name = part.get_filename()
        if not name:
            raise ValueError(f"No file name in part {part}!")
        name = name.replace("\r", "").replace("\n", "")
        filepath = rename_file(name, to_path, overwrite)
        persist_file(filepath, part)


def split_spec_char(s):
    trimmed_s = s.encode("ascii", errors="ignore").decode("ascii")
    spec_chars = set([c for c in s if c not in trimmed_s])
    out = [""]
    for c in s:
        if c not in spec_chars:
            out[-1] += c
        else:
            out.append("")
    return [o for o in out if o != ""]


class MailMonitor(object):
    """Class allowing to monitor a mailbox to save attachments to a
    directory using conditions on sender and subjet.

    If two-factor auth is activated, you will need to
    provide  an app password instead of your regular password. If you do not
    have one or do not remember it, make a new one by following the
    instructions here (only valid for office365 acconuts):
    https://docs.microsoft.com/fr-fr/azure/active-directory/user-help/
    multi-factor-authentication-end-user-app-passwords

    The relevant security page to set the app passwords :
    https://account.activedirectory.windowsazure.com/Proofup.aspx

    MailMonitor will use threading to allow for the monitoring of
    different conditions and saving to different paths.

    For a basic usage (monitoring one set of conditions and saving to one
    location) :

    >>> from mailutility import MailMonitor  # doctest: +SKIP
    >>> mail = MailMonitor("username")  # doctest: +SKIP
    >>> mail.monitor(  # doctest: +SKIP
    >>>     conditions={"subject": "test",  # doctest: +SKIP
    >>>                 "sender": "cottephi@gmail.com"},  # doctest: +SKIP
    >>>     to_path="/home/username/Bureau",  # doctest: +SKIP
    >>>     time_to_sleep=5  # doctest: +SKIP
    >>> )  # doctest: +SKIP

    To monitor several sources and save to different paths, use :

    >>> mail.monitor(  # doctest: +SKIP
    >>>     conditions=[{"sender": "a@b.c", "subject": "g"}, {"sender": "d@e.f", "subject": "h"}],  # doctest: +SKIP
    >>>     to_path=["/home/username/Desktop", "/home/username/Documents"],  # doctest: +SKIP
    >>>     time_to_sleep=5,  # doctest: +SKIP
    >>> )

    You can decide to save to GCS by using TransparentPath:

    >>> # noinspection PyShadowingNames, PyUnresolvedReferences
    >>> from transparentpath import TransparentPath as Path  # doctest: +SKIP
    >>> Path.set_global_fs("gcs", bucket="my_bucket", project="my_project")  # doctest: +SKIP
    >>> mail = MailMonitor("tomonitor@mailbox.com")  # doctest: +SKIP
    >>> mail.monitor(  # doctest: +SKIP
    >>>     conditions={"subject": "test",  # doctest: +SKIP
    >>>                 "sender": "chient@chat.com"},  # doctest: +SKIP
    >>>     to_path=Path("attachment"),   # doctest: +SKIP
    >>>     time_to_sleep=5  # doctest: +SKIP
    >>> )  # doctest: +SKIP

    If conditions is an empty dict, will save attachments of all incoming
    mails.

    Any email triggering the monitor will be marked as SEEN.

    Notes and warnings:

        1. Even though multiprocessing is used, any code written after the
        call to mail.monitor will not be executed until the monitoring ends.

        2. The file saving system tends to see mail signature as attachments,
        you will have to delete the files yourself, or ignore them in your
        analysis.
    """

    accepted_conditions = ["sender", "subject", "subject_exact"]
    instances = []
    default_mail = ""
    logger = None

    def __init__(
            self,
            username: str = None,
            token: str = None,
            port: int = 993,
            hostname: str = "outlook.office365.com",
            connect: bool = False,
            overwrite: bool = True,
    ):

        if username is None:
            username = input("User name:\n")
        if token is None:
            token = getpass.getpass(f"Password for {username}:")
        if "@" not in username:
            username = f"{username}@{MailMonitor.default_mail}"

        self.username = username
        self.token = token
        self.port = port
        self.hostname = hostname
        self.mailbox = None
        self.exit = False
        self.overwrite = overwrite
        if connect:
            self.open_connection()
        MailMonitor.instances.append(self)

    def open_connection(self):
        """ """
        # Connection to the server
        talk = False
        if self.mailbox is None:
            print(f"Connecting to {self.hostname} as {self.username}...")
            talk = True
        attempts = 0
        while True:
            attempts += 1
            try:
                self.mailbox = imaplib.IMAP4_SSL(self.hostname, self.port)
                # Login to your account
                self.mailbox.login(self.username, self.token)
                self.mailbox.select()
                if talk:
                    print("...successful")
                break
            except socket.gaierror as e:
                print(f"Failed more than {attempts} times. Raising the exception.")
                if attempts > 60:
                    raise e
                else:
                    print(f"Failed. Retrying for the {attempts}th time...")
                    sleep(1)

    @staticmethod
    def configure_date(date: Union[str, datetime]) -> str:
        """
        Converts datetime format to mail date format

        > https://datatracker.ietf.org/doc/html/rfc3501 page 84/85

        Parameters
        ----------
        date : Union[str, datetime]
            date to convert

        Returns
        -------
        str
            converted date
        """
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d")
        m_dict = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun", "07": "Jul",
                  "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"}
        if len(str(date.month)) == 1:
            m = "0" + str(date.month)
        else:
            m = str(date.month)
        mv = m_dict[m]
        return str(date.day) + "-" + mv + "-" + str(date.year)

    @staticmethod
    def read_date(date: str) -> datetime.date:
        """
        convert date from mail format for datetime

        > https://datatracker.ietf.org/doc/html/rfc3501 page 84/85

        Parameters
        ----------
        date : str
            mail format

        Returns
        -------
        datetime.date
        """
        m_dict = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun", "07": "Jul",
                  "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"}
        day = date[:2]
        m_dict = {i: j for i, j in zip(m_dict.values(), m_dict.keys())}
        month = m_dict[date[3:6]]
        year = date[7:11]
        date = datetime.strptime(year + "-" + month + "-" + day, "%Y-%m-%d")
        return date.date()

    def monitor(
            self,
            conditions: Union[dict, List[dict]],
            to_path: Union[Union["TransparentPath", Path, str], List[Union["TransparentPath", Path, str]]],
            time_to_sleep: Union[int, List[int]] = 60,
            mailbox: Union[str, List[str]] = "INBOX",
            overwrite: Union[bool, List[bool]] = None,
            timeout: int = None,
    ) -> None:
        """

        Parameters
        ----------
        conditions: Union[dict, List[dict]]
            The list of patterns to match for the mail to trigger. The keys
            for the dicts are:

                1: subject : a substring that must be containd in the email
                subject.

                2: subject_exact : the exact expected subject.

                3: sender : the sender email adress.

        to_path: Union[Union[TransparentPath, Path, str], List[Union[TransparentPath, Path, str]]]
            Where to save the attatchment. If is not a list, will use the
            same path for all monitoring conditions.

        time_to_sleep: Union[int, List[int]]
            The time between two mailbox checks (Default value = 60). If is
            not a list, will use the same time for all monitoring conditions.

        mailbox: Union[str, List[str]]
            The mailbox to check. If is not a list, will use the same
            mailbox for all monitoring conditions. (Default value = "INBOX")

        overwrite: Union[bool, List[bool]]
            If True, will overwrite any file with the same name. Else rename it
            appending to now's datetime. (Default value = self.overwrite)

        timeout: int
            Time in seconds the monitor must remain up. None for infinite time (Default value = None)

        Returns
        -------
        None

        """

        if overwrite is None:
            overwrite = self.overwrite

        if not isinstance(conditions, list):
            conditions = [conditions]
        if not isinstance(to_path, list):
            to_path = [to_path] * len(conditions)
        if not isinstance(time_to_sleep, list):
            time_to_sleep = [time_to_sleep] * len(conditions)
        if not isinstance(mailbox, list):
            mailbox = [mailbox] * len(conditions)
        if not isinstance(overwrite, list):
            overwrite = [overwrite] * len(conditions)

        if not len(conditions) == len(to_path):
            raise ValueError("to_path and conditions must have same length")
        if not len(conditions) == len(time_to_sleep):
            raise ValueError("time_to_sleep and conditions must have same length")
        if not len(conditions) == len(mailbox):
            raise ValueError("mailbox and conditions must have same length")
        theargs = []
        for i in range(len(conditions)):
            theargs.append((self, conditions[i], to_path[i], time_to_sleep[i], mailbox[i], overwrite[i], timeout))

        print("Will start monitoring for new emails. You can stop the monitoring at any moment by pressing 'CTRL+C'.")
        if timeout is not None:
            print(f"Monitoring will remain up for {timeout} seconds then will shut down.")
        for arg in theargs:
            threading.Thread(target=MailMonitor._monitor, args=arg).start()

    # noinspection PyUnresolvedReferences
    def fetch_one_mail(self,
                       mode: str,
                       save_dir: Union[str, Path],
                       state: str = "ALL",
                       subject: str = None,
                       sender: str = None,
                       body: str = None,
                       date: Union[str, datetime, None] = None,
                       mailbox: Union[str, List[str]] = "INBOX",
                       ) -> Union[bool, tuple]:
        """

        Will fetch to attachments of a mail based on the date on arrival and the select mode

        Parameters
        ----------
        subject : str

        sender : str

        state : str (SEEN, UNSEEN, ALL)

        date : Union[str, datetime]

        mode : str (last, next, nearest, exact)

        to_path : Union[Union["TransparentPath", Path, str], List[Union["TransparentPath", Path, str]]]

        mailbox : Union[str, List[str]] = "INBOX"

        overwrite : Union[bool, List[bool]] = None


        Returns
        -------
        Union[bool, tuple]
            True and mail date if successful else False
        """
        self.open_connection()
        self.mailbox.select(mailbox)
        base_req = ""
        if subject is not None:
            for i in split_spec_char(subject):
                base_req += f'SUBJECT "{i}" '
        if sender is not None:
            base_req += f"FROM {sender} "
        if body is not None:
            base_req += f"BODY {body} "
        if state != "ALL":
            base_req += f"({state})"
        if date is None:
            base_req += f"ON {self.configure_date(datetime.now())}"
        elif mode == "last":
            base_req += f"BEFORE {self.configure_date(date)}"
        elif mode == "next":
            base_req += f"SINCE {self.configure_date(date)}"
        elif mode == "on":
            base_req += f"ON {self.configure_date(date)}"
        uids = self.mailbox.uid("SEARCH", None, base_req)[1]
        uids = list(map(lambda x: str(x)[2:-1], uids))
        uids = uids[0].split(" ")
        if uids[0] == '':
            return False
        dict_date = self.list_dates(uids, invert=True)
        dates = list(dict_date.keys())
        if date is None:
            date = datetime.now().date()
        elif isinstance(date, str):
            date = datetime.strptime(date,"%Y-%m-%d").date()
        if mode == "exact":
            uid = dict_date.get(date, None)
            if uid is None:
                return False
            uid = uid[0]
        # TODO (Aducourthial): add time sensitivity
        elif mode == "next":
            uid = dict_date[(lambda x, y: min(x, key=lambda i: abs(i - y) if i < y else np.inf))(dates, date)][0]
        elif mode == "last":
            uid = dict_date[(lambda x, y: min(x, key=lambda i: abs(i - y) if i > y else np.inf))(dates, date)][0]
        elif mode == "nearest":
            uid = dict_date[(lambda x, y: min(x, key=lambda i: abs(i - y)))(dates, date)][0]
        else:
            return False
        bp = Path(save_dir)
        if not bp.exists():
            bp.mkdir()
        for i, j in self.fetch_attachment(uid).items():
            (bp / i).write_bytes(j)
        return True, self.list_dates([uid])[uid]

    def fetch_attachment(self, uid: str) -> dict:
        """
        will fetch attachments for one mail

        Parameters
        ----------
        uid: str
            uid of mail

        Returns
        -------
        dict of file name : data as bytes
        """
        ret = {}
        for part in email.message_from_string(
                self.mailbox.uid("FETCH", uid, "(BODY.PEEK[])")[1][0][1].decode("ascii")).walk():
            if part.get_content_maintype() != "multipart":
                name = part.get_filename()
                if name:
                    name = name.replace("\r", "").replace("\n", "")
                    data = part.get_payload(decode=True)
                    ret[name] = data
        return ret

    def list_dates(self, uids: list, invert: bool = False):
        """
        fetch intenal dates of list of uid
        base > {uid : date}
        inverted > {date : uids}

        Parameters
        ----------
        uids: list
        invert : bool
                invert dict

        Returns
        -------
        dict
        """
        ret = {}
        for uid in uids:
            msg = self.mailbox.uid("FETCH", uid, "INTERNALDATE")
            ret[uid] = self.read_date(msg[1][0].decode().split('"')[-2][:11])
        if invert:
            bi = ret.copy()
            ret = {}
            for i, j in bi.items():
                if j not in ret.keys():
                    ret[j] = [i]
                else:
                    ret[j].append(i)
        return ret

    def _monitor(
            self,
            conditions: dict,
            to_path: Union["TransparentPath", Path, str],
            time_to_sleep: int = 60,
            mailbox: str = "INBOX",
            overwrite: bool = None,
            timeout: int = None,
    ) -> None:
        """

        Parameters
        ----------
        conditions: dict
            The patterns to match for the mail to trigger. The keys are:

                1: subject : a substring that must be containd in the email
                subject.

                2: subject_exact : the exact expected subject.

                3: sender : the sender email adress.

        to_path: Union[TransparentPath, Path, str]

        time_to_sleep: int
             The time between two mailbox checks (Default value = 60)

        mailbox: str
             The mailbox to check (Default value = "INBOX")

        timeout: int
            Time in seconds the monitor must remain up. None for infinite time (Default value = None)

        Returns
        -------
        None

        """

        if overwrite is None:
            overwrite = self.overwrite

        s = (
            f"Checking {mailbox} of {self.username} each {time_to_sleep} "
            f"seconds for new emails matching the conditions:\n"
        )
        for condition in conditions:
            if condition not in MailMonitor.accepted_conditions:
                raise KeyError(f"Condition {condition} not valid")
            s += f"  - '{condition}' = {conditions[condition]}\n"
        s += f"Will save the attachment in {to_path}"
        print(s)

        def the_while(shelf: MailMonitor, t: int):
            t0 = time()
            while True:
                if shelf.exit:
                    break
                shelf.open_connection()
                shelf.mailbox.select(mailbox)
                cond = ""
                if "subject" in conditions:
                    matches = split_spec_char(conditions["subject"])
                    for m in matches:
                        cond = f'{cond}SUBJECT "{m}" '
                if "sender" in conditions:
                    cond = f'{cond}FROM "{conditions["sender"]}" '
                if len(cond) == 0:
                    raise ValueError("No filtering conditions specified")

                cond = f"{cond}(UNSEEN)"
                uids = shelf.mailbox.uid("SEARCH", None, cond)[1][0].split()
                for uid in uids:
                    try:
                        typ, msg_data = shelf.mailbox.uid("FETCH", uid, "(BODY.PEEK[])")
                    except ConnectionResetError:
                        break
                    if typ == "NO":
                        raise MailException(msg_data[0])
                    email_body = ""
                    if msg_data[0] is not None:
                        # noinspection PyUnresolvedReferences
                        email_body = msg_data[0][1]
                    else:
                        MailMonitor.log("Triggered on an empty mail?!", "warning")
                    encoding = chardet.detect(email_body)["encoding"]
                    email_body = email_body.decode(encoding)
                    mail = email.message_from_string(email_body)

                    print(
                        f"Triggered at {get_datetime_now()} on mail "
                        f"subject '{mail['Subject']}'"
                        f" from '{mail['From']}'"
                    )
                    for part in mail.walk():
                        save_attachment(part, to_path, overwrite)
                    _, _ = shelf.mailbox.uid("FETCH", uid, "(RFC822)")
                    print("Finished reading the mail")
                if not shelf.mailbox.state == "LOGOUT":
                    shelf.mailbox.select()
                    shelf.mailbox.close()
                    shelf.mailbox.logout()
                # Verification toutes les x secondes
                sleep(time_to_sleep)
                if t is not None and time() - t0 > t:
                    print(f"Requested run time of {t} completed. Exiting...")
                    break

        the_while(self, timeout)

    # noinspection PyUnresolvedReferences
    def send(self, msg):
        new_message = email.message.Message()
        new_message["From"] = f"{self.username}@{MailMonitor.default_mail}"
        new_message["Subject"] = "MailMonitoring ended with Exception"
        new_message.set_payload(msg)
        self.open_connection()
        self.mailbox.append(
            "INBOX", "", imaplib.Time2Internaldate(time()), str(new_message).encode(),
        )
        if not self.mailbox.state == "LOGOUT":
            self.mailbox.select()
            self.mailbox.close()
            self.mailbox.logout()
        print(f"Sent warning message to {self.username}@{MailMonitor.default_mail}")

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


_excepthook = getattr(sys, "excepthook")


# noinspection PyBroadException
@atexit.register
def clean():
    for mm in MailMonitor.instances:
        try:
            if mm.mailbox is not None and not mm.mailbox.state == "LOGOUT":
                mm.mailbox.select()
                mm.mailbox.close()
                mm.mailbox.logout()
        except Exception as e:
            MailMonitor.log("Failed to close the mailbox:", "warning")
            MailMonitor.log(e, "warning")
    del MailMonitor.instances


def overload_raise(ex, val, tb):
    if ex != KeyboardInterrupt:
        li = traceback.format_exception(ex, val, tb)
        to_send = "".join(li)
        for mm in MailMonitor.instances:
            mm.send(to_send)
        _excepthook(ex, val, tb)
    else:
        sys.exit(0)


setattr(sys, "excepthook", overload_raise)
