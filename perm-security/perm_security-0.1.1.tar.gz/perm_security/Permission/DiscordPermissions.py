from perm_banana.banana import banana
from perm_banana.Check import Check
from perm_banana.Permission import Permission
from discord import Member, TextChannel, StageChannel, VoiceChannel


@banana
class GuildPermissions(Permission):
    create_instant_invite = Check(Permission(1 << 0))
    kick_members = Check(Permission(1 << 1))
    ban_members = Check(Permission(1 << 2))
    administrator = Check(Permission(1 << 3))
    manage_channels = Check(Permission(1 << 4))
    manage_guild = Check(Permission(1 << 5))
    add_reactions = Check(Permission(1 << 6))
    view_audit_log = Check(Permission(1 << 7))
    priority_speaker = Check(Permission(1 << 8))
    stream = Check(Permission(1 << 9))
    view_channel = Check(Permission(1 << 10))
    send_messages = Check(Permission(1 << 11))
    send_tts_messages = Check(Permission(1 << 12))
    manage_messages = Check(Permission(1 << 13))
    embed_links = Check(Permission(1 << 14))
    attach_files = Check(Permission(1 << 15))
    read_message_history = Check(Permission(1 << 16))
    mention_everyone = Check(Permission(1 << 17))
    use_external_emojis = Check(Permission(1 << 18))
    view_guild_insights = Check(Permission(1 << 19))
    connect = Check(Permission(1 << 20))
    speak = Check(Permission(1 << 21))
    mute_members = Check(Permission(1 << 22))
    deafen_members = Check(Permission(1 << 23))
    move_members = Check(Permission(1 << 24))
    use_vad = Check(Permission(1 << 25))
    change_nickname = Check(Permission(1 << 26))
    manage_nicknames = Check(Permission(1 << 27))
    manage_roles = Check(Permission(1 << 28))
    manage_webhooks = Check(Permission(1 << 29))
    manage_emojis_and_stickers = Check(Permission(1 << 30))
    use_application_commands = Check(Permission(1 << 31))
    request_to_speak = Check(Permission(1 << 32))
    manage_threads = Check(Permission(1 << 34))
    use_public_threads = Check(Permission(1 << 35))
    use_private_threads = Check(Permission(1 << 36))
    use_external_stickers = Check(Permission(1 << 37))

    @classmethod
    def from_member(cls, member: Member):
        """
        Creates the guild permissions from a member using the value of Discord's permissions.
        """
        return cls(member.guild_permissions.value)


@banana
class StageChannelPermissions(Permission):
    create_instant_invite = Check(Permission(1 << 0))
    manage_channels = Check(Permission(1 << 4))
    view_channel = Check(Permission(1 << 10))
    connect = Check(Permission(1 << 20))
    mute_members = Check(Permission(1 << 22))
    deafen_members = Check(Permission(1 << 23))
    move_members = Check(Permission(1 << 24))
    manage_roles = Check(Permission(1 << 28))
    request_to_speak = Check(Permission(1 << 32))

    @classmethod
    def from_member(cls, member: Member, channel: StageChannel):
        return cls(channel.permissions_for(member).value)


@banana
class TextChannelPermissions(Permission):
    create_instant_invite = Check(Permission(1 << 0))
    manage_channels = Check(Permission(1 << 4))
    add_reactions = Check(Permission(1 << 6))
    view_channel = Check(Permission(1 << 10))
    send_messages = Check(Permission(1 << 11))
    send_tts_messages = Check(Permission(1 << 12))
    manage_messages = Check(Permission(1 << 13))
    embed_links = Check(Permission(1 << 14))
    attach_files = Check(Permission(1 << 15))
    read_message_history = Check(Permission(1 << 16))
    mention_everyone = Check(Permission(1 << 17))
    use_external_emojis = Check(Permission(1 << 18))
    manage_roles = Check(Permission(1 << 28))
    manage_webhooks = Check(Permission(1 << 29))
    use_application_commands = Check(Permission(1 << 31))
    manage_threads = Check(Permission(1 << 34))
    use_public_threads = Check(Permission(1 << 35))
    use_private_threads = Check(Permission(1 << 36))
    use_external_stickers = Check(Permission(1 << 37))

    @classmethod
    def from_member(cls, member: Member, channel: TextChannel):
        return cls(channel.permissions_for(member).value)


@banana
class VoiceChannelPermissions(Permission):
    create_instant_invite = Check(Permission(1 << 0))
    manage_channels = Check(Permission(1 << 4))
    priority_speaker = Check(Permission(1 << 8))
    stream = Check(Permission(1 << 9))
    view_channel = Check(Permission(1 << 10))
    connect = Check(Permission(1 << 20))
    speak = Check(Permission(1 << 21))
    mute_members = Check(Permission(1 << 22))
    deafen_members = Check(Permission(1 << 23))
    move_members = Check(Permission(1 << 24))
    use_vad = Check(Permission(1 << 25))
    manage_roles = Check(Permission(1 << 28))

    @classmethod
    def from_member(cls, member: Member, channel: VoiceChannel):
        return cls(channel.permissions_for(member).value)
