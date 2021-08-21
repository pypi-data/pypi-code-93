# class User():
#     def __init__(self, **kwargs):
#         self.username = kwargs.get('username')
#         self.public_flags = kwargs.get('public_flags')
#         self.id = kwargs.get('id')
#         self.discriminator = kwargs.get('discriminator')
#         self.avatar = kwargs.get('avatar')
#         self.roles = kwargs.get('roles')
#         self.premium_since = kwargs.get('premium_since')
#         self.pending = bool(kwargs.get('pending'))
#         self.nick = kwargs.get('nick')
#         self.mute = bool(kwargs.get('mute'))
#         self.joined_at = kwargs.get('joined_at')
#         self.is_pending = bool(kwargs.get('is_pending'))
#         self.hoisted_role = kwargs.get('hoisted_role')
#         self.deaf = bool(kwargs.get('deaf'))
#         self.avatar
from ._requests import *


class Member:
    def __init__(self, **kwargs):
        self.user = User(**kwargs.get('user')) if kwargs.get('user') else None
        self.nick = kwargs.get('nick') or None
        self.roles = list(kwargs.get('roles')) if kwargs.get('roles') else []
        self.joined_at = kwargs.get('joined_at')


class User:
    def __init__(self, **kwargs):
        self.username = kwargs.get('username')
        self.public_flags = int(kwargs.get('public_flags')) if kwargs.get(
            'public_flags') else None
        self.id = kwargs.get('id')
        self.discriminator = kwargs.get('discriminator')
        self.avatar = kwargs.get('avatar')
        self.bot = bool(kwargs.get('bot')) if kwargs.get('bot') else False
        self.system = bool(kwargs.get('system')) if kwargs.get(
            'system') else False
        self.mfa_enabled = bool(kwargs.get('mfa_enabled')) if kwargs.get(
            'mfa_enabled') else False
        self.locale = kwargs.get('locale') or None
        self.verified = bool(kwargs.get('verified')) if kwargs.get(
            'verified') else False
        self.email = kwargs.get('email') or None
        self.flags = int(kwargs.get('flags')) if kwargs.get('flags') else None
        self.premium_type = int(kwargs.get('premium_type')) if kwargs.get(
            'premium_type') else None
        self.webhook_id = kwargs.get('webhook_id') or None


class Connection:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.type = kwargs.get('type')
        self.revoked = bool(kwargs.get('revoked')) if kwargs.get(
            'revoked') else False
        self.integrations = list(kwargs.get('integrations')) if kwargs.get(
            'integrations') else None
        self.verified = bool(kwargs.get('verified'))
        self.friend_sync = bool(kwargs.get('friend_sync'))
        self.show_activity = bool(kwargs.get('show_activity'))
        self.visibility = int(kwargs.get('visibility'))


class Overwrite:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.type = kwargs.get('type')
        self.allow = kwargs.get('allow')
        self.deny = kwargs.get('deny')


class ThreadMetadata:
    def __init__(self, **kwargs):
        self.archived = bool(kwargs.get('archived'))
        self.auto_archive_duration = kwargs.get('auto_archive_duration')
        self.archive_timestamp = kwargs.get('archive_timestamp')
        self.locked = kwargs.get('locked') or False


class ThreadMember:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id') or None
        self.user_id = kwargs.get('user_id') or None
        self.join_timestamp = kwargs.get('join_timestamp') or None
        self.flags = kwargs.get('flags') or None


class Client_Status:
    def __init__(self, **kwargs):
        self.desktop = kwargs.get('desktop') or None
        self.mobile = kwargs.get('mobile') or None
        self.web = kwargs.get('web') or None


class Activity:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.type = int(kwargs.get('type'))
        self.url = kwargs.get('url') if self.type == 1 else None
        self.created_at = int(kwargs.get('created_at'))
        self.timestamps = ActivityTimestamps(
            **kwargs.get('timestamps')) if kwargs.get('timestamps') else None
        self.application_id = int(kwargs.get('application_id'))
        self.details = kwargs.get('details') or None
        self.state = kwargs.get('state') or None
        self.emoji = ActivityEmoji(
            **kwargs.get('emoji')) if kwargs.get('emoji') else None
        self.party = ActivityParty(
            **kwargs.get('party')) if kwargs.get('party') else None
        self.assets = ActivityAssets(
            **kwargs.get('assets')) if kwargs.get('assets') else None
        self.secrets = ActivitySecrets(
            **kwargs.get('secrets')) if kwargs.get('secrets') else None
        self.instance = bool(kwargs.get('instance') or None)
        self.flags = kwargs.get('flags') or None
        self.buttons = list(ActivityButtons(
            **kwargs.get('buttons'))) if kwargs.get('buttons') else None


class ActivityButtons:
    def __init__(self, **kwargs):
        self.label = kwargs.get('label')
        self.url = kwargs.get('url')


class ActivityAssets:
    def __init__(self, **kwargs):
        self.large_image = kwargs.get('large_image') or None
        self.large_text = kwargs.get('large_text') or None
        self.small_image = kwargs.get('small_image') or None
        self.small_text = kwargs.get('small_text') or None


class ActivityFlags:
    INSTANCE = 1 << 0
    JOIN = 1 << 1
    SPECTATE = 1 << 2
    JOIN_REQUEST = 1 << 3
    SYNC = 1 << 4
    PLAY = 1 << 5


class ActivitySecrets:
    def __init__(self, **kwargs):
        self.join = kwargs.get('join') or None
        self.spectate = kwargs.get('spectate') or None
        self.match = kwargs.get('match') or None


class ActivityParty:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id') or None
        self.size = list(kwargs.get('size')) if kwargs.get('size') else None


class ActivityEmoji:
    def __init__(self, **kwargs):
        self.name = str(kwargs.get('name'))
        self.id = int(kwargs.get('id')) if kwargs.get('id') else None
        self.animated = bool(kwargs.get('animated')) if kwargs.get(
            'animated') else None


class ActivityTimestamps:
    def __init__(self, **kwargs):
        self.start = int(kwargs.get('start')) if kwargs.get('start') else None
        self.end = int(kwargs.get('end')) if kwargs.get('end') else None


class Presence:
    def __init__(self, **kwargs):
        self.user = User(**kwargs.get('user'))
        self.guild_id = int(kwargs.get('guild'))
        self.status = str(kwargs.get('status'))
        self.activites = list(User(**kwargs.get('activites'))
                              if kwargs.get('activites') else []) or []
        self.client_status = Client_Status(
            **kwargs.get('client_status')) if kwargs.get('client_status') else None


class WelcomeScreenChannel:
    def __init__(self, **kwargs):
        self.channel_id = kwargs.get('channel_id')
        self.description = kwargs.get('description')
        self.emoji_id = kwargs.get('emoji_id')
        self.emoji_name = kwargs.get('emoji_name')


class WelcomeScreen:
    def __init__(self, **kwargs):
        self.description = kwargs.get('description') or None
        self.welcome_channels = list(WelcomeScreenChannel(
            **kwargs.get('welcome_channels')) if kwargs.get('welcome_channels') else []) or None


class StageInstance:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.guild_id = kwargs.get('guild_id')
        self.channel_id = kwargs.get('channel_id')
        self.topic = kwargs.get('topic')
        self.privacy_level = kwargs.get('privacy_level')
        self.discoverable_disabled = kwargs.get('discoverable_disabled')


class Sticker:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.pack_id = kwargs.get('pack_id')
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.tag = kwargs.get('tag')
        self.type = kwargs.get('type')
        self.format_type = kwargs.get('format_type')
        self.available = kwargs.get('available') or None
        self.guild_id = kwargs.get('guild_id') or None
        self.user = User(**kwargs.get('user')) if kwargs.get('user') else None
        self.sort_value = kwargs.get('sort_value') or None


class RoleTags:
    def __init__(self, **kwargs):
        self.bot_id = kwargs.get('bot_id')
        self.integration_id = kwargs.get('integration_id')
        self.premium_subscriber = kwargs.get('premium_subscriber') or None


class Role:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.color = kwargs.get('color')
        self.hoist = kwargs.get('hoist')
        self.position = kwargs.get('position')
        self.premissions = kwargs.get('premissions')
        self.managed = kwargs.get('managed')
        self.mentionable = kwargs.get('mentionable')
        self.tags = RoleTags(**kwargs.get('tags')
                             ) if kwargs.get('tags') else None


class Guild:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.icon = kwargs.get('icon') or None
        self.icon_hash = kwargs.get('icon_hash') or None
        self.splash = kwargs.get('splash') or None
        self.discovery_splash = kwargs.get('discovery_splash') or None
        self.owner = kwargs.get('owner') or None
        self.owner_id = kwargs.get('owner_id') or None,
        self.permissions = kwargs.get('permissions') or None,
        self.afk_channel_id = kwargs.get('afk_channel_id') or None,
        self.afk_timeout = kwargs.get('afk_timeout') or None,
        self.widget_enabled = bool(kwargs.get('widget_enabled')) if kwargs.get(
            'widget_enabled') else None
        self.widget_channel_id = kwargs.get('widget_channel_id') or None
        self.verification_level = int(kwargs.get('verification_level'))
        self.default_message_notifications = int(
            kwargs.get('default_message_notifications'))
        self.explicit_content_filter = int(
            kwargs.get('explicit_content_filter'))
        self.roles = list(kwargs.get('roles')) if kwargs.get('roles') else []
        self.emojis = list(kwargs.get('emojis')
                           ) if kwargs.get('emojis') else []
        self.features = list(kwargs.get('features')
                             ) if kwargs.get('features') else []
        self.mfa_level = int(kwargs.get('mfa_level'))
        self.application_id = int(kwargs.get('application_id')) if kwargs.get(
            'application_id') else None
        self.system_channel_id = int(kwargs.get('system_channel_id')) if kwargs.get(
            'system_channel_id') else None
        self.system_channel_flags = int(kwargs.get('system_channel_flags'))
        self.rules_channel_id = int(kwargs.get('rules_channel_id')) if kwargs.get(
            'rules_channel_id') else None
        self.joined_at = kwargs.get('joined_at') or None
        self.large = bool(kwargs.get('large')) if kwargs.get(
            'large') else False
        self.unavailable = bool(kwargs.get('unavailable')) if kwargs.get(
            'unavailable') else False
        self.member_count = int(kwargs.get('member_count')) if kwargs.get(
            'member_count') else 0
        self.voice_states = list(kwargs.get('voice_states')) if kwargs.get(
            'voice_states') else []
        self.members = list(
            Member(**i) for i in kwargs.get('members')) if kwargs.get('members') else []
        self.channels = list(Channel(**i)
                             for i in kwargs.get('channels')) if kwargs.get('channels') else []
        self.threads = list(
            Channel(**i) for i in kwargs.get('threads')) if kwargs.get('threads') else []
        self.presences = list(Presence(**kwargs.get('presences'))
                              if kwargs.get('presences') else []) if kwargs.get('presences') else []
        self.max_presences = kwargs.get('max_presences')
        self.max_members = kwargs.get('max_members')
        self.vanity_url_code = kwargs.get('vanity_url_code')
        self.description = kwargs.get('description')
        self.banner = kwargs.get('banner')
        self.premium_tier = kwargs.get('premium_tier')
        self.premium_subscription_count = kwargs.get(
            'premium_subscription_count') or None
        self.preferred_locale = kwargs.get('preferred_locale')
        self.public_updates_channel_id = kwargs.get(
            'public_updates_channel_id')
        self.max_video_channel_users = kwargs.get(
            'max_video_channel_users') or None
        self.approximate_member_count = kwargs.get(
            'approximate_member_count') or None
        self.approximate_presence_count = kwargs.get(
            'approximate_presence_count') or None
        self.welcome_screen = WelcomeScreen(
            **kwargs.get('welcome_screen')) if kwargs.get('welcome_screen') else None
        self.nsfw_level = kwargs.get('nsfw_level')
        self.stage_instances = list(StageInstance(
            **kwargs.get('stage_instances')) if kwargs.get('stage_instances') else []) or []
        self.stickers = list(Sticker(**kwargs.get('stickers'))
                             if kwargs.get('stickers') else []) or None


class ChannelMention:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.guild_id = kwargs.get('guild_id')
        self.type = kwargs.get('type')
        self.name = kwargs.get('name')


class Attachment:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.filename = kwargs.get('filename')
        self.content_type = kwargs.get('content_type') or None
        self.size = kwargs.get('size')
        self.url = kwargs.get('url')
        self.proxy_url = kwargs.get('proxy_url')
        self.height = kwargs.get('height') or None
        self.width = kwargs.get('width') or None


class Embed:
    def __init__(self, **kwargs):
        self.dict_: dict
        self.title = kwargs.get('title') or None
        self.dict_["title"] = self.title
        self.type = kwargs.get('type') or None
        self.dict_["type"] = self.type
        self.description = kwargs.get('description') or None
        self.dict_["description"] = self.description
        self.url = kwargs.get('url') or None
        self.dict_["url"] = self.url
        self.timestamp = kwargs.get('timestamp') or None
        self.dict_["timestamp"] = self.timestamp
        self.color = kwargs.get('color') or None
        self.dict_["color"] = self.color
        self.footer = EmbedFooter(
            **kwargs.get('footer')) if kwargs.get('footer') else None
        self.dict_["footer"] = self.footer
        self.image = EmbedImage(**kwargs.get('image')
                                ) if kwargs.get('image') else None
        self.dict_["image"] = self.image
        self.thumbnail = EmbedThumbnail(
            **kwargs.get('thumbnail')) if kwargs.get('thumbnail') else None
        self.dict_["thumbnail"] = self.thumbnail
        self.video = EmbedVideo(**kwargs.get('video')
                                ) if kwargs.get('video') else None
        self.dict_["video"] = self.video
        self.provider = EmbedProvider(
            **kwargs.get('provider')) if kwargs.get('provider') else None
        self.dict_["provider"] = self.provider
        self.author = EmbedAuthor(
            **kwargs.get('author')) if kwargs.get('author') else None
        self.dict_["author"] = self.author
        self.fields = EmbedField(
            **kwargs.get('fields')) if kwargs.get('fields') else None
        self.dict_["fields"] = self.fields

    def json(self):
        return_dict: dict = {}
        for name, value in self.dict_:
            if value is not None:
                return_dict[name] = value

        return return_dict


class EmbedThumbnail:
    def __init__(self, **kwargs):
        self.url = kwargs.get('url') or None
        self.proxy_url = kwargs.get('proxy_url') or None
        self.height = kwargs.get('height') or None
        self.width = kwargs.get('width') or None


class EmbedVideo:
    def __init__(self, **kwargs):
        self.url = kwargs.get('url') or None
        self.proxy_url = kwargs.get('proxy_url') or None
        self.height = kwargs.get('height') or None
        self.width = kwargs.get('width') or None


class EmbedImage:
    def __init__(self, **kwargs):
        self.url = kwargs.get('url') or None
        self.proxy_url = kwargs.get('proxy_url') or None
        self.height = kwargs.get('height') or None
        self.width = kwargs.get('width') or None


class EmbedProvider:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name') or None
        self.url = kwargs.get('url') or None


class EmbedAuthor:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name') or None
        self.url = kwargs.get('url') or None
        self.icon_url = kwargs.get('icon_url') or None
        self.proxy_icon_url = kwargs.get('proxy_icon_url') or None


class EmbedFooter:
    def __init__(self, **kwargs):
        self.text = kwargs.get('text')
        self.icon_rl = kwargs.get('icon_url') or None
        self.proxy_icon_url = kwargs.get('proxy_icon_url') or None


class EmbedField:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.value = kwargs.get('value')
        self.inline = kwargs.get('inline') or None


class Emoji:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id') or None
        self.name = kwargs.get('name') or None
        self.roles = list(Role(**kwargs.get('roles'))
                          if kwargs.get('roles') else []) or None
        self.user = User(**kwargs.get('user')) if kwargs.get('user') else None
        self.require_colons = kwargs.get('require_colons') or None
        self.managed = kwargs.get('managed') or None
        self.animated = kwargs.get('animated') or None
        self.available = kwargs.get('available') or None


class Reaction:
    def __init__(self, **kwargs):
        self.count = kwargs.get('count')
        self.me = bool(kwargs.get('me'))
        self.emoji = Emoji(**kwargs.get('emoji')
                           ) if kwargs.get('emoji') else None


class MessageActivity:
    def __init__(self, **kwargs):
        self.type = kwargs.get('type')
        self.party_id = kwargs.get('party_id') or None


class Application:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.icon = kwargs.get('icon') or None
        self.description = kwargs.get('description')
        self.rpc_origins = list((i for i in kwargs.get(
            'rpc_origins')) if kwargs.get('rpc_origins') else []) or False
        self.bot_public = bool(kwargs.get('bot_public'))
        self.bot_require_code_grant = bool(
            kwargs.get('bot_require_code_grant'))
        self.terms_of_service_url = kwargs.get('terms_of_service_url') or None
        self.privacy_policy_url = kwargs.get('privacy_policy_url') or None
        self.owner = User(**kwargs.get('owner')
                          ) if kwargs.get('owner') else None
        self.summary = kwargs.get('summary')
        self.verify_key = kwargs.get('verify_key')
        self.team = Team(**kwargs.get('team')) if kwargs.get('team') else None
        self.guild_id = kwargs.get('guild_id') or None
        self.primary_sku_id = kwargs.get('primary_sku_id') or None
        self.slug = kwargs.get('slug') or None
        self.cover_image = kwargs.get('cover_image') or None
        self.flags = kwargs.get('flags') or None


class Team:
    def __init__(self, **kwargs):
        self.icon = kwargs.get('icon') or None
        self.id = kwargs.get('id') or None
        self.members = list(TeamMember(**kwargs.get('members'))
                            ) if kwargs.get('members') else None
        self.name = kwargs.get('name')
        self.owner_user_id = kwargs.get('owner_user_id')


class TeamMember:
    def __init__(self, **kwargs):
        self.membership_state = kwargs.get('membership_state')
        self.permissions = list(kwargs.get('permissions'))
        self.team_id = kwargs.get('team_id')
        self.user = User(**kwargs.get('user')) if kwargs.get('user') else None


class MessageReference:
    def __init__(self, **kwargs):
        self.message_id = kwargs.get('message_id')
        self.channel_id = kwargs.get('channel_id') or None
        self.guild_id = kwargs.get('guild_id') or None
        self.fail_if_not_exists = kwargs.get('fail_if_not_exists') or None


class SelectMenu:
    def __init__(self, **kwargs):
        self.type = kwargs.get('type')
        self.custom_id = kwargs.get('custom_id')
        self.options = list(SelectOption(**kwargs.get('options'))
                            if kwargs.get('options') else []) or None
        self.placeholder = kwargs.get('placeholder') or None
        self.min_values = kwargs.get('min_values') or None
        self.max_values = kwargs.get('max_values') or None
        self.disabled = kwargs.get('disabled') or None


class SelectOption:
    def __init__(self, **kwargs):
        self.label = kwargs.get('label')
        self.value = kwargs.get('value')
        self.description = kwargs.get('description') or None
        self.emoji = Emoji(**kwargs.get('emoji')
                           ) if kwargs.get('emoji') else None
        self.default = kwargs.get('default') or None


class AllowedMention:
    def __init__(self, **kwargs):
        self.parse = list(AllowedMentionType(**i)
                          for i in kwargs.get('parse')) if kwargs.get('parse') else None
        self.roles = kwargs.get('roles')
        self.users = kwargs.get('users')
        self.replied_user = kwargs.get('replied_user') or False


class Component:
    def __init__(self, **kwargs):
        self.type = kwargs.get('type')
        self.custom_id = kwargs.get('custom_id') or None
        self.disabled = kwargs.get('disabled') or None
        self.style = kwargs.get('style') or None
        self.label = kwargs.get('label') or None
        self.emoji = Emoji(**kwargs.get('emoji')
                           ) if kwargs.get('emoji') else None
        self.url = kwargs.get('url') or None
        self.options = list(SelectOption(
            **i) for i in kwargs.get('options')) if kwargs.get('options') else None
        self.placeholder = kwargs.get('placeholder') or None
        self.min_values = kwargs.get('min_values') or None
        self.max_values = kwargs.get('max_values') or None
        self.components = list(Component(
            **i) for i in kwargs.get('components')) if kwargs.get('components') else None


class Interaction:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.application_id = kwargs.get('application_id')
        self.type = kwargs.get('type')
        self.data = InteractionData(**kwargs.get(
            'data')) if kwargs.get('data') else None
        self.guild_id = kwargs.get('guild_id') or None
        self.channel_id = kwargs.get('channel_id') or None
        self.member = Member(**kwargs.get('member')
                             ) if kwargs.get('member') else None
        self.user = User(**kwargs.get('user')) if kwargs.get('user') else None
        self.token = kwargs.get('token')
        self.version = kwargs.get('version')
        self.message = Message(**kwargs.get('message')
                               ) if kwargs.get('message') else None

    async def reply(self, msg):
        if isinstance(msg, Message):
            pass
        req_body = {
            'type': 4,
            'data': {
                'content': msg
            }
        }
        post(
            f'/interactions/{self.id}/{self.token}/callback', req_body)

    async def reply_raw(self, message, type: int = 4, embeds: list = None, tts=None, file=None, payload_json=None, allowed_mentions: AllowedMention = None, message_reference: MessageReference = None, components: Component = None, sticker_ids: list = None):
        if embeds:
            for i in embeds:
                if not isinstance(i, Embed):
                    raise TypeError(
                        "embeds must be an instance of <class 'Embed'>")
        base_json = {
            "content": message,
        }
        if embeds:
            base_json["embeds"] = embeds
        if tts:
            base_json["tts"] = tts

        if file:
            base_json["file"] = file
        if payload_json:
            base_json["payload_json"] = payload_json
        if allowed_mentions:
            base_json["allowed_mentions"] = allowed_mentions
        if message_reference:
            base_json["message_reference"] = message_reference
        if components:
            base_json["components"] = components
        if sticker_ids:
            base_json["sticker_ids"] = sticker_ids

        req_body = {
            "type": type,
            "data": base_json,
        }

        post(
            f'/interactions/{self.id}/{self.token}/callback', req_body)


class InteractionData:  # https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object-interaction-type
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.type = kwargs.get('type')
        self.resolved = ResolvedData(
            **kwargs.get('resolved')) if kwargs.get('resolved') else None
        # TODO add when support application command (slash commands)
        # self.options
        self.custom_id = kwargs.get('custom_id')
        self.component_type = kwargs.get('component_type') or None
        self.values = list(SelectOption(
            **i) for i in kwargs.get('values')) if kwargs.get('values') else None
        self.target_id = kwargs.get('target_id') or None


class ResolvedData:
    def __init__(self, **kwargs):
        self.users = map(User(**kwargs.get('users')),
                         User.objects.filter()) if kwargs.get('users') else None
        self.members = map(Member(**kwargs.get('members')),
                           Member.objects.filter()) if kwargs.get('members') else None
        self.roles = map(Role(**kwargs.get('roles')),
                         Role.objects.filter()) if kwargs.get('roles') else None
        self.channels = map(Channel(**kwargs.get('channels')),
                            Channel.objects.filter()) if kwargs.get('channels') else None
        self.messages = map(Message(**kwargs.get('messages')),
                            Message.objects.filter()) if kwargs.get('messages') else None


class MessageInteraction:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.type = Interaction(**kwargs.get('type'))
        self.name = kwargs.get('name')
        self.user = User(**kwargs.get('user')) if kwargs.get('user') else None


class StickerItem:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.format_type = kwargs.get('format_type')


class Message:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.channel_id = kwargs.get('channel_id')
        self.guild_id = kwargs.get('guild_id')
        self.author = User(**kwargs.get('author'))
        self.member = (Member(**i) for i in kwargs.get('member')
                       ) if kwargs.get('member') else None
        self.content = kwargs.get('content')
        self.timestamp = kwargs.get('timestamp')
        self.edited_timestamp = kwargs.get('edited_timestamp') or None
        self.tts = bool(kwargs.get('tts'))
        self.mention_everyone = bool(kwargs.get('mention_everyone'))
        self.mentions = list((User(**i) for i in kwargs.get('mentions'))
                             if kwargs.get('mentions') else []) or None
        self.mention_roles = list(Role(
            **kwargs.get("mention_roles")) if kwargs.get("mention_roles") else []) or None
        self.mention_channels = ChannelMention(
            **kwargs.get('mention_channels')) if kwargs.get('mention_channels') else None
        self.attachments = list(Attachment(
            **kwargs.get('attachments')) if kwargs.get('attachments') else []) or None
        self.embeds = list(Embed(**kwargs.get('embeds'))
                           if kwargs.get('embeds') else []) or None
        self.reactions = list(Reaction(**kwargs.get('reactions'))
                              if kwargs.get('reactions') else []) or None
        self.nonce = kwargs.get('nonce') or None
        self.pinned = bool(kwargs.get('pinned'))
        self.webhook_id = None if not kwargs.get(
            'webhook_id') else kwargs.get('webhook_id')
        self.type = kwargs.get('type')
        self.activity = MessageActivity(
            **kwargs.get('activity')) if kwargs.get('activity') else None
        self.application = Application(
            **kwargs.get('application')) if kwargs.get('application') else None
        self.application_id = kwargs.get('application_id') or None
        self.message_reference = MessageReference(
            **kwargs.get('message_reference')) if kwargs.get('message_reference') else None
        self.flags = kwargs.get('flags') or None
        self.referenced_message = Message(
            **kwargs.get('referenced_message')) if kwargs.get('referenced_message') else None
        self.interaction = MessageInteraction(
            **kwargs.get('interaction')) if kwargs.get('interaction') else None
        self.thread = Channel(**kwargs.get('thread')
                              ) if kwargs.get('thread') else None
        self.components = list(Component(
            **i) for i in kwargs.get('components')) if kwargs.get('components') else None
        self.sticker_items = list(StickerItem(
            **i) for i in kwargs.get('sticker_items')) if kwargs.get('sticker_items') else None
        self.stickers = list(Sticker(
            **i) for i in kwargs.get('stickers')) if kwargs.get('stickers') else None
        self.channel = self.get_channel()

    def get_channel(self):
        return Channel(
            **get(f'/channels/{self.channel_id}').json()) if self.channel_id else None


class AllowedMentionType:
    def __init__(self, type_):
        self.type = "roles" if type_ == "roles" else (
            "users" if type_ == "users" else ("everyone" if type_ == "everyone" else None))


class Channel:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.type = kwargs.get('type') or 1
        self.guild_id = kwargs.get('guild_id') or None
        self.position = int(kwargs.get('position')) if kwargs.get(
            'position') else None
        self.permission_overwrites = list(Overwrite(**i) for i in kwargs.get(
            'permission_overwrites')) if kwargs.get('permission_overwrites') else None
        self.name = kwargs.get('name') or None
        self.topic = kwargs.get('topic') or None
        self.nsfw = kwargs.get('nsfw') or None
        self.last_message_id = kwargs.get('last_message_id') or None
        self.birate = kwargs.get('birate') or None
        self.user_limit = int(kwargs.get('user_limit')
                              ) if kwargs.get('user_limit') else None
        self.rate_limit_per_user = kwargs.get('rate_limit_per_user') or None
        self.recipients = list(
            User(**i) for i in kwargs.get('recipients')) if kwargs.get('recipients') else []
        self.icon = kwargs.get('icon') or None
        self.owner_id = kwargs.get('owner_id') or None
        self.application_id = kwargs.get('application_id') or None
        self.parent_id = kwargs.get('parent_id') or None
        self.last_pin_timestamp = kwargs.get('last_pin_timestamp') or None
        self.rtc_region = kwargs.get('rtc_region') or None
        self.video_quality_mode = kwargs.get('video_quality_mode') or None
        self.message_count = kwargs.get('message_count') or None
        self.member_count = kwargs.get('member_count') or None
        self.thread_metadata = ThreadMetadata(
            **kwargs.get('thread_metadata')) if kwargs.get('thread_metadata') else None
        self.member = ThreadMember(
            **kwargs.get('member')) if kwargs.get('member') else None
        self.default_auto_archive_duration = kwargs.get(
            'default_auto_archive_duration') or None
        self.permissions = kwargs.get('permissions') or None

    async def send(self, message, channelId=None, embeds: list = None, tts=None, file=None, payload_json=None, allowed_mentions: AllowedMention = None, message_reference: MessageReference = None, components: Component = None, sticker_ids: list = None):
        if embeds:
            for i in embeds:
                if not isinstance(i, Embed):
                    raise TypeError(
                        "embeds must be an instance of <class 'Embed'>")
        base_json = {
            "content": message,
        }
        if embeds:
            base_json["embeds"] = embeds
        if tts:
            base_json["tts"] = tts

        if file:
            base_json["file"] = file
        if payload_json:
            base_json["payload_json"] = payload_json
        if allowed_mentions:
            base_json["allowed_mentions"] = allowed_mentions
        if message_reference:
            base_json["message_reference"] = message_reference
        if components:
            base_json["components"] = components
        if sticker_ids:
            base_json["sticker_ids"] = sticker_ids
        post(
            f"/channels/{channelId if channelId else self.id}/messages", base_json)
