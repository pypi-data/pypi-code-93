from discord import Guild

from .MemberAdapter import MemberAdapter
from ..Permission.DiscordPermissions import GuildPermissions


class MemberGuildAdapter(MemberAdapter):
    """
    A member that is using guild level permissions.
    """

    def __validate__(self, other) -> bool:
        return self.guild == other.guild and super().__eq__(other)

    @property
    def guild(self) -> Guild:
        return self.member.guild

    @property
    def permissions(self) -> GuildPermissions:
        return GuildPermissions.from_member(self.member)
