import datetime
from abc import ABC
from typing import Optional, List

from lgt.common.python.lgt_logging import log
from lgt.common.python.slack_client.web_client import SlackWebClient, SlackMessageConvertService, get_slack_credentials
from lgt_data.model import SlackHistoryMessageModel, UserLeadModel, UserModel, UserBotCredentialsModel
from lgt_data.mongo_repository import UserLeadMongoRepository, UserMongoRepository, \
    UserBotCredentialsMongoRepository
from pydantic import BaseModel

from ..runner import BackgroundJobRunner
from ..basejobs import BaseBackgroundJob, BaseBackgroundJobData
from ..smtp import SendMailJobData, SendMailJob
from ..env import portal_url

"""
Load slack chat history
"""
class LoadChatHistoryJobData(BaseBackgroundJobData, BaseModel):
    user_id: str
    days_ago: Optional[int] = 10

class LoadChatHistoryJob(BaseBackgroundJob, ABC):
    @staticmethod
    def _merge_chat_histories(saved_chat, current_chat):
        for message in current_chat:
            same_message = [msg for msg in saved_chat if msg.ts == message.ts]
            if same_message:
                message.text = same_message[0].text
            else:
                saved_chat.append(message)

        return saved_chat

    @staticmethod
    def _update_history(user_bots: List[UserBotCredentialsModel], user: UserModel, lead: UserLeadModel) -> Optional[SlackHistoryMessageModel]:
        saved_chat_history = lead.chat_history if lead.chat_history else list()

        creds = get_slack_credentials(user,
                                      lead,
                                      update_expired=False,
                                      user_bots=user_bots)
        if not creds or creds.invalid_creds:
            return None

        slack_client = SlackWebClient(creds.token, creds.cookies)
        history = slack_client.chat_history(lead.slack_channel)

        if not history['ok']:
            log.error(
                f'Failed to fetch chat history for the lead: {lead.id} | {user.email} | {creds}. ERROR: {history.get("error", "")}')
            return None

        messages = [SlackMessageConvertService.from_slack_response(user.email, "slack_files", creds.token, m) for m in history.get('messages', [])]
        messages = sorted(messages, key=lambda x: x.created_at)
        messages = LoadChatHistoryJob._merge_chat_histories(saved_chat=list(saved_chat_history), current_chat=messages)
        chat_history = [message.to_dic() for message in messages]
        UserLeadMongoRepository().update_lead(lead.user_id, lead.id, chat_history=chat_history)

        return messages[-1] if messages else None

    @staticmethod
    def _notify_about_new_messages(user: UserModel, lead: UserLeadModel):
        if not lead:
            return

        with open('lgt_jobs/templates/new_message_mail_template.html', mode='r') as template_file:
            html = template_file.read()
            html = html.replace("{sender}", lead.message.profile.get_name())
            html = html.replace("{view_message_link}", f'{portal_url}/')

            message_data = {
                "html": html,
                "subject": 'New message(s) on LEADGURU',
                "recipient": user.email
            }

            BackgroundJobRunner.submit(SendMailJob, SendMailJobData(**message_data))

    @property
    def job_data_type(self) -> type:
        return LoadChatHistoryJobData

    def exec(self, data: LoadChatHistoryJobData):
        user = UserMongoRepository().get(data.user_id)
        today = datetime.datetime.utcnow()
        delta = datetime.timedelta(days=data.days_ago)
        leads: List[UserLeadModel] = UserLeadMongoRepository().get_leads(user_id=data.user_id, skip=0, limit=100, from_date=today - delta)
        log.info(f"[LoadChatHistoryJob]: processing {len(leads)} for user: {user.email}")

        if not leads:
            return

        user_bots = UserBotCredentialsMongoRepository().get_bot_credentials(user_id=data.user_id)
        last_message = None
        last_message_lead = None
        for lead in leads:
            if not lead.slack_channel:
                continue

            message = LoadChatHistoryJob._update_history(user_bots=user_bots, user=user, lead=lead)

            if not message:
                continue

            if not last_message:
                last_message = message
                last_message_lead = lead

            if message.created_at > last_message.created_at and message.user == lead.message.sender_id:
                last_message = message
                last_message_lead = lead

                if lead.last_action_at < last_message.created_at:
                    lead.last_action_at = last_message.created_at
                    UserLeadMongoRepository().update_lead(lead.user_id, lead.id, last_action_at=last_message.created_at)

        has_to_be_notified = not user.new_message_notified_at \
                             or (last_message and last_message.created_at > user.new_message_notified_at)

        if last_message and has_to_be_notified and last_message.user == last_message_lead.message.sender_id:
            LoadChatHistoryJob._notify_about_new_messages(user, last_message_lead)
            UserMongoRepository().set(data.user_id, new_message_notified_at=datetime.datetime.utcnow())
