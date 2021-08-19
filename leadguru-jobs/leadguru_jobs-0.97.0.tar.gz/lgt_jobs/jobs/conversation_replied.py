from abc import ABC
from datetime import datetime, timedelta
from typing import Optional

from lgt.common.python.lgt_logging import log
from lgt.common.python.slack_client.slack_client import SlackClient
from lgt.common.python.slack_client.web_client import SlackWebClient, get_system_slack_credentials
from pydantic import BaseModel
from lgt_data.mongo_repository import LeadMongoRepository, BotMongoRepository, \
    UserLeadMongoRepository
from ..basejobs import BaseBackgroundJobData, BaseBackgroundJob

"""
Update messages conversations
"""


class ConversationRepliedJobData(BaseBackgroundJobData, BaseModel):
    message_id: str
    ts: str


class ConversationRepliedJob(BaseBackgroundJob, ABC):
    @property
    def job_data_type(self) -> type:
        return ConversationRepliedJobData

    def exec(self, data: ConversationRepliedJobData):
        bots = BotMongoRepository().get()
        lead = LeadMongoRepository().get_by_message_id(data.message_id)
        if not lead:
            return

        creds = get_system_slack_credentials(lead, bots)
        if not creds:
            log.warning(f"Lead: {lead.id}, bot credentials are not valid")
            return

        client = SlackClient(creds.token, creds.cookies)
        resp = client.conversations_replies(lead.message.channel_id, data.ts)
        if not resp["ok"]:
            return

        if not resp.get("messages"):
            return

        messages = [m["text"] for m in resp["messages"][1:]]
        set_dict = {
            "replies": messages,
        }
        LeadMongoRepository().collection().update_many({"message_id": data.message_id}, {"$set": set_dict})
        UserLeadMongoRepository().collection().update_many({"message_id": data.message_id}, { "$set": set_dict })
