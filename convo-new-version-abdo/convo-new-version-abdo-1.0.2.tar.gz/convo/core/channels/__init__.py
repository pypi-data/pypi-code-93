from typing import Text, Dict, List, Type

from convo.core.channels.channel import (
    InputSocket,
    OutputSocket,
    UserMsg,
    CollectOutputChannel,
)

# this prevents IDE's from optimizing the imports - we need to import the
# above first, otherwise we will run into import cycles
from convo.core.channels.socketio import ChannelIoInput

pass

from convo.core.channels.botframework import BotFrameworkEnter  # nopep8
from convo.core.channels.callback import CallbackInsert  # nopep8
from convo.core.channels.console import CommandlineInput  # nopep8
from convo.core.channels.facebook import FBInputs  # nopep8
from convo.core.channels.mattermost import MattermostEnter  # nopep8
from convo.core.channels.convo_chat import ChatInput  # nopep8
from convo.core.channels.rest import RestApiInput  # nopep8
from convo.core.channels.rocketchat import RocketChatEnter  # nopep8
from convo.core.channels.slack import SlackEnter  # nopep8
from convo.core.channels.telegram import TGInput  # nopep8
from convo.core.channels.twilio import TWInput  # nopep8
from convo.core.channels.webexteams import WebexTeamsEnter  # nopep8
from convo.core.channels.hangouts import HangoutsEnter  # nopep8

input_channel_classes: List[Type[InputSocket]] = [
    CommandlineInput,
    FBInputs,
    SlackEnter,
    TGInput,
    MattermostEnter,
    TWInput,
    ChatInput,
    BotFrameworkEnter,
    RocketChatEnter,
    CallbackInsert,
    RestApiInput,
    ChannelIoInput,
    WebexTeamsEnter,
    HangoutsEnter,
]

# Mapping from an input channel name to its class to allow name based lookup.
BUILTIN_CHANNELS: Dict[Text, Type[InputSocket]] = {
    c.name(): c for c in input_channel_classes
}
