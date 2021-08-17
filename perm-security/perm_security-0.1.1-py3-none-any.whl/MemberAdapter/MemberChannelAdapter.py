from typing import Union

from discord import TextChannel, StageChannel, VoiceChannel

from .MemberAdapter import MemberAdapter
from ..Permission.DiscordPermissions import (
    VoiceChannelPermissions,
    TextChannelPermissions,
    StageChannelPermissions,
)


class MemberChannelAdapter(MemberAdapter):
    """
    A member that is using channel level permissions.
    """

    def __init__(self, member, channel: Union[TextChannel, VoiceChannel, StageChannel], *args, **kwargs):
        self.channel = channel
        super().__init__(member)

    def __validate__(self, other) -> bool:
        return self.channel == other.channel

    @property
    def permissions(self) -> Union[VoiceChannelPermissions, TextChannelPermissions, StageChannelPermissions]:
        if isinstance(self.channel, TextChannel):
            return TextChannelPermissions.from_member(self.member, self.channel)
        elif isinstance(self.channel, VoiceChannel):
            return VoiceChannelPermissions.from_member(self.member, self.channel)
        elif isinstance(self.channel, StageChannel):
            return StageChannelPermissions.from_member(self.member, self.channel)
        else:
            raise NotImplementedError(f"Member {self.member} and {self.channel} do not have any permissions.")
