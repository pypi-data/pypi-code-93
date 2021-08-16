import datetime
import time
from abc import ABC
from random import randint

from lgt.common.python.lgt_logging import log
from lgt.common.python.slack_client.web_client import SlackWebClient
from lgt_data.mongo_repository import BotMongoRepository, UserBotCredentialsMongoRepository
from pydantic import BaseModel

from ..basejobs import BaseBackgroundJobData, BaseBackgroundJob

"""
UserBots Credentials update
"""
class UserBotsCredentialsUpdateData(BaseBackgroundJobData, BaseModel):
    bot_name: str
    user_id: str

class UserBotsCredentialsUpdateJob(BaseBackgroundJob, ABC):
    @property
    def job_data_type(self) -> type:
        return UserBotsCredentialsUpdateData

    def exec(self, data: UserBotsCredentialsUpdateData):
        bots_rep = UserBotCredentialsMongoRepository()
        workspace_bots = BotMongoRepository().get()

        # sleep a little bit before moving forward
        time.sleep(randint(10, 100))

        if not [b for b in workspace_bots if b.name == data.bot_name]:
            log.info(f"{data.bot_name} is not in our workspace list. Simply skip it")

        bot = list(filter(lambda x: x.bot_name == data.bot_name, bots_rep.get_bot_credentials(data.user_id)))
        if not bot:
            log.error(f"Unable to find bot {data.bot_name} for user: {data.user_id}")
            return

        bot = bot[0]
        if bot.invalid_creds:
            return

        creds = SlackWebClient.get_access_token(bot.slack_url, bot.user_name, bot.password, True)
        if not creds:
            try:
                SlackWebClient(bot.token, bot.cookies).channels_list()
            except:
                print(f'{bot.bot_name}....[INVALID_CREDS]')
                bots_rep.set(data.user_id, data.bot_name, invalid_creds=True, updated_at=datetime.datetime.utcnow())
                return

        bots_rep.set(data.user_id, data.bot_name, invalid_creds=False, token=creds.token, cookies=creds.cookies, updated_at=datetime.datetime.utcnow())