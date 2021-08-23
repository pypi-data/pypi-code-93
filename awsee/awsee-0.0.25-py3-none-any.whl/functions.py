from awsee.style import Style
from awsee.emoticons import Emoticons
from awsee.awseestate import AwsSeeState
from awsee.__init__ import __version__
from awsee.general import *

class Functions:

    LIST_PROFILES             = "LIST_PROFILES"
    SYNC                      = "SYNC"
    INFO                      = "INFO"
    CLEAN                     = "CLEAN"
    ENV                       = "ENV"

    ADD_ROLE                  = "ADD_ROLE"
    REMOVE_ROLE               = "REMOVE_ROLE"
    LIST_ROLES                = "LIST_ROLES"

    ADD_MFA                   = "ADD_MFA"
    REMOVE_MFA                = "REMOVE_MFA"
    LIST_MFAS                 = "LIST_MFAS"
    START_SESSION_MFA_TOKEN   = "START_SESSION_MFA_TOKEN"
    START_SESSION             = "START_SESSION"

    ASSUME_ROLE               = "ASSUME_ROLE"

    # Groups
    GENERAL     = "GENERAL"
    ROLE        = "ROLE"
    MFA         = "MFA"
    AWS_SESSION = "AWS SESSION"

    FUNCTIONS = {
        INFO:{
            "name": "Info about your session",
            "identifiers": ["-i","--info"],
            "group": GENERAL,
            "description": "Show information about a session opened with AWSee",
            "arguments": [
                #{"name": "full","mandatory": False, "description": "List all the information, the roles added for each profile.","biggerLabel": 20},
            ],
            "examples-interactive": [
                {"command":f"{Style.GREEN}awsee --info {Style.RESET}"},
            ]
        },
        ENV:{
            "name": "Info about AWS Environment Variable",
            "identifiers": ["-e","--env"],
            "group": GENERAL,
            "description": "Show information about all the AWS Environment Variables set",
            "arguments": [
                #{"name": "full","mandatory": False, "description": "List all the information, the roles added for each profile.","biggerLabel": 20},
            ],
            "examples-interactive": [
                {"command":f"{Style.GREEN}awsee --env {Style.RESET}"},
            ]
        },
        CLEAN:{
            "name": "Clean the currennt session",
            "identifiers": ["-c","--clean"],
            "group": GENERAL,
            "description": "Clean the current AWS Session from the environment",
            "arguments": [
                #{"name": "full","mandatory": False, "description": "List all the information, the roles added for each profile.","biggerLabel": 20},
            ],
            "examples-interactive": [
                {"command":f"{Style.GREEN}awsee --clean {Style.RESET}"},
            ]
        },
        LIST_PROFILES:{
            "name": "List profiles",
            "identifiers": ["-l","-lf","--list"],
            "group": GENERAL,
            "description": "List all profiles at your credentials (~/.aws/credentials)",
            "arguments": [
                {"name": "full","mandatory": False, "description": "List all the information, the roles added for each profile.","biggerLabel": 20},
            ],
            "examples-interactive": [
                {"command":f"{Style.GREEN}awsee --list {Style.RESET}"},
                {"command":f"{Style.GREEN}awsee --list {Style.IBLUE}full {Style.RESET}"},
                {"command":f"{Style.GREEN}awsee -l {Style.IBLUE}full {Style.RESET}"},
                {"command":f"{Style.GREEN}awsee -lf {Style.MAGENTA}# Same as -l full / --list full{Style.RESET}"},
            ]
        },
        SYNC:{
            "name": "Synchronize cache with remote data of credentials",
            "identifiers": ["-s","--sync"],
            "group": GENERAL,
            "description": f"Synchronize information remotely acquired from AWS (ex: Account Number, MFA Serial) for the credentials. This is done automatically (if not blocked by Polices) only once, when the {Style.IGREEN}awsee{Style.RESET} run for the first time. Using this command, you can force an update.",
            "arguments": [
                # {"name": "-f","mandatory": False, "description": "Full list, MFA Serial and Account (remote calls)","biggerLabel": 20}
            ],
            "examples-interactive": [
                {"command":f"{Style.GREEN}awsee --sync {Style.RESET}"},
            ]
        },
        START_SESSION_MFA_TOKEN:{
            "id": START_SESSION_MFA_TOKEN,
            "identifiers": [],
            "name": "Start AWS Session using MFA Token",
            "group": AWS_SESSION,
            "description": f"Start an AWS Session that needs your six-digit MFA Token. Optionally, it can be informed the profile chosen, if not informe the default will be used.",
            "arguments": [
                {"name": "{000000}","mandatory": True, "description": "The MFA Token","biggerLabel": 20},
                {"name": "[profile]","mandatory": False, "description": "The profile to be used to start the Session","biggerLabel": 20}
            ],
            "examples-interactive": [
                {"command":f"{Style.GREEN}awsee 874341 {Style.RESET}"},
                {"command":f"{Style.GREEN}awsee 687509 {Style.RESET}{Style.IBLUE}johneast{Style.RESET}"},
            ]
        },
        START_SESSION:{
            "id": START_SESSION,
            "identifiers": ["-p"],
            "name": "Start AWS Session",
            "group": AWS_SESSION,
            "description": f"Start an AWS Session for a specific profile.",
            "arguments": [
                {"name": "[profile]","mandatory": True, "description": "The profile to be used to start the Session","biggerLabel": 20}
            ],
            "examples-interactive": [
                {"command":f"{Style.GREEN}awsee -p {Style.RESET}{Style.IBLUE}johneast{Style.RESET}"},
                {"command":f"{Style.GREEN}awsee -p {Style.RESET}{Style.IBLUE}supplier_cc{Style.RESET}"},
            ]
        },
         ASSUME_ROLE:{
            "name": "Assume Role",
            "group": AWS_SESSION,
            "identifiers": ["-r","--assume-role"],
            "description": f"Assume a role",
            "arguments": [
                 {"name": "{role}","mandatory": True, "description": "The role name to be assumed (check their names listing the roles using: aswme -lr","biggerLabel": 20},
            ],
            "examples-interactive": [
                {"command":f"{Style.GREEN}awsee -r {Style.RESET}{Style.IBLUE}supplier{Style.RESET}"},
                {"command":f"{Style.GREEN}awsee -r {Style.RESET}{Style.IBLUE}ecommerce{Style.RESET}"},
            ]
        },
        ADD_ROLE:{
            "name": "Add a role to one of your profiles",
            "identifiers": ["-ar","--add-role"],
            "group": ROLE,
            "description": f"Associate a Role to one of your profiles to enable the request of Session Tokens while \"assuming\" this role (ex: cross account access).",
            "arguments": [
                # {"name": "[profile]","mandatory": False, "description": "The profile to be used to start the Session","biggerLabel": 20}
            ],
            "examples-interactive": [
                {"command":f"{Style.GREEN}awsee -ar {Style.RESET}"},
            ]
        },
        LIST_ROLES:{
            "name": "List roles of your profiles",
            "identifiers": ["-lr","--list-role"],
            "group": ROLE,
            "description": f"List all roles added to use with your profiles.",
            "arguments": [
                 {"name": "[profile]","mandatory": False, "description": "Filter by profile","biggerLabel": 20}
            ],
            "examples-interactive": [
                {"command":f"{Style.GREEN}awsee -lr {Style.RESET}"},
                {"command":f"{Style.GREEN}awsee -lr {Style.RESET}{Style.IBLUE}johneast{Style.RESET}"},
            ]
        },
        REMOVE_ROLE:{
            "name": "Remove a role of your profile",
            "identifiers": ["-rr","--remove-role"],
            "group": ROLE,
            "description": f"Remove a role added to your profile.",
            "arguments": [
                 {"name": "[#number]","mandatory": False, "description": "Number of the role in the list to be removed. Use -lr to see the list","biggerLabel": 20},
                 {"name": "[role-name]","mandatory": False, "description": "Name of the role to be removed","biggerLabel": 20}
            ],
            "examples-interactive": [
                {"command":f"{Style.GREEN}awsee -rr {Style.RESET}{Style.IBLUE}2{Style.RESET}"},
                {"command":f"{Style.GREEN}awsee -rr {Style.RESET}{Style.IBLUE}johnwest{Style.RESET}"},
            ]
        },
        ADD_MFA:{
            "name": "Add a MFA Device to one of your profiles",
            "identifiers": ["-am","--add-mfa"],
            "group": MFA,
            "description": f"Associate a MFA Device to one of your profiles to enable access using MFA Tokens.",
            "arguments": [
                # {"name": "[profile]","mandatory": False, "description": "The profile to be used to start the Session","biggerLabel": 20}
            ],
            "examples-interactive": [
                {"command":f"{Style.GREEN}awsee -am {Style.RESET}"},
            ]
        },
        LIST_MFAS:{
            "name": "List MFAs Device of your profiles",
            "identifiers": ["-lm","--list-mfa"],
            "group": MFA,
            "description": f"List all MFA Devices added to use with your profiles.",
            "arguments": [
                 {"name": "[profile]","mandatory": False, "description": "Filter by profile","biggerLabel": 20}
            ],
            "examples-interactive": [
                {"command":f"{Style.GREEN}awsee -lm {Style.RESET}"},
                {"command":f"{Style.GREEN}awsee -lm {Style.RESET}{Style.IBLUE}johneast{Style.RESET}"},
            ]
        },
        REMOVE_MFA:{
            "name": "Remove a MFA Device of your profile",
            "group": MFA,
            "identifiers": ["-rm","--remove-mfa"],
            "description": f"Remove a MFA Device added to your profile.",
            "arguments": [
                 {"name": "[#number]","mandatory": True, "description": "Number of the MFA Device in the list to be removed. Use -lm to see the list","biggerLabel": 20},
            ],
            "examples-interactive": [
                {"command":f"{Style.GREEN}awsee -rm {Style.RESET}{Style.IBLUE}3{Style.RESET}"},
            ]
        }
    }

    def __init__(self):
        pass

    def version_label(self):
        return f"{Style.IBLUE}AWS{Style.IYELLOW}ee {Style.IBLUE}v{Style.IYELLOW}{__version__}{Style.RESET}\n"
    def showVersion(self):
        printPy(self.version_label())

    def showUsage(self, short=True):
        SIZE_SEPARATOR             = 120
        LABEL_LENGTH_FUNCTION_NAME = 25

        output  = self.version_label()
        output += "-".ljust(SIZE_SEPARATOR,"-") + "\n" 
        output += "   " + Emoticons.tool() + "   " + Style.CYAN + "U S A G E" + Style.RESET + "" + "\n"
        output += "-".ljust(SIZE_SEPARATOR,"-") + "\n"
        output += f"""
        {Style.GREEN}awsee {Style.IBLUE}[TOKEN-MFA]{Style.RESET} {Style.IBLUE}[-p profile] [-r role] {Style.IBLACK}[-nt or --new-terminal]
        
        Examples:
            {Style.GREEN}awsee {Style.IBLUE}857946                       {Style.IMAGENTA}Open AWS Session with default profile with your six-digit MFA Token
            {Style.GREEN}awsee {Style.IBLUE}857946 -p infra              {Style.IMAGENTA}Open AWS Session with the passed profile using your six-digit MFA Token
            {Style.GREEN}awsee {Style.IBLUE}857946 -p infra -r prod      {Style.IMAGENTA}Open AWS Session with the passed profile using your six-digit MFA Token
                                               and immediatelly assume the passed role at this new session
            {Style.GREEN}awsee{Style.IBLUE}                              {Style.IMAGENTA}Open AWS Session with default profile, it will check if needs MFA 
            {Style.GREEN}awsee {Style.IBLUE}-p dev                       {Style.IMAGENTA}Open AWS Session with the passed profile, asks for MFA if needed
            {Style.GREEN}awsee {Style.IBLUE}-r developer                 {Style.IMAGENTA}Assume a Role inside the current AWS Session
            {Style.GREEN}awsee {Style.IBLUE}-p dev  -r developer         {Style.IMAGENTA}Open AWS Session with the passed profile, and following assume the role 
            {Style.GREEN}awsee {Style.IBLUE}-p prod -r admin             {Style.IMAGENTA}Open AWS Session with the passed profile, and following assume the role 
        
        {Style.GREEN}awsee -nt {Style.RESET}or {Style.GREEN}--new-terminal            {Style.IMAGENTA}When opening an AWS Session, will do it in a new terminal{Style.RESET}
        {Style.GREEN}awsee -h  {Style.RESET}or {Style.GREEN}--help                    {Style.IMAGENTA}Show this and all auxiliary functions (use --help for more information){Style.RESET}
        {Style.GREEN}awsee -u  {Style.RESET}or {Style.GREEN}--usage                   {Style.IMAGENTA}Show only how to use, not the auxiliary functions{Style.RESET}
        {Style.GREEN}awsee -v  {Style.RESET}or {Style.GREEN}--version                 {Style.IMAGENTA}Well, guess what? :-){Style.RESET}

        {Style.GREEN}awsee {Style.IBLUE}[FUNCTION] {Style.IMAGENTA}                      {Style.IMAGENTA}Execute an auxiliary function, see below for all available options{Style.RESET}
        """
        printPy(output)

    def showFunctions(self, short=True):
        SIZE_SEPARATOR             = 120
        LABEL_LENGTH_FUNCTION_NAME = 25

        output  = "-".ljust(SIZE_SEPARATOR,"-") + "\n" 
        output += "   " + Emoticons.tool() + "   " + Style.CYAN + "F U N C T I O N S" + Style.RESET + "" + "\n"
        output += "-".ljust(SIZE_SEPARATOR,"-") + "\n"
        groupPrinted = ""
        i = 0
        for key in self.FUNCTIONS:
            i += 1
            function      = self.FUNCTIONS[key]
            functionName  = self.convertFunctionsName(key)
            functionDescr = "  " + Emoticons.pointRight() + " " + Style.GREEN + functionName + Style.RESET + (" ".ljust(LABEL_LENGTH_FUNCTION_NAME - len(functionName) + 2,"-")) + \
                                  "> "+ Functions.formatDescr(function["description"], 34, 60) + "\n"
            
            groupTitle = " " + Style.IWHITE + Style.BG_BLUE + " --> " + function["group"].upper() + " ".ljust(10 - len(function["group"])," ") + Style.RESET + "\n" #+ "-".ljust(len(function["group"]),"-") + "\n"    
            if groupPrinted != function["group"]:
                output += groupTitle 
                groupPrinted = function["group"]

            output += functionDescr

            if not short:
               if len(function["arguments"]) > 0:
                  output += Style.IBLUE + "          Arguments: " + Style.RESET + "\n"
               for args in function["arguments"]:
                   output += Style.IBLUE + "               " + args["name"] + " ".ljust(args["biggerLabel"] - len(args["name"])," ") + Style.IBLUE 
                   output += ("[Required]" if args["mandatory"] == True else "[Optional]")
                   output += Style.RESET + "....: " + Style.RESET + Functions.formatDescr(args["description"],51,45) + "\n"    
               output += "          " + Style.IBLUE + "Examples:" + Style.RESET + "\n"
               for exs in function["examples-interactive"]:
                   output += "               " + exs["command"] + "\n"
               output += "-".ljust(SIZE_SEPARATOR,"-") + "\n"
            else:
               output += " ".ljust(LABEL_LENGTH_FUNCTION_NAME + 10," ") + f"{Style.GREEN}awsee "
               for ii,ident in enumerate(function["identifiers"]):
                   output += f"{Style.GREEN}[{ident}]"
                   output += " or " if ii < len(function["identifiers"]) - 1 else ""
               output += f"{Style.RESET}\n"
            
        printPy(output)
    
    def showFunction(self, key):
        SIZE_SEPARATOR             = 95
        LABEL_LENGTH_FUNCTION_NAME = 25

        function = Functions.FUNCTIONS[key]

        output  = "-".ljust(SIZE_SEPARATOR,"-") + "\n"           
        output += "   " + Emoticons.tool() + " " + Style.CYAN +  function["name"].upper() + Style.RESET + "" + "\n"
        output += "-".ljust(SIZE_SEPARATOR,"-") + "\n"    

        functionName = self.convertFunctionsName(key)
        functionDescr = "  " + Emoticons.pointRight() + " " + Style.GREEN + functionName + Style.RESET + (" ".ljust(LABEL_LENGTH_FUNCTION_NAME - len(functionName) + 2,"-")) + \
                                "> "+ Functions.formatDescr(function["description"], 26, 59) + "\n"
        output += functionDescr
        output += Style.MAGENTA + "          Arguments: " + Style.RESET + "\n"
        for args in function["arguments"]:
            output += Style.BLUE + "               " + args["name"] + " ".ljust(args["biggerLabel"] - len(args["name"])," ") + Style.MAGENTA 
            output += ("[Required]" if args["mandatory"] == True else "[Optional]")
            output += Style.RESET + "....: " + Style.RESET + Functions.formatDescr(args["description"],51,34) + "\n"
        output += "          " + Style.MAGENTA + "Examples:" + Style.RESET + "\n"
        for exs in function["examples-interactive"]:
            output += "               " + exs["command"] + "\n"
        output += "-".ljust(SIZE_SEPARATOR,"-") + "\n"
        return output

    def getFunctionByArgumentIdentifier(self,identifier):
        for f in self.FUNCTIONS:
            for identf in self.FUNCTIONS[f]["identifiers"]:
                if identf == identifier:
                   return f
        return None

    def convertFunctionsName(self,function):
        pos = function.find("-")
        while pos > 1 and pos < 20:
            capitalize = function[pos+1]
            function = function.replace("-"+capitalize,capitalize.upper())
            pos = function.find("-")
        return function

    def formatDescr(text, margin, width):
        MARGIN    = margin
        WIDTH     = width
        formatted = text
        line      = ""

        if len(formatted) > WIDTH:
           formatted = ""
           for word in text.split(" "):
               if len(line + word + " ") <= (WIDTH):
                  line += word + " "
               else:
                  finalLine  = Functions.fillLineSpacesUntil(line,WIDTH)
                  formatted += finalLine + "\n" + "".ljust(MARGIN," ") 
                  line = word + " " 
        
        return formatted + line
    
    def fillLineSpacesUntil(line, width):
        finalLine = line
        posSpace  = 0
        while (len(finalLine) + 1)  < width:
            spaceIndex = finalLine.find(' ',posSpace)
            finalLine  = finalLine[:spaceIndex] + " " + finalLine[spaceIndex:]
            posSpace   = spaceIndex + 2
           
        return finalLine      

