import discord, types, typing
from discord.ext import commands
from .gbl import GB


class Hook:
    channel: discord.TextChannel
    hook: discord.Webhook

    @classmethod
    async def connect(cls, channel, name='default'):
        self = cls()
        self.channel = channel
        hooks = await channel.webhooks()
        for hook in hooks:
            if hook.name == name:
                self.hook = hook
                break
        else:
            self.hook = await channel.create_webhook(name=name)
        return self

    async def send(self, msg: discord.TextChannel):
        files = [await attc.to_file() for attc in msg.attachments]
        await self.hook.send(content=msg.content, avatar_url=str(msg.author.avatar_url), username=msg.author.name, tts=msg.tts, files=files)

class MessageLike:
    """
    Children of this class may be passed to Link.send for complete control over the message sent by the webhook
    """
    content: str
    tts: bool
    id: int
    author: types.SimpleNamespace

    # https://i.imgur.com/DTJuzsi.png
    def __init__(self, content, author_name="unset", author_avatar_url="unset", tts: bool = False, id: int = None, channel: discord.TextChannel = None, attachments=None, reference=None):
        if attachments is None: attachments = []
        self.attachments = attachments
        self.content = content
        self.tts = tts
        self.id = id
        self.channel = channel
        self.reference = reference
        self.author = types.SimpleNamespace(name=author_name, avatar_url=author_avatar_url)

    @classmethod
    def from_message(cls, msg: discord.Message):
        if isinstance(msg, cls): return msg
        else: return cls(
            content=msg.content,
            author_name=msg.author.name,
            author_avatar_url=msg.author.avatar_url,
            tts=msg.tts,
            id=msg.id,
            channel=msg.channel,
            attachments=msg.attachments,
            reference=msg.reference
        )


class Link:
    hook: Hook
    channel: discord.TextChannel
    chain: object

    @classmethod
    async def new(cls, channel: discord.TextChannel, chain):
        self = cls()
        self.chain = chain
        self.channel = channel
        self.hook = await Hook.connect(channel, GB.bot.user.name)
        return self

    async def check(self, message: discord.Message):
        if message.channel.id == self.channel.id:
            await self.on_message(message)

    async def on_message(self, message: discord.Message):
        await self.chain.on_message(message)

    async def send(self, msg: typing.Union[discord.Message, MessageLike, str]):
        """
        Send a message to the channel.
        If a string is passed, the bot will not use the webhook to send the message.
        If a discord message is passed, the bot will try to imitate the message and author using a webhook.
        A MessageLike can be passed for finer control.
        """
        if isinstance(msg, str):
            await self.channel.send(msg)
        else:
            await self.hook.send(msg)


class Chain:
    links: list[Link]
    handler: typing.Callable

    @classmethod
    async def new(cls, channels: list[discord.TextChannel]):
        self = cls()
        self.links = [await Link.new(ch,  self) for ch in channels]
        return self

    async def check(self, message: discord.Message):
        for link in self.links:
            await link.check(message)

    async def send(self, message: MessageLike):
        """
        Send a message to each and every channel contained within the chain.
        If a string is passed, the bot will not use the webhook to send the message.
        If a discord message is passed, the bot will try to imitate the message and author using a webhook.
        A MessageLike can be passed for finer control.
        """
        for link in self.links:
            if link.channel != message.channel:
                await link.send(message)

    async def on_message(self, message: MessageLike):
        """
        Decorator that is called whenever any channel contained within this chain receives a message.
        """
        await self.send(message)


class Bot(discord.Client):

    def __init__(self):
        super().__init__()
        self.chains = []
        self.init = None

    async def on_ready(self):
        await self.init()
        print('Logged on as {0}!'.format(GB.bot.user))

    async def on_message(self, message: discord.Message):
        if message.author == self.user or (int(message.author.discriminator) == 0):
            return
        for chain in self.chains:
            await chain.check(message)

    async def register(self, channels: list[int], **options):
        """
        Pass a list of channel IDs.
        A newly created chain (connection) will be returned.
        """
        channels = [GB.bot.get_channel(id) for id in channels]
        chain = await Chain.new(channels)
        self.chains.append(chain)
        return chain

    def configure(self, func: typing.Callable):
        """
        All custom code should be placed within an async function wrapped by this decorator
        """
        self.init = func