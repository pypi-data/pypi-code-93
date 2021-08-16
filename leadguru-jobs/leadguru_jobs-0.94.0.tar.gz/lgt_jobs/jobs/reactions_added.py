from abc import ABC

from lgt.common.python.lgt_logging import log
from lgt.common.python.slack_client.web_client import SlackWebClient, get_system_slack_credentials
from lgt_data.mongo_repository import LeadMongoRepository, BotMongoRepository, \
    UserLeadMongoRepository
from pydantic import BaseModel

from ..basejobs import BaseBackgroundJobData, BaseBackgroundJob

"""
Update messages reactions
"""


class ReactionAddedJobData(BaseBackgroundJobData, BaseModel):
    message_id: str
    ts: str

class ReactionAddedJob(BaseBackgroundJob, ABC):
    @property
    def job_data_type(self) -> type:
        return ReactionAddedJobData

    def exec(self, data: ReactionAddedJobData):
        bots = BotMongoRepository().get()
        like_name = '+1'

        lead = LeadMongoRepository().get_by_message_id(data.message_id)
        if not lead:
            return

        creds = get_system_slack_credentials(lead, bots)
        if not creds:
            log.warning(f"Lead: {lead.id}, bot credentials are not valid")
            return

        client = SlackWebClient(creds.token, creds.cookies)
        message_data = client.get_reactions(lead.message.channel_id, lead.message.slack_options['ts'])
        if not message_data['ok']:
            return

        message = message_data.get('message')
        if not message:
            return

        replies = message.get('reply_count')
        lead.replies = replies if replies else 0

        reactions_data = message.get('reactions')
        reactions = reactions_data if reactions_data else []
        for reaction in reactions:
            if reaction["name"] == like_name:
                lead.likes = reaction["count"]
            else:
                lead.reactions += 1

        _set = {
            "likes": lead.likes,
            "reactions": lead.reactions
        }
        LeadMongoRepository().collection().update_many({"message_id": data.message_id}, { "$set": _set })
        UserLeadMongoRepository().collection().update_many({"message_id": data.message_id}, { "$set": _set })