
import re, uuid
from tinydb import Query, where
from arnparse import arnparse
from awsee.messages import Messages
from awsee.style import Style
from awsee.emoticons import Emoticons
from awsee.utils import Utils
from awsee.tableargs import TableArgs
from awsee.prettytable import PrettyTable
from awsee.repository import CredentialsRepository, RoleRepository
from awsee.general import *

class RoleManager:

    def __init__(self):
        self.credentialsRepository = CredentialsRepository()
        self.roleRepository        = RoleRepository()

    def addRole(self):
        Messages.showMessage("ADD ROLE TO PROFILE")
        index            = 0
        sizeSeparator    = 120
        sizeLabelProfile = 18
        output           = ""
        output           += Style.GREEN + "-".ljust(sizeSeparator,"-") + "\n"
        output           += f" {Style.IBLUE}PROFILES:\n"
        profiles          = []
        for c in self.credentialsRepository.all():
            index += 1
            profiles.append(c['profile'])

            pn        = c['profile'] + " ".rjust(sizeLabelProfile -len(c['profile']), " ")
            account   = c['account']
            line      = f"  {Style.IBLUE}{index:02d} -->{Style.GREEN} {pn} {Style.IBLUE}Account..:{Style.GREEN} {account}"
            labelRole = "Roles..: "
            roles     = ""
            for idx, r in enumerate(self.roleRepository.searchByQuery(where('profile') == c['profile'])):
                if len(roles) > 1:
                    roles += "\n" + " ".ljust(len(Utils.removeCharsColors(line)) + len(labelRole) + 1," ")
                roles += f"{Style.BLUE}{idx+1:02d}{Style.GREEN}-{r['role-arn']} {Style.BLUE}({r['role-name']})"
            if len(roles) > 1:
                roles = f"{Style.IBLUE}{labelRole}{Style.GREEN}{roles}{Style.GREEN}"
            output += line + f" {roles}\n"
        output += "-".ljust(sizeSeparator,"-")
        printPy(output)
        printPy(f"{Style.GREEN} {Emoticons.pin()} Choose a profile....:{Style.BLUE}", end= ' ')
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
        printPy(f"{Style.GREEN} {Emoticons.pin()} Role Name...........:{Style.BLUE}",end=' ')
        roleName = input()

        spacesFound = re.search(" ",roleName)
        if spacesFound:
            Messages.showWarning(f"Invalid Role Name \"{Style.IBLUE}{roleName}{Style.IGREEN}\", spaces are not allowed")
            return None

        printPy(f"{Style.GREEN} {Emoticons.pin()} Role ARN............:{Style.BLUE}",end=' ')
        roleArn  = input()
        try:
            roleArnParse = arnparse(roleArn)
        except:
            Messages.showWarning(f"Invalid Role ARN \"{Style.IBLUE}{roleArn}{Style.IGREEN}\"")
            return None

        output  = "\n"
        output += f" {Style.IBLUE} --> {Style.GREEN}Profile............: {Style.IBLUE}{profile}{Style.RESET}\n"
        output += f" {Style.IBLUE} --> {Style.GREEN}Role Name..........: {Style.IBLUE}{roleName}{Style.RESET}\n"
        output += f" {Style.IBLUE} --> {Style.GREEN}Role ARN...........: {Style.IBLUE}{roleArn}{Style.RESET}\n"
        printPy(output)

        printPy(f"{Style.GREEN} {Emoticons.pin()} Confirm [{Style.IGREEN}y/{Style.IGREEN}n{Style.RESET}]:{Style.BLUE}",end=' ')
        confirm = input()
        if confirm.lower() == "y":
            record = {
                "id": str(uuid.uuid4()),
                "profile": profile,
                "role-name": roleName,
                "role-arn": roleArn
            }
            self.roleRepository.insert(record)
            output = f"{Style.GREEN} {Emoticons.ok()} Saved!{Style.RESET}"
            printPy(output)
    
    def removeRole(self, numberInList, roleName):
        roleToRemove = None
        if numberInList > 0:
            for idx,role in enumerate(self.roleRepository.all()):
                if (idx+1) == numberInList:
                    roleToRemove = role
                    break
        else:
            roleToRemove = self.roleRepository.searchByQuery(where('role-name') == roleName)
            roleToRemove = roleToRemove[0]
        
        if not roleToRemove:
            Messages.showWarning("Role not found!")
        else:
            output  = "\n"
            output += f" {Style.IBLUE} --> {Style.GREEN}Profile............: {Style.IBLUE}{roleToRemove['profile']}{Style.RESET}\n"
            output += f" {Style.IBLUE} --> {Style.GREEN}Role Name..........: {Style.IBLUE}{roleToRemove['role-name']}{Style.RESET}\n"
            output += f" {Style.IBLUE} --> {Style.GREEN}Role ARN...........: {Style.IBLUE}{roleToRemove['role-arn']}{Style.RESET}\n"
            printPy(output)

            printPy(f"{Style.GREEN} {Emoticons.pin()} Remove [{Style.IGREEN}y/{Style.IGREEN}n{Style.RESET}]:{Style.BLUE}",end=' ')
            confirm = input()
            if confirm.lower() == "y":
                self.roleRepository.remove(Query().id == roleToRemove['id'])
                output  = "\n"
                output += f"{Style.GREEN} {Emoticons.ok()} Removed!{Style.RESET}"
                printPy(output)
    
    def listRoles(self, filterByProfile):
        listRoles = None
        if filterByProfile:
            listRoles = self.roleRepository.searchByQuery(where('profile') == filterByProfile)
        else:
            listRoles = self.roleRepository.all()

        if len(listRoles) < 1:
            if filterByProfile:
               msg = f"There's no role added to the profile {Style.IBLUE}{filterByProfile}{Style.RESET}"
            else:
               msg = f"There's no role added"
            Messages.showWarning(msg)
            return None
        
        activeRole = os.environ['AWS_ROLE'] if 'AWS_ROLE' in os.environ else None
        tableArgs = TableArgs()
        # Hightlight the current Role
        if activeRole:
           tableArgs.setArguments("| " + activeRole + " ")
        header = ["#","Profile","Role Name","Role ARN"]
        prettyTable = PrettyTable(header)
        for idx, r in enumerate(listRoles):
            columns = [ idx+1, r['profile'], r['role-name'], r['role-arn']]
            prettyTable.addRow(columns)
        prettyTable.sortByColumn(int(tableArgs.sortCol) - 1)
        prettyTable.ascendingOrder(not tableArgs.desc)
        output = "\n" + Style.RESET + prettyTable.printMe("listRoles",False,tableArgs)
        Messages.showMessage("ROLES", output)