from typing import Union, Callable, Dict, Optional, List

from jinja2 import Template

DictVar = Dict[str, str]
DictVarOrFunc = Union[DictVar, Callable[[], DictVar]]

__all__ = []


def render(template: Optional[str] = None,
           template_file: Optional[str] = None,
           variables: Dict[str, str] = {}):
    tpl_str = ''
    if template is not None:
        tpl_str = template
    if template_file is not None:
        with open(template_file, 'r') as f:
            tpl_str = f.read()

    return Template(tpl_str).render(**variables)


try:
    from SNSNotifications.channels.mail import Mailable

    __all__ += ['MailableNotification']


    class MailableNotification:
        email_variables: DictVarOrFunc = {}

        @property
        def email_template(self) -> Optional[str]:
            return None

        @property
        def email_template_file(self) -> Optional[str]:
            return None

        @property
        def email_to_addr(self) -> List[str]:
            raise NotImplementedError()

        @property
        def email_subject(self) -> str:
            raise NotImplementedError()

        @property
        def attachments(self) -> Optional[list]:
            return None

        def to_mail(self):
            return Mailable(to_addr=self.email_to_addr,
                            subject=self.email_subject,
                            attachments=self.attachments,
                            html=render(self.email_template, self.email_template_file, self.email_variables))
except ImportError:
    pass

try:
    from SNSNotifications.channels.slack import SlackMessage

    __all__ += ['SlackableNotification']


    class SlackableNotification:
        slack_variables: DictVarOrFunc = {}

        @property
        def slack_channel(self) -> Optional[str]:
            return None

        @property
        def slack_template(self) -> Optional[str]:
            return None

        @property
        def slack_mentions(self) -> Optional[List[str]]:
            return None

        def to_slack(self):
            return SlackMessage(text=render(self.slack_template, None, self.slack_variables),
                                mentions=self.slack_mentions,
                                channel=self.slack_channel)
except ImportError:
    pass
