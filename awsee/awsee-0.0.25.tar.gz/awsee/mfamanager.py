
import re, uuid
from tinydb import Query, where
from arnparse import arnparse
from awsee.messages import Messages
from awsee.style import Style
from awsee.emoticons import Emoticons
from awsee.utils import Utils
from awsee.tableargs import TableArgs
from awsee.prettytable import PrettyTable
from awsee.repository import CredentialsRepository, MfaRepository
from awsee.general import *

class MFAManager:

    def __init__(self):
        self.credentialsRepository = CredentialsRepository()
        self.mfaRepository         = MfaRepository()

    def addMfa(self):
        Messages.showMessage("ADD MFA DEVICE TO PROFILE")
        index            = 0
        sizeSeparator    = 120
        sizeLabelProfile = 18
        output           = ""
        output           += Style.GREEN + "-".ljust(sizeSeparator,"-") + "\n"
        output           += f" {Style.IBLUE}MFA DEVICES:\n"
        profiles          = []
        for c in self.credentialsRepository.all():
            index += 1
            profiles.append(c['profile'])
            pn         = c['profile'] + " ".rjust(sizeLabelProfile -len(c['profile']), " ")
            account    = c['account']
            line       = f"  {Style.IBLUE}{index:02d} -->{Style.GREEN} {pn} {Style.IBLUE}Account..:{Style.GREEN} {account}"
            labelMfa   = "MFA Devices..: "
            mfaDevices = ""
            for idx, r in enumerate(self.mfaRepository.searchByQuery(where('profile') == c['profile'])):
                if len(mfaDevices) > 1:
                    mfaDevices += "\n" + " ".ljust(len(Utils.removeCharsColors(line)) + len(labelMfa) + 1," ")
                mfaDevices += f"{Style.BLUE}{idx+1:02d}{Style.GREEN}-{r['mfa-device']}"
            if len(mfaDevices) > 1:
                mfaDevices = f"{Style.IBLUE}{labelMfa}{Style.GREEN}{mfaDevices}{Style.GREEN}"
            output += line + f" {mfaDevices}\n"
        output += "-".ljust(sizeSeparator,"-")
        printPy(output)

        printPy(f"{Style.GREEN} {Emoticons.pin()} Choose a profile....:{Style.BLUE}", end=' ')
        result = input()
        if result == "":
           return None
           
        if not Utils.isNumber(result):
            Messages.showWarning(f"Invalid choice \"{Style.IBLUE}{result}{Style.IGREEN}\"")
            return None
        if int(result) > index:
            Messages.showWarning(f"Profile \"{Style.IBLUE}{result}{Style.IGREEN}\" not valid!")
            return None

        profile  = profiles[int(result)-1]
        printPy(f"{Style.GREEN} {Emoticons.pin()} MFA Device..........:{Style.BLUE}", end=' ')
        mfaDevice = input()

        spacesFound = re.search(" ",mfaDevice)
        if spacesFound:
            Messages.showWarning(f"Invalid MFA Device \"{Style.IBLUE}{mfaDevice}{Style.IGREEN}\", spaces are not allowed")
            return None
        try:
            arnparse(mfaDevice)
        except:
            Messages.showWarning(f"Invalid MFA Device \"{Style.IBLUE}{mfaDevice}{Style.IGREEN}\"")
            return None

        printPy(f"{Style.GREEN} {Emoticons.pin()} User Name...........:{Style.BLUE}", end=' ')
        userName = input()
        spacesFound = re.search(" ",mfaDevice)
        if spacesFound or userName == "":
            Messages.showWarning(f"Invalid User Name\"{Style.IBLUE}{mfaDevice}{Style.IGREEN}\"")
            return None

        output  = "\n"
        output += f" {Style.IBLUE} --> {Style.GREEN}Profile............: {Style.IBLUE}{profile}{Style.RESET}\n"
        output += f" {Style.IBLUE} --> {Style.GREEN}MFA Device.........: {Style.IBLUE}{mfaDevice}{Style.RESET}\n"
        output += f" {Style.IBLUE} --> {Style.GREEN}User Name..........: {Style.IBLUE}{userName}{Style.RESET}\n"
        printPy(output)

        printPy(f"{Style.GREEN} {Emoticons.pin()} Confirm [{Style.IGREEN}y/{Style.IGREEN}n{Style.RESET}]:{Style.BLUE}",end= ' ')
        confirm = input()
        if confirm.lower() == "y":
            record = {
                "id": str(uuid.uuid4()),
                "profile": profile,
                "mfa-device": mfaDevice,
                "user-name": userName
            }
            self.mfaRepository.insert(record)
            output = f"{Style.GREEN} {Emoticons.ok()} Saved!{Style.RESET}"
            printPy(output)
    
    def removeMFADevice(self, numberInList):
        mfaToRemove = None
        if numberInList > 0:
            for idx,mfa in enumerate(self.mfaRepository.all()):
                if (idx+1) == numberInList:
                    mfaToRemove = mfa
                    break
        if not mfaToRemove:
            Messages.showWarning("MFA Device not found!")
        else:
            output  = "\n"
            output += f" {Style.IBLUE} --> {Style.GREEN}Profile............: {Style.IBLUE}{mfaToRemove['profile']}{Style.RESET}\n"
            output += f" {Style.IBLUE} --> {Style.GREEN}MFA Device.........: {Style.IBLUE}{mfaToRemove['mfa-device']}{Style.RESET}\n"
            printPy(output)

            msgConfirm = f"{Style.GREEN} {Emoticons.pin()} Remove [{Style.IGREEN}y/{Style.IGREEN}n{Style.RESET}]: {Style.BLUE}"
            printPy(msgConfirm, end=" ")
            confirm = input()
            if confirm.lower() == "y":
                self.mfaRepository.remove(Query().id == mfaToRemove['id'])
                output  = "\n"
                output += f"{Style.GREEN} {Emoticons.ok()} Removed!{Style.RESET}"
                printPy(output)
    
    def listmfaDevices(self, filterByProfile):
        listmfaDevices = None
        if filterByProfile:
            listmfaDevices = self.mfaRepository.searchByQuery(where('profile') == filterByProfile)
        else:
            listmfaDevices = self.mfaRepository.all()

        if len(listmfaDevices) < 1:
            if filterByProfile:
               msg = f"There's no MFA Device added to the profile {Style.IBLUE}{filterByProfile}{Style.RESET}"
            else:
               msg = f"There's no MFA Device added" 
            Messages.showWarning(msg)
            return None
        
        tableArgs = TableArgs()
        header = ["#","Profile","MFA Device", "User Name"]
        prettyTable = PrettyTable(header)
        for idx, r in enumerate(listmfaDevices):
            columns = [ idx+1, r['profile'], r['mfa-device'], r['user-name']]
            prettyTable.addRow(columns)
        prettyTable.sortByColumn(int(tableArgs.sortCol) - 1)
        prettyTable.ascendingOrder(not tableArgs.desc)
        output = "\n" + Style.RESET + prettyTable.printMe("listMfaDevices",False,tableArgs)
        Messages.showMessage("MFA Devices", output)