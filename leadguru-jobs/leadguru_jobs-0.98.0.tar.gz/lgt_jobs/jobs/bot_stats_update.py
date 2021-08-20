from abc import ABC
from typing import Optional
from lgt.common.python.slack_client.web_client import SlackWebClient
from lgt_data.mongo_repository import BotMongoRepository, DedicatedBotRepository
from pydantic import BaseModel
from lgt_data.analytics import get_bots_aggregated_analytics

from ..basejobs import BaseBackgroundJob, BaseBackgroundJobData

"""
Update bots statistics
"""


class BotStatsUpdateJobData(BaseBackgroundJobData, BaseModel):
    dedicated_bot_id: Optional[str]
    bot_name: Optional[str]


class BotStatsUpdateJob(BaseBackgroundJob, ABC):
    @property
    def job_data_type(self) -> type:
        return BotStatsUpdateJobData

    def exec(self, data: BotStatsUpdateJobData):
        received_messages, filtered_messages = get_bots_aggregated_analytics(
            bot_names=[data.bot_name] if data.bot_name else None,
            dedicated_bot_ids=[data.dedicated_bot_id] if data.dedicated_bot_id else None)

        if data.dedicated_bot_id:
            bots_rep = DedicatedBotRepository()
            bot = bots_rep.get_by_id(data.dedicated_bot_id)
        else:
            bots_rep = BotMongoRepository()
            bot = bots_rep.get_by_id(data.bot_name)

        if not bot:
            return

        client = SlackWebClient(bot.token, bot.cookies)
        channels = client.channels_list()['channels']

        connected_channels = 0
        channels_users = {}
        users_count = 0
        for channel in channels:
            connected_channels += 1 if channel['is_member'] else 0
            num_members = channel.get('num_members', 0)
            channels_users[channel['id']] = num_members
            users_count += num_members

        bot.messages_received = received_messages.get(bot.name, 0)
        bot.messages_filtered = filtered_messages.get(bot.name, 0)
        bot.connected_channels = connected_channels
        bot.channels = len(channels)
        bot.channels_users = channels_users
        bot.users_count = users_count
        bots_rep.add_or_update(bot)
