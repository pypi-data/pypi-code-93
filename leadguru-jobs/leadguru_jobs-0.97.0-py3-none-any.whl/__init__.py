from .jobs.conversation_replied import ConversationRepliedJob, ConversationRepliedJobData
from .jobs.reactions_added import ReactionAddedJobData, ReactionAddedJob

name = "lgt_jobs"

from .jobs.user_limits_update import UpdateUserDataUsageJob, UpdateUserDataUsageJobData
from .jobs.analytics import (TrackAnalyticsJob, TrackAnalyticsJobData)
from .jobs.archive_leads import (ArchiveLeadsJob, ArchiveLeadsJobData)
from .jobs.bot_stats_update import (BotStatsUpdateJob, BotStatsUpdateJobData)
from .jobs.bots_creds_update import (BotsCredentialsUpdateJob, BotsCredentialsUpdateData)
from .jobs.chat_history import (LoadChatHistoryJob, LoadChatHistoryJobData)
from .jobs.restart_bots import (RestartBotsJob, RestartBotsJobData)
from .jobs.restart_dedicated_bots import (RestartDedicatedBotsJob, RestartDedicatedBotsJobData)
from .jobs.update_slack_profile import (UpdateUserSlackProfileJob, UpdateUserSlackProfileJobData)
from .jobs.user_bots_creds_update import (UserBotsCredentialsUpdateJob, UserBotsCredentialsUpdateData)

from .basejobs import (BaseBackgroundJobData, BaseBackgroundJob, InvalidJobTypeException)
from .smtp import (SendMailJob, SendMailJobData)
from .runner import (BackgroundJobRunner)
from .simple_job import (SimpleTestJob, SimpleTestJobData)

jobs_map = {
    "SimpleTestJob": SimpleTestJob,
    "BotStatsUpdateJob": BotStatsUpdateJob,
    "ArchiveLeadsJob": ArchiveLeadsJob,
    "BotsCredentialsUpdateJob": BotsCredentialsUpdateJob,
    "RestartBotsJob": RestartBotsJob,
    "SendMailJob": SendMailJob,
    "TrackAnalyticsJob": TrackAnalyticsJob,
    "LoadChatHistoryJob": LoadChatHistoryJob,
    "UserBotsCredentialsUpdateJob": UserBotsCredentialsUpdateJob,
    "UpdateUserSlackProfileJob": UpdateUserSlackProfileJob,
    "RestartDedicatedBotsJob": RestartDedicatedBotsJob,
    "UpdateUserDataUsageJob": UpdateUserDataUsageJob,
    "ConversationRepliedJob": ConversationRepliedJob,
    "ReactionAddedJob": ReactionAddedJob
}
__all__ = [
    # Jobs
    SimpleTestJob,
    BotStatsUpdateJob,
    ArchiveLeadsJob,
    BotsCredentialsUpdateJob,
    RestartBotsJob,
    SendMailJob,
    SimpleTestJob,
    LoadChatHistoryJob,
    UserBotsCredentialsUpdateJob,
    UpdateUserSlackProfileJob,
    RestartDedicatedBotsJob,
    TrackAnalyticsJob,
    UpdateUserDataUsageJob,
    ConversationRepliedJob,
    ReactionAddedJob,

    # module classes
    BackgroundJobRunner,
    BaseBackgroundJobData,
    BaseBackgroundJob,
    InvalidJobTypeException,

    BotStatsUpdateJobData,
    ArchiveLeadsJobData,
    BotsCredentialsUpdateData,
    RestartBotsJobData,
    SendMailJobData,
    SimpleTestJobData,
    LoadChatHistoryJobData,
    UserBotsCredentialsUpdateData,
    UpdateUserSlackProfileJobData,
    RestartDedicatedBotsJobData,
    TrackAnalyticsJobData,
    UpdateUserDataUsageJobData,
    ConversationRepliedJobData,
    ReactionAddedJobData,

    # mapping
    jobs_map
]
