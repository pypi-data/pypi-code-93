from quick.commands.context import ContextGroup
from quick.commands.gateway import GatewayGroup
from quick.commands.mirror import MirrorGroup
from quick.commands.streams_app import StreamsAppGroup
from quick.commands.topic import TopicGroup


COMMANDS = [
    ContextGroup,
    TopicGroup,
    GatewayGroup,
    MirrorGroup,
    StreamsAppGroup,
]
