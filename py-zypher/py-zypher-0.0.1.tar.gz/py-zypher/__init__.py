from requests import get
import pylast
import asyncio
from distutils.util import strtobool as sb
from logging import basicConfig, getLogger, INFO, DEBUG
import os
import sys
from telethon.sessions import StringSession
from py-zypher import TelegramClient
from py-zypher.ZConfig import Var
import time

if Var.STRING_SESSION:
  session_name = str(Var.STRING_SESSION)
  zypherr = TelegramClient(StringSession(session_name), Var.APP_ID, Var.API_HASH)
else:
  session_name = "startup"
  zypherr = TelegramClient(session_name, Var.APP_ID, Var.API_HASH)
  
#STUFFS
StartTime = time.time()
zypherver = "0.0.1"

CMD_LIST = {}
CMD_HELP = {}
INT_PLUG = ""
LOAD_PLUG = {}
CMD_HNDLR = Var.CMD_HNDLR


ENV = os.environ.get("ENV", False)
