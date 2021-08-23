import json, datetime, os
import clipboard
import pytz
from io import StringIO
from datetime import timezone
from dateutil import tz
from os import stat
from pygments import highlight, lexers, formatters
from awsee.style import Style
from awsee.general import *


class Utils:
    
    @staticmethod
    def time_to_expire(expDate):
        result = {}

        total_seconds = (expDate - datetime.datetime.now(timezone.utc)).seconds
        total_minutes = total_seconds / 60
        total_hours   = total_minutes / 60

        result["total_seconds"] = total_seconds
        result["total_minutes"] = total_minutes
        result["total_hours"]   = total_hours

        hours   = total_minutes / 60
        minutes = ((total_minutes / 60) - int(hours)) * 60
        seconds = ((((total_minutes / 60) - int(hours)) * 60) -  int(minutes)) * 60
        hours   = int(hours)
        minutes = int(minutes)
        seconds = int(seconds)
        result["HH:MM:SS"] = f"{hours:02.0f}h:{minutes:02.0f}m:{seconds:02.0f}s"

        return result
    
    @staticmethod
    def label_time_to_expire(expDate, format="min"):
        time_to_expire = Utils.time_to_expire(expDate, format)


    @staticmethod
    def formatPrettyJson(dictResult):
        jsonResult = Utils.dictToJson(dictResult)
        colorful_json = highlight(jsonResult, lexers.JsonLexer(), formatters.TerminalFormatter())
        return colorful_json
    
    @staticmethod 
    def dictToJson(response, sortKeys=False):
        strObj = StringIO()
        json.dump(response, strObj, default=str, indent=4, sort_keys=sortKeys)
        return strObj.getvalue()
    
    @staticmethod 
    def cleanBreakLines(text):
        if isinstance(text, str):
           text = text.replace("\n","")
           return text
        return text
    
    @staticmethod
    def addToClipboard(text):
        try:
            textNoColor = Utils.removeCharsColors(text)
            if textNoColor:
               clipboard.copy(textNoColor.strip())
        except:
            pass
    
    @staticmethod
    def isRunningOnGitBash():
        try:
            # Probably on a GitBash environment (Windows)
            os.environ["SHELL"]
            return True
        except:
            return False

    @staticmethod
    def isWindows():
        return 1 if os.name == "nt" else 0
    
    @staticmethod
    def parseUTCDateToLocalZoneDate(utc_date):
        #utc_date       = datetime.datetime.strptime(string_date, "%Y-%m-%d %H:%M:%S+00:00")
        local_timezone = tz.tzlocal() 
        local_datetime = utc_date.replace(tzinfo=pytz.utc)
        local_datetime = local_datetime.astimezone(local_timezone)
        return local_datetime
        

    @staticmethod
    def isNumber(s):
        try:
            int(s)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def removeCharsColors(text):
        if isinstance(text, str):
           text = text.replace(Style.UNDERLINE,"") \
                      .replace(Style.RESET,"") \
                      .replace(Style.BLACK,"") \
                      .replace(Style.RED,"") \
                      .replace(Style.GREEN,"") \
                      .replace(Style.YELLOW,"") \
                      .replace(Style.BLUE,"") \
                      .replace(Style.MAGENTA,"") \
                      .replace(Style.CYAN,"") \
                      .replace(Style.WHITE,"") \
                      .replace(Style.BBLACK,"") \
                      .replace(Style.BRED,"") \
                      .replace(Style.BGREEN,"") \
                      .replace(Style.BYELLOW,"") \
                      .replace(Style.BBLUE,"") \
                      .replace(Style.BMAGENTA,"") \
                      .replace(Style.BCYAN,"") \
                      .replace(Style.BWHITE,"") \
                      .replace(Style.BG_BLACK,"") \
                      .replace(Style.BG_RED,"") \
                      .replace(Style.BG_GREEN,"") \
                      .replace(Style.BG_YELLOW,"") \
                      .replace(Style.BG_BLUE,"") \
                      .replace(Style.BG_PURPLE,"") \
                      .replace(Style.BG_CYAN,"") \
                      .replace(Style.BG_WHITE,"") \
                      .replace(Style.IBLACK,"") \
                      .replace(Style.IRED,"") \
                      .replace(Style.IGREEN,"") \
                      .replace(Style.IYELLOW,"") \
                      .replace(Style.IBLUE,"") \
                      .replace(Style.IMAGENTA,"") \
                      .replace(Style.ICYAN,"") \
                      .replace(Style.IWHITE,"") \
                      .replace(Style.BIBLACK,"") \
                      .replace(Style.BIRED,"") \
                      .replace(Style.BIGREEN,"") \
                      .replace(Style.BIYELLOW,"") \
                      .replace(Style.BIBLUE,"") \
                      .replace(Style.BIPURPLE,"") \
                      .replace(Style.BICYAN,"") \
                      .replace(Style.BIWHITE,"") \
                      .replace(Style.On_IBLACK,"") \
                      .replace(Style.On_IRED,"") \
                      .replace(Style.On_IGREEN,"") \
                      .replace(Style.On_IYELLOW,"") \
                      .replace(Style.On_IBLUE,"") \
                      .replace(Style.On_IPURPLE,"") \
                      .replace(Style.On_ICYAN,"") \
                      .replace(Style.On_IWHITE,"")
        return text
