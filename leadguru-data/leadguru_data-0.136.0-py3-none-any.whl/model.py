import copy
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List

from bson import ObjectId


class BaseModel(ABC):
    def __init__(self):
        self.id = None
        self.created_at = datetime.utcnow()

    @classmethod
    def from_dic(cls, dic: dict):
        if not dic:
            return None

        model = cls()
        for k, v in dic.items():
            setattr(model, k, v)

        if '_id' in dic:
            setattr(model, 'id', dic['_id'])

        return model

    def to_dic(self):
        result = copy.deepcopy(self.__dict__)
        return result


class BaseBotModel(BaseModel):
    pass

    def __init__(self):
        super().__init__()

        self.type = None
        self.country = None
        self.created_by = None
        self.user_name = None
        self.name = None
        self.password = None
        self.token = None
        self.cookies = None
        self.slack_url = None
        self.registration_link = None
        self.channels = None
        self.connected_channels = None
        self.invalid_creds = False
        self.channels_users = None
        self.users_count = None
        self.messages_received: int = 0
        self.messages_filtered: int = 0

    @abstractmethod
    def is_dedicated(self):
        pass


class BotModel(BaseBotModel):
    pass

    def __init__(self):
        super().__init__()

    def is_dedicated(self):
        return False


class DedicatedBotModel(BaseBotModel):
    pass

    def __init__(self):
        super().__init__()
        self.user_id: Optional[str] = None
        self.updated_at: Optional[datetime] = datetime.utcnow()

    def is_dedicated(self):
        return True


class LeadProfileModel(BaseModel):
    pass

    def __init__(self):
        super().__init__()
        self.display_name = None
        self.real_name = None
        self.email = None
        self.phone = None
        self.title = None
        self.skype = None
        self.images = None

    def get_name(self):
        if self.real_name and self.real_name != '':
            return self.real_name

        if self.display_name and self.display_name != '':
            return self.display_name

        return None

    def get_short_name(self):
        full_name = self.get_name()
        if not full_name:
            return None

        if full_name.strip() == '':
            return None

        name_parts = [name_part for name_part in full_name.split(' ') if name_part.strip() != '']
        return name_parts[0] + ' ' + name_parts[-1][0] + '.' if len(name_parts) > 1 else name_parts[0]


class MessageModel(BaseModel):
    pass

    def __init__(self):
        super().__init__()
        self.message_id = None
        self.channel_id = None
        self.message = None
        self.name = None
        self.sender_id = None
        self.source = None
        self.slack_options = None
        self.dedicated_slack_options = None
        self.profile = None
        self.companies: List[str] = list()
        self.technologies: List[str] = list()
        self.locations: List[str] = list()

    @classmethod
    def from_dic(cls, dic: dict):
        if not dic:
            return None

        model: MessageModel = cls()
        for k, v in dic.items():
            setattr(model, k, v)

        if dic.get('profile', None):
            model.profile = LeadProfileModel.from_dic(dic['profile'])

        return model

    def to_dic(self):
        result = copy.deepcopy(self.__dict__)

        if result.get('profile', None):
            result['profile'] = result.get('profile').__dict__

        return result


class UserModel(BaseModel):
    pass

    def __init__(self):
        super().__init__()
        self.email: Optional[str] = None
        self.password: Optional[str] = None
        self.roles: List[str] = []
        self.user_name: str = ''
        self.company: str = ''
        self.position: str = ''
        self.new_message_notified_at: Optional[datetime] = None
        self.photo_url: str = ''
        self.slack_profile = SlackProfile()
        self.leads_limit: Optional[int] = None
        self.leads_proceeded: Optional[int] = None
        self.leads_filtered: Optional[int] = None
        self.leads_limit_updated_at: Optional[int] = None
        self.excluded_channels: Optional[Dict[str, List[str]]] = None

    @classmethod
    def from_dic(cls, dic: dict):
        if not dic:
            return None

        model: UserModel = cls()
        for k, v in dic.items():
            setattr(model, k, v)

        if '_id' in dic:
            setattr(model, 'id', dic['_id'])

        if dic.get('slack_profile', None):
            model.slack_profile = SlackProfile.from_dic(dic['slack_profile'])

        return model

    def to_dic(self):
        result = copy.deepcopy(self.__dict__)

        if result.get('slack_profile', None):
            result['slack_profile'] = result.get('slack_profile').__dict__

        return result


class UserBotCredentialsModel(BaseModel):
    pass

    def __init__(self):
        super().__init__()
        self.user_name = None
        self.password = None
        self.bot_name = None
        self.slack_url = None
        self.token = None
        self.user_id = None
        self.cookies = []
        self.invalid_creds = False
        self.updated_at: datetime = datetime.utcnow()
        self.slack_profile: Optional[SlackProfile] = None

    @classmethod
    def from_dic(cls, dic: dict):
        if not dic:
            return None

        model = cls()
        for k, v in dic.items():
            setattr(model, k, v)

        if 'name' in dic:
            setattr(model, 'id', dic['name'])

        if 'cookies' in dic:
            setattr(model, 'cookies', dic['cookies'])

        if 'invalid_creds' in dic:
            setattr(model, 'invalid_creds', dic['invalid_creds'])

        if 'slack_profile' in dic:
            setattr(model, 'slack_profile', SlackProfile.from_dic(dic['slack_profile']))

        return model


class UserResetPasswordModel(BaseModel):
    pass

    def __init__(self):
        super().__init__()
        self.email = None


class UserLeadStatusModel(BaseModel):
    pass

    def __init__(self):
        super().__init__()
        self.name = None
        self.order = 0
        self.user_id = None


class AuthorAttributesModel(BaseModel):
    pass

    def __init__(self):
        super().__init__()
        self.sender_id = None
        self.notes = None


class LeadModel(BaseModel):
    pass

    def __init__(self):
        super().__init__()
        self.message_id = ''
        self.url = ''
        self.status = ''
        self.notes = ''
        self.archived = False
        self.label = None
        self.slack_channel = None
        self.message = None
        self.tags = []
        self.group_tags = []
        self.label = None
        self.hidden = False
        self.followup_date = None
        self.score = 0
        self.board_id = None
        self.linkedin_urls = []
        self.likes = 0
        self.reactions = 0
        self.replies = []
        self.last_action_at: Optional[datetime] = None

    def is_dedicated_lead(self) -> bool:
        return self.message and \
               hasattr(self.message, "dedicated_slack_options") and \
               self.message.dedicated_slack_options

    def get_dedicated_credentials(self) -> Optional[dict]:
        return self.message.dedicated_slack_options

    @classmethod
    def from_dic(cls, dic: dict):
        if not dic:
            return None

        model = LeadModel()
        for k, v in dic.items():
            setattr(model, k, v)

        model.message = MessageModel.from_dic(dic['message'])
        model.message.profile = LeadProfileModel.from_dic(dic['message'].get('profile', None))

        if not model.last_action_at:
            model.last_action_at = model.created_at

        return model

    def to_dic(self):
        result = copy.deepcopy(self.__dict__)
        result["message"] = self.message.to_dic()
        result['archived'] = self.archived

        return result


class SlackHistoryMessageModel:
    text: str
    created_at: datetime
    user: str
    type: str
    ts: str

    class SlackFileModel:
        def __init__(self):
            self.id = None
            self.name = None
            self.title = None
            self.filetype = None
            self.size = 0
            self.mimetype = None
            self.download_url = None

        def to_dic(self):
            result = copy.deepcopy(self.__dict__)
            return result

    def __init__(self):
        self.text: str = ''
        self.created_at: datetime
        self.user = ''
        self.type = ''
        self.ts = ''
        self.files = []

    def to_dic(self):
        result = copy.deepcopy(self.__dict__)
        if self.files and 'files' in result:
            result['files'] = [x.to_dic() if isinstance(x, SlackHistoryMessageModel.SlackFileModel) else x
                               for x in self.files]

        return result

    @classmethod
    def from_dic(cls, dic: dict):
        if not dic:
            return None
        model = cls()
        for k, v in dic.items():
            setattr(model, k, v)
        return model


class UserLeadModel(LeadModel):
    pass

    def __init__(self):
        super().__init__()
        self.order: int = 0
        self.followup_date = None
        self.user_id = None
        self.chat_viewed_at = None
        self.chat_history = [SlackHistoryMessageModel]
        self.board_id = None
        self.contacts: UserLeadContacts = None

    @classmethod
    def from_dic(cls, dic: dict):
        if not dic:
            return None

        result = LeadModel.from_dic(dic)
        result.contacts = UserLeadContacts().from_dic(dic.get('contacts', None))
        result.chat_history = list(map(lambda x: SlackHistoryMessageModel.from_dic(x), dic.get('chat_history', None))) \
            if dic.get('chat_history', None) else []
        result.chat_viewed_at = dic.get('chat_viewed_at', None)

        result.chat_history = sorted(result.chat_history, key=lambda x: x.created_at)
        return result

    @staticmethod
    def from_route(lead: LeadModel):
        model_dict = lead.to_dic()
        result = UserLeadModel.from_dic(model_dict)
        result.order = 0

        result.message = MessageModel.from_dic(model_dict['message'])
        result.message_id = result.message.message_id
        result.message.profile = LeadProfileModel.from_dic(model_dict['message'].get('profile', None))
        result.chat_history = []
        result.chat_viewed_at = None
        result.contacts = None
        return result


class UserLeadContacts:
    email: str

    @classmethod
    def from_dic(cls, dic: dict):
        if not dic:
            return None

        model = cls()
        for k, v in dic.items():
            setattr(model, k, v)

        return model

    def to_dic(self):
        return copy.deepcopy(self.__dict__)


class BoardModel(BaseModel):
    pass

    def __init__(self):
        super().__init__()
        self.name = None
        self.user_id = None
        self.statuses = list()
        self.is_primary = None

    @classmethod
    def from_dic(cls, dic: dict):
        if not dic:
            return None

        model = BoardModel()
        for k, v in dic.items():
            setattr(model, k, v)

        if '_id' in dic:
            setattr(model, 'id', dic['_id'])

        if 'statuses' in dic:
            model.statuses = [BoardedStatus.from_dic(status) for status in dic['statuses']]

        return model

    def to_dic(self):
        result = copy.deepcopy(self.__dict__)
        result["statuses"] = [BoardedStatus.to_dic(status) for status in self.statuses]

        for status in result['statuses']:
            status['board_id'] = result['id']

        return result


class BoardedStatus:
    pass

    def __init__(self):
        self.id = None
        self.name = None
        self.order = 0

    def to_dic(self):
        self.id = self.name
        return copy.deepcopy(self.__dict__)

    @classmethod
    def from_dic(cls, dic: dict):
        if not dic:
            return None
        model = cls()
        for k, v in dic.items():
            setattr(model, k, v)
        return model


class SlackProfile:
    pass

    def __init__(self):
        self.title = ''
        self.phone = ''
        self.skype = ''
        self.display_name = ''
        self.real_name = ''
        self.email = ''

    def to_dic(self):
        return copy.deepcopy(self.__dict__)

    @classmethod
    def from_dic(cls, dic: dict):
        if not dic:
            return None
        model = cls()
        for k, v in dic.items():
            setattr(model, k, v)
        return model


class Contact(SlackProfile):
    pass

    def __init__(self):
        super().__init__()
        self.slack_url = ''
        self.linkedin_url = ''
        self.type = ''


class SlackUserPresenceModel(BaseModel):
    user: str
    status: str
    updated_at: datetime
    bot_name: Optional[str]
    bot_id: Optional[ObjectId]


class SlackMemberInformation(BaseModel, SlackProfile):
    workspace: str
    user: str
    images: dict
    full_text: str
    deleted: bool = False
    is_bot: bool = False
    is_app_user: bool = False
    is_admin: bool = False
    is_owner: bool = False
    is_email_confirmed: bool = False
