from awsee.style import Style
from awsee.emoticons import Emoticons
from awsee.preferences import Preferences
from awsee.utils import Utils
from awsee.general import *

class Messages:

    def __init__(self):
        pass

    @staticmethod
    def formatMessage(title,msg=None):
        emoticon = Emoticons.pointRight()
        output = ""
        #output  = Style.ICYAN + "=".ljust(len(title)+5,"=")
        output += f"\n{Style.IBLUE} {emoticon} {Style.IGREEN}{title}{Style.RESET}\n"
        #output += Style.ICYAN + "=".ljust(len(title)+5,"=")
        if msg:
           output += f"{Style.GREEN}{msg}"
        return output
    def showMessage(title,msg=None):
        output = Messages.formatMessage(title,msg)
        output = Utils.removeCharsColors(output) if Preferences().noColor else output
        printPy(output)
    
    @staticmethod
    def formatWarning(title,msg=None):
        emoticon = Emoticons.ops()
        output = ""
        #output  = Style.ICYAN + "=".ljust(len(title)+5,"=")
        output = f"\n{Style.IBLUE} {emoticon} {Style.IGREEN}{title}{Style.RESET}\n"
        #output += Style.ICYAN + "=".ljust(len(title)+5,"=")
        if msg:
           output += f"{Style.GREEN}{msg}"
        return output
    def showWarning(title,msg=None):
        output = Messages.formatWarning(title,msg)
        output = Utils.removeCharsColors(output) if Preferences().noColor else output
        printPy(output)

    def formatStartExecution(title,msg=None):
        emoticon = Emoticons.pointRight()
        output = ""
        output += f"{Style.IBLUE} {emoticon} {Style.IGREEN}{title}{Style.RESET}"
        if msg:
           output += f"{Style.GREEN}{msg}"
        return output
    def showStartExecution(title,msg=None):
        output = Messages.formatStartExecution(title,msg)
        output = Utils.removeCharsColors(output) if Preferences().noColor else output
        printPy(output, end='\r')
    
    @staticmethod
    def formatError(title,msg=None):
        emoticon = Emoticons.ops()
        output = ""
        output = f"\n{Style.IRED} {emoticon} {Style.IMAGENTA}{title}{Style.RESET}\n"
        if msg:
           output += f"    {Style.GREEN}{msg}"
        return output
    def showError(title,msg=None):
        output = Messages.formatError(title,msg)
        output = Utils.removeCharsColors(output) if Preferences().noColor else output
        printPy(output)
        printPy("")

