from typing import Optional, List


class Mailable:
    def __init__(self,
                 subject: str,
                 to_addr: List[str],
                 cc: Optional[List[str]] = None,
                 bcc: Optional[List[str]] = None,
                 from_addr: Optional[str] = None,
                 from_name: Optional[str] = None,
                 reply_to: Optional[str] = None,
                 plain: str = None,
                 html: str = None,
                 attachments: list = None):
        self.subject = subject
        self.to_addr = to_addr
        self.from_addr = from_addr
        self.from_name = from_name
        self.cc = cc
        self.bcc = bcc
        self.reply_to = reply_to
        self.plain = plain
        self.html = html
        self.attachments = attachments
