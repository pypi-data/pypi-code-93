import datetime
from abc import ABC
from typing import List

import pytz
from lgt.common.python.lgt_logging import log
from lgt.common.python.slack_client.slack_client import SlackClient
from lgt.common.python.slack_client.web_client import SlackWebClient
from lgt_data.model import UserBotCredentialsModel, UserModel
from lgt_data.mongo_repository import UserMongoRepository, \
    UserBotCredentialsMongoRepository, DedicatedBotRepository
from pydantic import BaseModel

from ..runner import BackgroundJobRunner
from ..basejobs import BaseBackgroundJobData, BaseBackgroundJob

"""
Update Slack User profile
"""
class UpdateUserSlackProfileJobData(BaseBackgroundJobData, BaseModel):
    user_id: str
    bot_name: str

class UpdateUserSlackProfileJob(BaseBackgroundJob):
    @staticmethod
    def __update_profile(user: UserModel, slack: SlackClient) -> bool:
        try:
            profile_resp = slack.get_profile()
        except:
            log.warning(f"User: {user.email} Bot credentials are not valid")
            return False

        if not profile_resp["ok"]:
            return False

        profile = {
            'title': profile_resp['profile']["title"],
            'phone': profile_resp['profile']["phone"],
            'skype': profile_resp['profile']["skype"],
            'real_name': profile_resp['profile']["real_name"],
            'display_name': profile_resp['profile']["display_name"]
        }
        # try to update user photo
        if user.photo_url:
            photo_resp = slack.update_profile_photo(user.photo_url)
            log.info(f"[PHOTO UPDATE] {photo_resp}")

        return True

    @property
    def job_data_type(self) -> type:
        return UpdateUserSlackProfileJobData

    @staticmethod
    def try_bot_credentials(bot: UserBotCredentialsModel) -> UserBotCredentialsModel:
        utcnow = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
        cred_date_time = bot.updated_at.replace(tzinfo=pytz.UTC)
        if (utcnow - cred_date_time).days > 7:
            login_response = SlackWebClient.get_access_token(bot.slack_url, bot.user_name, bot.password)
            if login_response:
                return UserBotCredentialsMongoRepository().update_bot_creadentials(bot.user_id, bot.bot_name,
                                          bot.user_name, bot.password, bot.slack_url,
                                          login_response.token, login_response.cookies)

        return bot

    @staticmethod
    def update_all_user_bots_command(data: UpdateUserSlackProfileJobData, bots: List[UserBotCredentialsModel]):
        for bot in bots:
            BackgroundJobRunner.submit(UpdateUserSlackProfileJob,
                                       UpdateUserSlackProfileJobData(user_id=data.user_id,
                                                                     bot_name=bot.bot_name))

        UpdateUserSlackProfileJob.update_dedicated_bot_profile(data)

    @staticmethod
    def update_dedicated_bot_profile(data: UpdateUserSlackProfileJobData):
        user = UserMongoRepository().get(data.user_id)
        bots = DedicatedBotRepository().get_user_bots(data.user_id)
        for bot in bots:
            if bot.invalid_creds:
                log.warning(f'User: {user.email} dedicated bot: {bot.name} credentials are invalid. Not able to update user profile')
                continue

            slack = SlackClient(bot.token, bot.cookies)
            UpdateUserSlackProfileJob.__update_profile(user, slack)


    @staticmethod
    def update_single_user_bots_command(data: UpdateUserSlackProfileJobData, bots: List[UserBotCredentialsModel]):
        user = UserMongoRepository().get(data.user_id)
        for bot in bots:
            if bot.bot_name != data.bot_name:
                continue

            if bot.invalid_creds:
                log.warning(f'User: {user.email} bot: {bot.bot_name} credentials are invalid. Not able to update user profile')
                continue

            if not bot.user_name or not bot.password:
                log.warning(f"User: {user.email} Bot: {bot.bot_name} credentials are not SET")
                continue


            bot = UpdateUserSlackProfileJob.try_bot_credentials(bot)
            slack = SlackClient(bot.token, bot.cookies)
            result = UpdateUserSlackProfileJob.__update_profile(user, slack)
            if result:
                UserBotCredentialsMongoRepository().set(user_id=data.user_id, bot_name=data.bot_name,
                                                        slack_profile=user.slack_profile.to_dic())

            if user.slack_profile:
                print(slack.update_profile(user.slack_profile.to_dic()))


    def exec(self, data: UpdateUserSlackProfileJobData):
        bots = UserBotCredentialsMongoRepository().get_bot_credentials(data.user_id)
        if data.bot_name == '':
            UpdateUserSlackProfileJob.update_all_user_bots_command(data, bots)
        else:
            UpdateUserSlackProfileJob.update_single_user_bots_command(data, bots)

