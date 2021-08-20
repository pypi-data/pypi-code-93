# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import multiprocessing
import traceback

from pyrogram import idle
from telethon.errors.rpcerrorlist import (
    AccessTokenExpiredError,
    ApiIdInvalidError,
    AuthKeyDuplicatedError,
    PhoneNumberInvalidError,
)

from . import *
from .dB.database import Var
from .funcs import autobot, autopilot, customize, plug, ready, startup_stuff
from .loader import plugin_loader

startup_stuff()

if not udB.get("BOT_TOKEN"):
    ultroid_bot.loop.run_until_complete(autobot())


async def istart():
    ultroid_bot.me = await ultroid_bot.get_me()
    ultroid_bot.uid = ultroid_bot.me.id
    ultroid_bot.first_name = ultroid_bot.me.first_name
    if not ultroid_bot.me.bot:
        udB.set("OWNER_ID", ultroid_bot.uid)


async def bot_info():
    asst.me = await asst.get_me()
    return asst.me


LOGS.info("Initialising...")


# log in
BOT_TOKEN = udB.get("BOT_TOKEN")
LOGS.info("Starting Ultroid...")
try:
    asst.start(bot_token=BOT_TOKEN)
    ultroid_bot.start()
    ultroid_bot.loop.run_until_complete(istart())
    ultroid_bot.loop.run_until_complete(bot_info())
    LOGS.info("Done, startup completed")
    LOGS.info("Assistant - Started")
except (AuthKeyDuplicatedError, PhoneNumberInvalidError, EOFError):
    LOGS.info("Session String expired. Please create a new one! Ultroid is stopping...")
    exit(1)
except ApiIdInvalidError:
    LOGS.info("Your API ID/API HASH combination is invalid. Kindly recheck.")
    exit(1)
except AccessTokenExpiredError:
    udB.delete("BOT_TOKEN")
    LOGS.info(
        "BOT_TOKEN expired , So Quitted The Process, Restart Again To create A new Bot. Or Set BOT_TOKEN env In Vars"
    )
    exit(1)
except BaseException:
    LOGS.info("Error: " + str(traceback.print_exc()))
    exit(1)


ultroid_bot.loop.run_until_complete(autopilot())

pmbot = udB.get("PMBOT")
manager = udB.get("MANAGER")
addons = udB.get("ADDONS") or Var.ADDONS
vcbot = udB.get("VC_SESSION") or Var.VC_SESSION

plugin_loader(addons=addons, pmbot=pmbot, manager=manager, vcbot=vcbot)


def pycli():
    vcasst.start()
    multiprocessing.Process(target=idle).start()
    CallsClient.run()


suc_msg = """
            ----------------------------------------------------------------------
                Ultroid has been deployed! Visit @TheUltroid for updates!!
            ----------------------------------------------------------------------
"""
# for channel plugins
plugin_channels = udB.get("PLUGIN_CHANNEL")

# for buddy
Hosted_in_buddy = os.getenv("BUDDY")
if bool(Hosted_in_buddy):
    aplogger = logging.getLogger("BUDDY WORKS")
    logging.getLogger("apscheduler").setLevel(logging.CRITICAL)

    def fumkoff():
        aplogger.info("Alive!")

    try:
        from apscheduler.schedulers.background import BackgroundScheduler

        sc = BackgroundScheduler()
        sc.daemonic = False
        sc.start()
        sc.add_job(fumkoff, "interval", seconds=500)
    except ImportError:
        aplogger.info("Buddy Wont stay alive!\nPlease install APScheduler!")


ultroid_bot.loop.run_until_complete(customize())
if plugin_channels:
    ultroid_bot.loop.run_until_complete(plug(plugin_channels))
ultroid_bot.loop.run_until_complete(ready())


if __name__ == "__main__":
    if vcbot:
        if vcasst and vcClient and CallsClient:
            multiprocessing.Process(target=pycli).start()
        LOGS.info(suc_msg)
        multiprocessing.Process(target=ultroid_bot.run_until_disconnected).start()
    else:
        LOGS.info(suc_msg)
        ultroid_bot.run_until_disconnected()
