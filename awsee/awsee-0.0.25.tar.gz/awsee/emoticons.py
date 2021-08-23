# coding=utf-8

import os

class Emoticons:
    ENABLED = True
    REPLACE = "->>"

    _PROMPT      = ['⛅','⛅']
    _WAITING     = ['💤💤💤','☕☕☕']
    _SEE_YA      = ['👋','✌']
    _ERROR       = ['❌💣','❌☠']
    _TOOL        = ['🔧','⚒']
    _THUMBS_UP   = ['👍','✔']
    _POINT_RIGHT = ['👉','❖']
    _WINK        = ['😉','☻']
    _OPS         = ['😕','☹']
    _PIN         = ['📌','✎']
    _ENV         = ['📝','✍']
    _TIME        = ['🕘','☕']
    _WAIT_DISTR  = ['🍺','♨']
    _WAIT_DISTR2 = ['🍼','⚾']
    _MAGNIFIER   = ['🔍','☌']
    _BLOCKS      = ['📦','❒']
    _REDMARK     = ['🔴','⚫']
    _UPLOAD      = ['📤','✈']
    _UPLOAD_PART = ['🔹','➩']
    _FOLDER      = ['🔹','➩']
    _OK          = ['✅','✅']
    _COOKIE      = ['🍪','⚫']
    _IMGS        = [
                     ['🕒','🕓','🕔','🕕','🕖','🕗','🕘','🕙','🕚','🕛','🕐','🕑'],
                     ['☰','☱','☲','☴','☵','☶','☷','☶','☴']
                   ]

    @staticmethod
    def isWindows():
        return 1 if os.name == "nt" else 0

    @staticmethod
    def cookie():
        return Emoticons._COOKIE[Emoticons.isWindows()] if Emoticons.ENABLED else Emoticons.REPLACE
    @staticmethod
    def prompt():
        return Emoticons._PROMPT[Emoticons.isWindows()] if Emoticons.ENABLED else Emoticons.REPLACE
    @staticmethod
    def waiting():
        return Emoticons._WAITING[Emoticons.isWindows()] if Emoticons.ENABLED else Emoticons.REPLACE
    @staticmethod
    def seeYa():
        return Emoticons._SEE_YA[Emoticons.isWindows()] if Emoticons.ENABLED else Emoticons.REPLACE
    @staticmethod
    def folder():
        return Emoticons._FOLDER[Emoticons.isWindows()] if Emoticons.ENABLED else Emoticons.REPLACE
    @staticmethod
    def error():
        return Emoticons._ERROR[Emoticons.isWindows()] if Emoticons.ENABLED else Emoticons.REPLACE
    @staticmethod
    def tool():
        return Emoticons._TOOL[Emoticons.isWindows()] if Emoticons.ENABLED else Emoticons.REPLACE
    @staticmethod
    def thumbsUp():
        return Emoticons._THUMBS_UP[Emoticons.isWindows()] if Emoticons.ENABLED else Emoticons.REPLACE
    @staticmethod
    def pointRight():
        return Emoticons._POINT_RIGHT[Emoticons.isWindows()] if Emoticons.ENABLED else Emoticons.REPLACE
    @staticmethod
    def wink():
        return Emoticons._WINK[Emoticons.isWindows()] if Emoticons.ENABLED else Emoticons.REPLACE
    @staticmethod
    def pin():
        return Emoticons._PIN[Emoticons.isWindows()] if Emoticons.ENABLED else Emoticons.REPLACE
    @staticmethod
    def env():
        return Emoticons._ENV[Emoticons.isWindows()] if Emoticons.ENABLED else Emoticons.REPLACE
    @staticmethod
    def time():
        return Emoticons._TIME[Emoticons.isWindows()] if Emoticons.ENABLED else Emoticons.REPLACE
    @staticmethod
    def waitDistract():
        return Emoticons._WAIT_DISTR[Emoticons.isWindows()] if Emoticons.ENABLED else Emoticons.REPLACE
    @staticmethod
    def waitDistract2():
        return Emoticons._WAIT_DISTR2[Emoticons.isWindows()] if Emoticons.ENABLED else Emoticons.REPLACE
    @staticmethod
    def ops():
        return Emoticons._OPS[Emoticons.isWindows()] if Emoticons.ENABLED else Emoticons.REPLACE
    @staticmethod
    def magnifier():
        return Emoticons._MAGNIFIER[Emoticons.isWindows()] if Emoticons.ENABLED else Emoticons.REPLACE
    @staticmethod
    def ok():
        return Emoticons._OK[Emoticons.isWindows()] if Emoticons.ENABLED else Emoticons.REPLACE
    @staticmethod
    def redMark():
        return Emoticons._REDMARK[Emoticons.isWindows()] if Emoticons.ENABLED else Emoticons.REPLACE