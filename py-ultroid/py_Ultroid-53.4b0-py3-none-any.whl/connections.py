# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import os
import time
from logging import INFO, FileHandler, StreamHandler, basicConfig, getLogger

import redis
from pyrogram import Client
from pytgcalls import PyTgCalls
from telethon import TelegramClient
from telethon import __version__ as vers
from telethon.sessions import StringSession

from .dB.database import Var
from .version import __version__ as ver
from .version import ultroid_version

LOGS = getLogger("pyUltroid")

if os.path.exists("ultroid.log"):
    try:
        os.remove("ultroid.log")
    except BaseException:
        pass

basicConfig(
    format="%(asctime)s || %(name)s [%(levelname)s] - %(message)s",
    level=INFO,
    datefmt="%m/%d/%Y, %H:%M:%S",
    handlers=[FileHandler("ultroid.log"), StreamHandler()],
)

LOGS.info(
    """
                -----------------------------------
                        Starting Deployment
                -----------------------------------
"""
)
LOGS.info(f"py-Ultroid Version - {ver}")
LOGS.info(f"Telethon Version - {vers}")
LOGS.info(f"Ultroid Version - {ultroid_version}")


def connect_redis():
    if Var.REDIS_URI and Var.REDIS_PASSWORD:
        err = ""
        if ":" not in Var.REDIS_URI:
            err += "\nWrong REDIS_URI. Quitting...\n"
        if "/" in Var.REDIS_URI:
            err += "Your REDIS_URI should start with redis.xxx. Quitting...\n"
        if err != "":
            LOGS.info(err)
            exit(1)
        redis_info = Var.REDIS_URI.strip().split(":")
        LOGS.info("Getting Connection With Redis Database")
        time.sleep(3.5)
        return redis.Redis(
            host=redis_info[0],
            port=redis_info[1],
            password=Var.REDIS_PASSWORD.strip(),
            decode_responses=True,
        )
    else:
        LOGS.info("Getting Connection With Redis Database")
        time.sleep(3.5)
        return connect_qovery_redis()


def redis_connection():
    our_db = connect_redis()
    time.sleep(5)
    try:
        our_db.ping()
    except BaseException:
        connected = []
        LOGS.info("Can't connect to Redis Database.... Restarting....")
        for x in range(1, 6):
            try:
                our_db = connect_redis()
                time.sleep(3)
                if our_db.ping():
                    connected.append(1)
                    break
            except BaseException as conn:
                LOGS.info(
                    f"{(conn)}\nConnection Failed ...  Trying To Reconnect {x}/5 .."
                )
        if not connected:
            LOGS.info("Redis Connection Failed.....")
            exit(1)
        else:
            LOGS.info("Reconnected To Redis Server Succesfully")
    LOGS.info("Succesfully Established Connection With Redis DataBase.")
    return our_db


def session_file():
    if os.path.exists("client-session.session"):
        _session = "client-session"
    elif Var.SESSION:
        _session = StringSession(Var.SESSION)
    else:
        LOGS.info("No String Session found. Quitting...")
        exit(1)
    return _session


def client_connection(String=None, only_user=False):
    if not String:
        String = session_file()
    client = TelegramClient(String, Var.API_ID, Var.API_HASH)
    if only_user:
        return client
    bot_client = TelegramClient(None, api_id=Var.API_ID, api_hash=Var.API_HASH)
    return client, bot_client


def vc_connection(udB):
    VC_SESSION = udB.get("VC_SESSION") or Var.VC_SESSION
    if VC_SESSION:
        try:
            vcasst = Client(
                ":memory:",
                api_id=Var.API_ID,
                api_hash=Var.API_HASH,
                bot_token=udB.get("BOT_TOKEN"),
            )
            vcClient = Client(VC_SESSION, api_id=Var.API_ID, api_hash=Var.API_HASH)
            CallsClient = PyTgCalls(vcClient)
            return vcasst, vcClient, CallsClient
        except Exception as er:
            LOGS.info(str(er))
    return None, None, None


def connect_qovery_redis():
    uri = Var.REDIS_URI
    passw = Var.REDIS_PASSWORD
    if uri is None and passw is None:
        var = ""
        for i in os.environ:
            if i.startswith("QOVERY_REDIS_") and i.endswith("_PORT"):
                var = i
        if var:
            try:
                hash = var.split("QOVERY_REDIS_")[1].split("_")[0]
                # or config(f"QOVERY_REDIS_{hash}_HOST")
                endpoint = os.environ[f"QOVERY_REDIS_{hash}_HOST"]
                # or config(f"QOVERY_REDIS_{hash}_PORT")
                port = os.environ[f"QOVERY_REDIS_{hash}_PORT"]
                # or config(f"QOVERY_REDIS_{hash}_PASSWORD")
                passw = os.environ[f"QOVERY_REDIS_{hash}_PASSWORD"]
            except KeyError:
                LOGS.info("Redis Vars are missing. Quitting.")
                exit(1)
            except Exception as er:
                LOGS.info(er)
                exit(1)
            # uri = endpoint + ":" + str(port)
    return redis.Redis(
        host=endpoint,
        port=str(port),
        password=passw,
        decode_responses=True,
    )
    # return uri, passw
