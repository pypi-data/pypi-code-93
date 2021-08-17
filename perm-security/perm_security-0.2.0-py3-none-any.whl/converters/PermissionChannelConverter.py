from discord.ext.commands import Converter, Context

from ..Permission.DiscordPermissions import TextChannelPermissions


_channel_permissions = {
    "create_instant_invite": TextChannelPermissions.create_instant_invite,
    "manage_channels": TextChannelPermissions.manage_channels,
    "add_reactions": TextChannelPermissions.add_reactions,
    "view_channel": TextChannelPermissions.view_channel,
    "send_messages": TextChannelPermissions.send_messages,
    "send_tts_messages": TextChannelPermissions.send_tts_messages,
    "manage_messages": TextChannelPermissions.manage_messages,
    "embed_links": TextChannelPermissions.embed_links,
    "attach_files": TextChannelPermissions.attach_files,
    "read_message_history": TextChannelPermissions.read_message_history,
    "mention_everyone": TextChannelPermissions.mention_everyone,
    "use_external_emojis": TextChannelPermissions.use_external_emojis,
    "manage_roles": TextChannelPermissions.manage_roles,
    "manage_webhooks": TextChannelPermissions.manage_webhooks,
    "use_application_commands": TextChannelPermissions.use_application_commands,
    "manage_threads": TextChannelPermissions.manage_threads,
    "use_public_threads": TextChannelPermissions.use_public_threads,
    "use_private_threads": TextChannelPermissions.use_private_threads,
    "use_external_stickers": TextChannelPermissions.use_external_stickers,
}


class PermissionChannelConverter(Converter):
    """Tries and finds a valid Permission"""

    async def convert(self, ctx: Context, argument: str) -> TextChannelPermissions:
        checks = [_channel_permissions[check] for check in argument.split(",")]
        return TextChannelPermissions.from_checks(*checks)
