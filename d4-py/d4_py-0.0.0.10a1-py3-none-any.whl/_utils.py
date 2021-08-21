from ._d4 import *
import typing
import inspect
from ._requests import get, post, patch, delete
from ._models import *


def nitro_converter(value):
    return {
        0 or '0': None,
        1 or '1': 'Nitro Classic',
        2 or '2': 'Nitro'
    }[value]


def visibility_converter(value):
    return {
        0 or '0': None,
        1 or '1': 'Everyone'
    }[value]


def get_current_user():
    return User(**get('/users/@me').json())


def get_user(id_):  # TODO: Check if ** works or not
    id_ = str(id_)
    return User(**get(f'users/{id_}').json())


def modify_current_user(username=None, avatar=None):
    return User(**patch('users/@me', {'username': username, 'avatar': avatar}).json())


def get_current_user_guilds():  # Change to Guild() when finished
    return get('/users/@me/guilds').json()


def leave_guild(id_):
    return delete(f'/users/@me/guilds/{id_}').json()


def create_dm(id_):
    dm_channel = post(
        f'/users/@me/channels', {'recipient_id': id_}).json()
    return dm_channel


def create_group_dm(id_, acc_token: list, nicks: dict):
    group_channel = post(
        f'/users/@me/channels', {'access_tokens': acc_token, 'nicks': nicks})
    return group_channel


def get_user_connections():
    return get('/users/@me/connections')


def activity_type_converter(act):
    if isinstance(act, Activity):
        return {
            0: f"Playing {act.name}",
            1: f"Streaming {act.details}",
            2: f"Listening to {act.name}",
            3: f"Watching {act.name}",
            4: f"{act.emoji} {act.name}",
            5: f"Competing in {act.name}"
        }[act.type]
    else:
        return {
            0: "Game",
            1: "Streaming",
            2: "Listening",
            3: "Watching",
            4: "Custom",
            5: "Competing"
        }[act]


def get_channel(channel_id=None):
    return Channel(**get(f"/channels/{channel_id}").json())

# From https://github.com/eunwoo1104/dico - dico/model/gateway.py


class FlagBase:
    def __init__(self, *args, **kwargs):
        self.values = {x: getattr(self, x) for x in dir(
            self) if isinstance(getattr(self, x), int)}
        self.value = 0
        for x in args:
            if x.upper() not in self.values:
                raise AttributeError(f"invalid name: `{x}`")
            self.value |= self.values[x.upper()]
        for k, v in kwargs.items():
            if k.upper() not in self.values:
                raise AttributeError(f"invalid name: `{k}`")
            if v:
                self.value |= self.values[k.upper()]

    def __int__(self):
        return self.value

    def __getattr__(self, item):
        return self.has(item)

    def has(self, name: str):
        if name.upper() not in self.values:
            raise AttributeError(f"invalid name: `{name}`")
        return (self.value & self.values[name.upper()]) == self.values[name.upper()]

    def __setattr__(self, key, value):
        orig = key
        key = key.upper()
        if orig in ["value", "values"] or key not in self.values.keys():
            return super().__setattr__(orig, value)
        if not isinstance(value, bool):
            raise TypeError(f"only type `bool` is supported.")
        has_value = self.has(key)
        if value and not has_value:
            self.value |= self.values[key]
        elif not value and has_value:
            self.value &= ~self.values[key]

    def add(self, value):
        return self.__setattr(value, True)

    def remove(self, value):
        return self.__setattr(value, False)

    @classmethod
    def from_value(cls, value: int):
        ret = cls()
        ret.value = value
        return ret


class Intents(FlagBase):
    GUILDS = 1 << 0
    GUILD_MEMBERS = 1 << 1
    GUILD_BANS = 1 << 2
    GUILD_EMOJIS = 1 << 3
    GUILD_INTEGRATIONS = 1 << 4
    GUILD_WEBHOOKS = 1 << 5
    GUILD_INVITES = 1 << 6
    GUILD_VOICE_STATES = 1 << 7
    GUILD_PRESENCES = 1 << 8
    GUILD_MESSAGES = 1 << 9
    GUILD_MESSAGE_REACTIONS = 1 << 10
    GUILD_MESSAGE_TYPING = 1 << 11
    DIRECT_MESSAGES = 1 << 12
    DIRECT_MESSAGE_REACTIONS = 1 << 13
    DIRECT_MESSAGE_TYPING = 1 << 14

    @classmethod
    def full(cls):
        return cls(*[x for x in dir(cls) if isinstance(getattr(cls, x), int)])

    @classmethod
    def no_privileged(cls):
        ret = cls.full()
        ret.guild_presences = False
        ret.guild_members = False
        return ret


class Opcodes:
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    PRESENCE_UPDATE = 3
    VOICE_STATE_UPDATE = 4
    RESUME = 6
    RECONNECT = 7
    REQUEST_GUILD_MEMBERS = 8
    INVALID_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11

    @staticmethod
    def as_string(code: int):
        opcodes = {0: "Dispatch",
                   1: "Heartbeat",
                   2: "Identify",
                   3: "Presence Update",
                   4: "Voice State Update",
                   6: "Resume",
                   7: "Reconnect",
                   8: "Request Guild Members",
                   9: "Invalid Session",
                   10: "Hello",
                   11: "Heartbeat ACK"}
        return opcodes.get(code)


def ensure_coro(func):
    async def wrap(*args, **kwargs):
        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    return wrap


class SessionStartLimit:
    def __init__(self, resp: dict):
        self.total = resp["total"]
        self.remaining = resp["remaining"]
        self.reset_after = resp["reset_after"]
        self.max_concurrency = resp["max_concurrency"]

    @classmethod
    def optional(cls, resp: dict):
        if resp:
            return cls(resp)

    def to_dict(self):
        return {"total": self.total, "remaining": self.remaining, "reset_after": self.reset_after, "max_concurrency": self.max_concurrency}


class GetGateway:
    def __init__(self, resp: dict):
        self.url: str = resp["url"]
        self.shards: typing.Optional[int] = resp.get("shards", 0)
        self.session_start_limit: typing.Optional[SessionStartLimit] = SessionStartLimit.optional(
            resp.get("session_start_limit"))

    def to_dict(self):
        return {"url": self.url, "shards": self.shards, "session_start_limit": self.session_start_limit}


class GatewayResponse:
    def __init__(self, resp: dict):
        self.raw = resp
        self.op = resp["op"]
        self.d = resp.get("d", {})
        self.s = resp.get("s")
        self.t = resp.get("t")

    def to_dict(self):
        return {"op": self.op, "d": self.d, "s": self.s, "t": self.t}


class EventHandler:
    def __init__(self, client):
        self.events = {}
        self.client = client

    def add(self, event, func):
        if event not in self.events:
            self.events[event] = []

        self.events[event].append(ensure_coro(func))

    def get(self, event) -> list:
        return self.events.get(event, [])

    def process_response(self, name, resp):
        model_dict = {
            "INTERACTION_CREATE": Interaction
        }
        if name in model_dict:
            ret = model_dict[name].create(self.client, resp)
        else:
            ret = resp
        return ret

    def dispatch_from_raw(self, name, resp):
        ret = self.process_response(name, resp)
        if hasattr(ret, "_dont_dispatch") and ret._dont_dispatch:
            return
        self.client.dispatch(name, ret)
