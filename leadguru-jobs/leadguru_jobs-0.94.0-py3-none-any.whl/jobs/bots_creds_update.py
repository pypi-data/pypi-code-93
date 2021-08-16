import time
from abc import ABC
from random import randint

from lgt.common.python.slack_client.web_client import SlackWebClient
from lgt_data.mongo_repository import BotMongoRepository
from pydantic import BaseModel

from ..basejobs import BaseBackgroundJob, BaseBackgroundJobData

"""
Bots Credentials update
"""
class BotsCredentialsUpdateData(BaseBackgroundJobData, BaseModel):
    bot_name: str


class BotsCredentialsUpdateJob(BaseBackgroundJob, ABC):
    @property
    def job_data_type(self) -> type:
        return BotsCredentialsUpdateData

    def exec(self, data: BotsCredentialsUpdateData):
        bots_rep = BotMongoRepository()
        bot = bots_rep.get_by_id(data.bot_name)

        # sleep a little bit before moving forward
        time.sleep(randint(10, 100))

        creds = SlackWebClient.get_access_token(bot.slack_url, bot.user_name, bot.password, True)
        if not creds:
            try:
                SlackWebClient(bot.token, bot.cookies).channels_list()
                print("Login failed but we still have valid credentials in our database")
                return
            except Exception:
                # here we 100 percents sure that the credentials a valid
                print(f'{data.bot_name}....[INVALID_CREDS]')
                bot.invalid_creds = True
                bots_rep.add_or_update(bot)
                return

        bot.token = creds.token
        bot.cookies = creds.cookies
        bot.invalid_creds = False
        bots_rep.add_or_update(bot)
        print(f'{data.bot_name}....[UPDATED]')
