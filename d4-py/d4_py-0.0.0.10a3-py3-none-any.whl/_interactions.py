import aiohttp
from ._d4 import *
import typing
import asyncio
from ._utils import *
import time
import sys
import traceback
from ._exception import *
import json
from ._cmd import *
from ._models import *

v9_url = 'https://discord.com/api/v9'


def Log(message=None):
    if printLog:
        print(message)
    else:
        pass


class AsyncHTTPRequest:
    def __init__(self,
                 token: str,
                 loop: asyncio.AbstractEventLoop = None,
                 session: aiohttp.ClientSession = None,
                 retry_default=3):
        self.loop = loop or asyncio.get_event_loop()
        self.token = token
        self.session = session or aiohttp.ClientSession(loop=self.loop)
        self.retry_default = retry_default
        self._closed = False

    async def close(self):
        await self.session.close()
        self._closed = True

    async def request(self, route: str, meth: str, body: typing.Any = None, *, is_json: bool = False, reason_header: str = None, retry: int = None, **kwargs) -> dict:
        code = 429  # Empty code in case of rate limit fail.
        resp = {}   # Empty resp in case of rate limit fail.
        retry = (retry if retry >
                 0 else 1) if retry is not None else self.default_retry
        for x in range(retry):
            code, resp = await self._request(route, meth, body, is_json, reason_header, **kwargs)
            if 200 <= code < 300:
                return resp
            elif code == 400:
                raise BadRequest(route, code, resp)
            elif code == 403:
                raise Forbidden(route, code, resp)
            elif code == 404:
                raise NotFound(route, code, resp)
            elif code == 429:
                wait_sec = resp["retry_after"]
                await asyncio.sleep(wait_sec)
                continue
            elif 500 <= code < 600:
                raise DiscordError(code)
            else:
                raise Unknown(code)
        raise RateLimited(route, code, resp)

    async def _request(self, route: str, meth: str, body: typing.Any = None, is_json: bool = False, reason_header: str = None, **kwargs) -> typing.Tuple[int, dict]:
        headers = {"Authorization": f"Bot {self.token}"}
        if meth not in ["GET"] and body is not None:
            if is_json:
                headers["Content-Type"] = "application/json"
                body = json.dumps(body)
            kwargs["data"] = body
        if reason_header is not None:
            headers["X-Audit-Log-Reason"] = reason_header
        async with self.session.request(meth, self.BASE_URL+route, headers=headers, **kwargs) as resp:
            return resp.status, await resp.json() if resp.status != 204 else None


class WSClosing(Exception):
    # def __init__(self, code):
    #     self.code = code
    pass


async def safe_call(coro, additional_message: typing.Optional[str] = None):
    """
    Calls coroutine, ignoring raised exception and only print traceback.
    This is used for event listener call, and intended to be used at creating task.
    :param coro: Coroutine to safely call
    :param additional_message: Additional traceback message to print at the top.
    """

    try:
        await coro
    except Exception as ex:
        tb = traceback.format_exc()
        if additional_message:
            _p = additional_message + "\n" + tb
        else:
            _p = tb
        print(_p, file=sys.stderr)


def dispatch(self, name, *args):
    """
    Dispatches new event.
    :param name: Name of the event.
    :param args: Arguments of the event.
    """
    [self.loop.create_task(safe_call(x(*args)))
     for x in self.events.get(name.upper())]
    # [self.__wait_futures[name.upper()].pop(x).set_result(args) for x in range(len(self.__wait_futures.get(name.upper(), [])))]
    for x in range(len(self.__wait_futures.get(name.upper(), []))):
        fut: asyncio.Future = self.__wait_futures[name.upper()].pop(x)
        if not fut.cancelled():
            fut.set_result(args)


def dispatch_from_raw(self, name, resp):
    ret = self.process_response(name, resp)
    if hasattr(ret, "_dont_dispatch") and ret._dont_dispatch:
        return
    self.client.dispatch(name, ret)


class WebSocketClient:
    def __init__(self, token, intents: typing.Union[Intents, int] = None, ws: aiohttp.ClientWebSocketResponse = None,):
        self.http = AsyncHTTPRequest
        self.ws = ws or aiohttp.ClientWebSocketResponse
        self.base_url: str = ""
        self.intents = intents or typing.Union[Intents, int]
        self.session = aiohttp.ClientSession
        self.heartbeat_interval: int
        self._closed = False
        self.last_heartbeat_send = 0
        self.last_heartbeat_ack = 0
        self._reconnecting = False
        self._fresh_reconnecting = False
        self._heartbeat_task = None
        self.session_id = None
        self.seq = None
        self._ping_start = 0.0
        self.token = token
        self.ping = 0.0

    async def close(self, code: int = 1000):
        if self._closed:
            return
        Log(self.ws)
        await self.ws.close(code=code)
        self._closed = True

    async def reconnect(self, fresh: bool = False):
        if self._reconnecting or self._fresh_reconnecting:
            return
        self._reconnecting = not fresh
        self._fresh_reconnecting = fresh
        if not self._closed:
            await self.close(4000)

    async def identify(self):
        data = {
            "op": Opcodes.IDENTIFY,
            "d": {
                "token": self.token,
                "intents": int(self.intents),
                "properties": {
                    "$os": sys.platform,
                    "$browser": "d4-buttons-dico",
                    "$device": "d4-buttons-dico"
                }
            }
        }
        await self.ws.send_json(data)

    async def resume(self):
        data = {
            "op": Opcodes.RESUME,
            "d": {
                "token": self.token,
                "session_id": self.session_id,
                "seq": self.seq
            }
        }

    async def send_heartbeat(self):
        while not self._closed:
            if not self.last_heartbeat_send <= self.last_heartbeat_ack <= time.time():
                await self.reconnect()
                break
            data = {"op": Opcodes.HEARTBEAT, "d": self.seq}
            self._ping_start = time.time()
            await self.ws.send_json(data)
            self.last_heartbeat_send = time.time()
            await asyncio.sleep(self.heartbeat_interval/1000)

    async def connect(self):
        while True:
            while not self._closed:
                try:
                    ws = await self.receive()
                    res = ws.json()
                    Log(res)
                except WSClosing as ex:
                    # res = await ws.receive()
                    # res = res.json()
                    # print(res)
                    # if res["s"]:
                    #     self.seq = res["s"]

                    # if res["op"] == Opcodes.HELLO:
                    #     print("OPCODE HELLO RECEIVED")
                    #     self.ws = res
                    #     self.heartbeat_interval = res["d"]["heartbeat_interval"]
                    #     self._heartbeat_task = asyncio.get_event_loop().create_task(
                    #         self.send_heartbeat(ws, self.heartbeat_interval))
                    #     if self._reconnecting:
                    #         await self.resume()
                    #     else:
                    #         await self.identify()
                    #     if self._fresh_reconnecting:
                    #         self._fresh_reconnecting = False
                    # elif res["op"] == Opcodes.DISPATCH:
                    #     if res["t"] == "READY":
                    #         self.session_id = res["d"]["session_id"]
                    #         # dispatch
                    # elif res["op"] == Opcodes.HEARTBEAT_ACK:
                    #     self.last_heartbeat_ack = time.time()
                    #     self.ping = self.last_heartbeat_ack - self._ping_start

                    # elif res["op"] == Opcodes.INVALID_SESSION:
                    #     await asyncio.sleep(5)
                    #     await self.reconnect(fresh=True)
                    #     break

                    # elif res["op"] == Opcodes.RECONNECT:
                    #     await self.reconnect()
                    #     break
                    Log("Websocket is closing with code:" + {ex.code})
                    if ex.code is None and self.try_reconnect:
                        Log("Trying to reconnect...")
                        await self.reconnect(fresh=True)
                    break
                a = Opcodes.as_string(res["op"])
                b = ' with event name `' + (res["t"] if res["t"] else "None")
                c = res["op"]
                d = res["t"]
                e = f"Received {a} payload" f"{f' with event name {d}' if res['op'] == Opcodes.DISPATCH else ''}."
                Log(e)

                if res["s"]:
                    self.seq = res["s"]

                if res["op"] == Opcodes.DISPATCH:
                    global event_dict
                    global command_dict
                    if res["t"] == "READY":
                        self.session_id = res["d"].get(
                            "session_id", self.session_id)
                        if "ON_READY".lower() in event_dict.keys():
                            func = event_dict["on_ready"]
                            await func()
                    elif res["t"] == "INTERACTION_CREATE":
                        if "INTERACTION_CREATE".lower() in event_dict.keys():
                            func = event_dict["interaction_create"]
                            e = Interaction(**res["d"])
                            await func(e)  # TODO: call function with info
                    elif res["t"] == "MESSAGE_CREATE":
                        if "MESSAGE_CREATE".lower() in event_dict.keys():
                            func = event_dict["message_create"]
                            e = Message(**res["d"])
                            await func(e)
                        else:
                            e = Message(**res["d"])
                            for i in command_dict.keys():
                                if str(e.content) == i:
                                    func = command_dict[e.content]
                                    await func(e)
                                elif str(e.content).startswith(i + ' '):
                                    func = command_dict[i]
                                    await func(e)
                    else:
                        if res["t"].lower() in event_dict.keys():
                            func = event_dict[res["t"]]
                            await func(**res["d"])

                elif res["op"] == Opcodes.HELLO:
                    self.heartbeat_interval = res["d"]["heartbeat_interval"]
                    self._heartbeat_task = asyncio.get_event_loop().create_task(self.send_heartbeat())
                    if self._reconnecting:
                        await self.resume()
                    else:
                        await self.identify()
                    if self._fresh_reconnecting:
                        self._fresh_reconnecting = False

                elif res["op"] == Opcodes.HEARTBEAT_ACK:
                    self.last_heartbeat_ack = time.time()
                    self.ping = self.last_heartbeat_ack - self._ping_start

                elif res["op"] == Opcodes.INVALID_SESSION:
                    print(
                        "Failed utils resume, reconnecting to utils without resuming.")
                    await asyncio.sleep(5)
                    await self.reconnect(fresh=True)
                    break

                elif res["op"] == Opcodes.RECONNECT:
                    await self.reconnect()
                    break

            if self._reconnecting or self._fresh_reconnecting:
                self._closed = False
            else:
                return

    async def receive(self):
        res = await self.ws.receive()
        if res.type == aiohttp.WSMsgType.TEXT:
            self.seq = res.json()["s"]
            return res
        elif res.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSED):
            raise WSClosing(res.data)

    @classmethod
    async def raiseConnection(cls, tk, it):
        ws = await aiohttp.ClientSession().ws_connect(url="wss://gateway.discord.gg/?v=9&encoding=json")
        return cls(tk, intents=it, ws=ws)
