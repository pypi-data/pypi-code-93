import os
import telethon
import requests
from bot.config import Config
import asyncio
import re
import functools
from telethon.errors import BadRequestError
from telethon.tl.functions.channels import EditAdminRequest, EditBannedRequest
from telethon.tl.functions.messages import UpdatePinnedMessageRequest
from telethon.tl.types import ChatAdminRights,ChatBannedRights,MessageEntityMentionName
from telethon import TelegramClient, events, functions, Button

#==================================================

bot = TelegramClient("bot", api_id=Config.API_ID, api_hash=Config.API_HASH)
utilsbot = bot.start(bot_token=Config.BOT_TOKEN)

#==================================================
def callback(sed):
    def callbacks(func):
        data = sed
        utilsbot.add_event_handler(
            func, events.callbackquery.CallbackQuery(data=data)
        )

    return callbacks

def cmd(add_cmd, is_args=False):
    def acmd(func):
        if is_args :
        	pattern = "^/" + add_cmd + "(?: |$)(.*)"
        elif is_args== "simple" :
            pattern = "^/" + add_cmd + " ?(.*)"
        elif is_args== "simple2" :
            pattern = "^/" + add_cmd + " ?(.*) ?(.*)"
        elif is_args=="normal":
            pattern = "^/" + add_cmd
        elif is_args=="notes1":
            pattern = "^/" + add_cmd + "(\S+)"
        elif is_args=="unpin":
            pattern = "^/" + add_cmd + "($| (.*))"
        elif is_args=="blacklist":
            pattern = "^/" + add_cmd + "((.|\n)*)"
        else:
            pattern = "^/" + add_cmd + "$"
        utilsbot.add_event_handler(
            func, events.NewMessage(incoming=True, pattern=pattern)
        )
    return acmd

def inline():
    def ainline(func):
        utilsbot.add_event_handler(func, events.InlineQuery)
    return ainline

def is_admin():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(event):
            sed = await utilsbot.get_permissions(event.chat_id, event.sender_id)
            user = event.sender_id
            if sed.is_admin:
                await func(event)
            if not user:
                pass
            if not sed.is_admin:
                await event.reply("Only Admins Can Use it.")
        return wrapper
    return decorator

def can_restrict():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(event):
            sed = await utilsbot.get_permissions(event.chat_id, event.sender_id)
            user = event.sender_id
            if sed.ban_users:
                await func(event)
            if not user:
                pass
            if not sed.ban_users:
                await event.reply("You Dont Have Permissions to Restrict Users")
            if not sed.is_admin:
                await event.reply("Only Admins Can Use it.")
        return wrapper
    return decorator

def can_pin():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(event):
            sed = await utilsbot.get_permissions(event.chat_id, event.sender_id)
            user = event.sender_id
            if sed.pin_messages:
                await func(event)
            if not user:
                pass
            if not sed.pin_messages:
                await event.reply("You Dont Have Permissions to Pin Messages")
            if not sed.is_admin:
                await event.reply("Only Admins Can Use it.")
        return wrapper
    return decorator

def chat_creator():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(event):
            sed = await utilsbot.get_permissions(event.chat_id, event.sender_id)
            user = event.sender_id
            if sed.is_creator:
                await func(event)
            if not user:
                pass
            if not sed.is_creator:
                await event.reply("Only Chat Creators Can Execute this Command")
            if not sed.is_admin:
                await event.reply("Only Admins Can Use it.")
        return wrapper
    return decorator

def can_promote():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(event):
            sed = await utilsbot.get_permissions(event.chat_id, event.sender_id)
            user = event.sender_id
            if sed.add_admins:
                await func(event)
            if not user:
                pass
            if not sed.add_admins:
                await event.reply("You Dont Have Permissions to Promote/Demote")
            if not sed.is_admin:
                await event.reply("Only Admins Can Use it.")
        return wrapper
    return decorator

def change_info():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(event):
            sed = await utilsbot.get_permissions(event.chat_id, event.sender_id)
            user = event.sender_id
            if sed.change_info:
                await func(event)
            if not user:
                pass
            if not sed.change_info:
                await event.reply("You Dont Have Permissions to Change Info")
            if not sed.is_admin:
                await event.reply("Only Admins Can Use it.")
        return wrapper
    return decorator

def can_delete():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(event):
            sed = await utilsbot.get_permissions(event.chat_id, event.sender_id)
            user = event.sender_id
            if sed.delete_messages:
                await func(event)
            if not user:
                pass
            if not sed.delete_messages:
                await event.reply("You Dont Have Permissions to Delete Messages")
            if not sed.is_admin:
                await event.reply("Only Admins Can Use it.")
        return wrapper
    return decorator

def is_bot_admin():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(event):
            pep = await utilsbot.get_me()
            sed = await utilsbot.get_permissions(event.chat_id, pep)
            if sed.is_admin:
                await func(event)
            else:
                await event.reply("I Must Be Admin To Do This.")
        return wrapper
    return decorator

def only_groups():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(event):
            if event.is_group:
                await func(event)
            else:
                await event.reply("This Command Only Works On Groups.")
        return wrapper
    return decorator

def only_pm():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(event):
            if event.is_group:
                pass
            else:
                await func(event)
        return wrapper
    return decorator

def owner_only():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(event):
            owner = Var.OWNER_ID
            if event.sender_id == owner:
                await func(event)
            else:
                pass
        return wrapper
    return decorator

#==================================================
is_admin = is_admin()
is_bot_admin = is_bot_admin()
only_groups = only_groups()
only_pm = only_pm()
can_restrict = can_restrict()
can_pin = can_pin()
chat_creator = chat_creator()
can_promote = can_promote()
change_info = change_info()
can_delete = can_delete()
owner_only = owner_only()
# =================== CONSTANT ===================
