"""d4-py"""
"""Copyright 2021 ast.08. Check LICENSE for more details."""


import typing
import requests
import json
import aiohttp
import asyncio
import _exception
import _interactions
import traceback
import _cmd
from _models import *
from _utils import *
v9_url = 'https://discord.com/api/v9'
Token: str

global commandClass
global printLog
printLog: bool


class Client:
    def __init__(self, prefix=None, print_log=False):
        global printLog
        self.prefix = prefix or "!"
        printLog = print_log

    def EventListener(self, func):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Event must be a coroutine function")

        def decorator(*args, **kwargs):
            if func.__name__ == 'ready':
                _cmd.event_dict['on_ready'] = func
            elif func.__name__ == 'message':
                _cmd.event_dict['message_create'] = func
            elif func.__name__ == "interaction":
                _cmd.event_dict['interaction_create'] = func
            else:
                _cmd.event_dict[func.__name__.lower()] = func

        return decorator()

    def toClsCmd(self, name=None, aliases=None, slash=None, prefix=None, cls=None):
        if cls is None:
            cls = _cmd.Command

        def decorator(func):
            if isinstance(func, _cmd.Command):
                raise TypeError("Cannot register command: 'Already a command'")
            return cls(func, name=name, aliases=aliases, slash=slash, prefix=prefix)

        return decorator

    def cmd(self, *_args, name=None, aliases: list = [], slash=None, prefix=None, **__kwargs):  # decorator arugments
        ____name____ = name
        ____aliases____ = aliases
        ____slash____ = slash
        ____prefix____ = prefix

        def decorator(func):
            if ____prefix____ is None:
                pf = "!"
            else:
                pf = ____prefix____

            if ____name____ is None:
                name_ = pf + func.__name__
            else:
                name_ = pf + ____name____
            if ____aliases____ is None:
                aliases_: list = [].append(name_)
            else:
                aliases_ = []
                for i in ____aliases____:
                    aliases_.append(pf + i)
            res_cmd = self.toClsCmd(name_, aliases_, ____slash____,
                                    pf)(func)

            return _cmd.Command().add_command(res_cmd)
            # return func(*args, **kwargs)
        return decorator

    async def start(self, tk):
        intent: Intents = Intents.no_privileged()
        ws = await _interactions.WebSocketClient(token=tk, intents=intent).raiseConnection(tk, intent)
        try:
            await ws.connect()
        except KeyboardInterrupt:
            print("Exiting...")
        # except Exception:
        #     print("UNEXPECTED EXCEPTION OCCURED")
        #     traceback.print_exc()
        finally:
            await ws.close()
            await ws.http(tk).close()

    def login(self, token: str = None):
        global Token
        if token is None:
            raise SyntaxError.msg == "token is required"
        else:
            Token = token
            asyncio.get_event_loop().run_until_complete(self.start(tk=Token))


def Emoji(name: str = None, id: str = None, animated: bool = False):
    return {'name': name, 'id': id, 'animated': str(animated).lower()}


class Button:
    def __init__(self, style, text, emoji=None, url=None, customId=None, disabled: bool = False):
        self.style = style
        self.text = text
        self.emoji = emoji
        self.url = url
        self.customId = customId
        self.disabled = disabled

    async def send(self, ctx=None, content=None, id=None):
        headers = {"Authorization": f"Bot {Token}"}
        headers["Content-Type"] = "application/json"
        channel_id: str
        if ctx is None and id is None:
            raise TypeError(
                "Error: Code 10. Check out https://github.com/namuKR/d4-buttons/wiki#code-10 for more info.")
        elif ctx is not None and id is not None:
            channel_id = ctx.channel.id
        elif ctx is None and id is not None:
            channel_id = id
        elif ctx is not None and id is None:
            channel_id = ctx.channel.id

        if content is None:
            print(
                "Warning: Code 10. Check out https://github.com/namuKR/d4-buttons/wiki#code-10-1 for more info.")
            content = '​'  # zero width space inside it!

        if self.url is not None and self.customId is None and self.emoji is None:
            req_body = {
                "content": content,
                "tts": False,
                "components": [
                    {
                        "type": 1,
                        "components": [
                            {
                                "type": 2,
                                "label": self.text,
                                "style": 5,
                                "url": self.url,
                                "disabled": self.disabled if self.disabled else False
                            }
                        ]
                    }
                ]
            }
        elif self.url is not None and self.customId is None and self.emoji is not None:
            req_body = {
                "content": content,
                "tts": False,
                "components": [
                    {
                        "type": 1,
                        "components": [
                            {
                                "type": 2,
                                "label": self.text,
                                "style": 5,
                                "url": self.url,
                                "disabled": self.disabled if self.disabled else False,
                                "emoji": self.emoji
                            }
                        ]
                    }
                ]
            }
        elif self.emoji is not None:
            if self.customId is None:
                raise TypeError.msg == "Buttons that are not Link style must have customId values."
            elif self.style is None or self.text is None:
                raise TypeError.msg == "Button.style or Button.text missing"

            req_body = {
                "content": content,
                "tts": False,
                "components": [
                    {
                        "type": 1,
                        "components": [
                            {
                                "type": 2,
                                "label": self.text,
                                "style": self.style,
                                "emoji": self.emoji,
                                "custom_id": self.customId,
                                "disabled": self.disabled if self.disabled else False
                            }
                        ]
                    }
                ]
            }

        elif self.url is not None and self.customId is not None:
            raise TypeError.msg == "Link Buttons should not have customId values."
        elif self.url is None and self.customId is None:
            raise TypeError.msg == "Buttons that are not Link style must have customId values."
        elif self.style is None or self.text is None:
            raise TypeError.msg == "Button.style or Button.text missing"
        elif type(self.style) is not int:
            raise TypeError.msg == "Button.style is not int - button style must be int type."
        else:
            req_body = {
                "content": content,
                "tts": False,
                "components": [
                    {
                        "type": 1,
                        "components": [
                            {
                                "type": 2,
                                "label": self.text,
                                "style": self.style,
                                "custom_id": self.customId,
                                "disabled": self.disabled if self.disabled else False
                            }
                        ]
                    }
                ]
            }
        response = requests.post(
            v9_url + f"/channels/{channel_id}/messages", headers=headers, json=req_body)
        return response


chn: str
cntt = '​'


def queue(ctx=None, content=None, id=None):
    global chn, cntt
    id = str(id)
    if ctx is None and id is None:
        raise TypeError.msg == "Error: Code 10. Check out https://github.com/namuKR/d4-buttons/wiki#code-10 for more info."
    elif ctx is not None and id is not None:
        chn = ctx.channel.id
    elif ctx is None and id is not None:
        chn = id
    elif ctx is not None and id is None:
        chn = ctx.channel.id

    if content is None:
        print(
            "Warning: Code 10. Check out https://github.com/namuKR/d4-buttons/wiki#code-10-1 for more info.")
        content = '​'  # zero width space inside it!
    else:
        cntt = content


def send(*_buttons):
    global chn, cntt
    i = 0
    r = []
    for button in _buttons:
        i += 1
        if i > 5:
            raise SyntaxError.msg == "You can only request 5 buttons at a time."
        self = button
        headers = {"Authorization": f"Bot {Token}"}
        headers["Content-Type"] = "application/json"
        # channel_id: str
        # if ctx is None and id is None:
        #     raise TypeError.msg == "Error: Code 10. Check out https://github.com/namuKR/d4-buttons/wiki#code-10 for more info."
        # elif ctx is not None and id is not None:
        #     channel_id = ctx.channel.id
        # elif ctx is None and id is not None:
        #     channel_id = id
        # elif ctx is not None and id is None:
        #     channel_id = ctx.channel.id

        # if content is None:
        #     print(
        #         "Warning: Code 10. Check out https://github.com/namuKR/d4-buttons/wiki#code-10-1 for more info.")
        #     content = '​'  # zero width space inside it!

        if self.url is not None and self.customId is None and self.emoji is None:  # Link Button

            r.append({
                "type": 2,
                "label": self.text,
                "style": 5,
                "url": self.url,
                "disabled": self.disabled if self.disabled else False
            })

        elif self.url is not None and self.customId is None and self.emoji is not None:

            r.append({
                "type": 2,
                "label": self.text,
                "style": 5,
                "url": self.url,
                "disabled": self.disabled if self.disabled else False,
                "emoji": self.emoji
            })

        elif self.emoji is not None:
            if self.customId is None:
                raise TypeError.msg == "Buttons that are not Link style must have customId values."
            elif self.style is None or self.text is None:
                raise TypeError.msg == "Button.style or Button.text missing"

            r.append({
                "type": 2,
                "label": self.text,
                "style": self.style,
                "emoji": self.emoji,
                "custom_id": self.customId,
                "disabled": self.disabled if self.disabled else False
            })

        elif self.url is not None and self.customId is not None:
            raise TypeError.msg == "Link Buttons should not have customId values."
        elif self.url is None and self.customId is None:
            raise TypeError.msg == "Buttons that are not Link style must have customId values."
        elif self.style is None or self.text is None:
            raise TypeError.msg == "Button.style or Button.text missing"
        elif type(self.style) is not int:
            raise TypeError.msg == "Button.style is not int - button style must be int type."
        else:

            r.append({
                "type": 2,
                "label": self.text,
                "style": self.style,
                "custom_id": self.customId,
                "disabled": self.disabled if self.disabled else False
            })

    rq = []
    for v in range(i):
        rq.append(r[v])

    req_body: dict = {
        "content": cntt,
        "tts": False,
        "components": [
            {
                "type": 1,
                "components": [

                ]
            }
        ]

    }

    req_body["components"][0]["components"] = rq

    response = requests.post(
        v9_url + f"/channels/{chn}/messages", headers=headers, json=req_body)
    return response
