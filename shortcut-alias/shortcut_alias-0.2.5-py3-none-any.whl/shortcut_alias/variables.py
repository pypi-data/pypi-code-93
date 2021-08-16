from datetime import datetime
import platform
import sys

__author__ = "Matt Limb <matt.limb17@gmail.com>"

class VAR_DATETIME:
    weekdays = {
        0: ( "Monday", "Mon" ),
        1: ( "Tuesday", "Tue" ),
        2: ( "Wednesday", "Wed" ),
        3: ( "Thursday", "Thurs" ),
        4: ( "Friday", "Fri" ),
        5: ( "Saturday", "Sat" ),
        6: ( "Sunday", "Sun" )
    }

    @property
    def date(self):
        return datetime.now().date().isoformat()

    @property
    def date_utc(self):
        return datetime.utcnow().date().isoformat()

    @property
    def time(self):
        return datetime.now().time().isoformat()

    @property
    def time_utc(self):
        return datetime.utcnow().time().isoformat()
    
    @property
    def weekday(self):
        return self.weekdays[datetime.now().weekday()][0]
    
    @property
    def weekday_short(self):
        return self.weekdays[datetime.now().weekday()][1]

    @property
    def timezone(self):
        return datetime.now().astimezone().tzname()

_datetime = VAR_DATETIME()

VARIABLES = {
    "variables": {
        "options": {},
        "env": {},
        "datetime": VAR_DATETIME(),
        "platform": {
            "name": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
        },
        "device": {
            "name": platform.node(),
            "arch": platform.machine(),
            "processor": platform.processor(),
        },
        "python": {
            "compiler": platform.python_compiler(),
            "implementation": platform.python_implementation(),
            "revision": platform.python_revision(),
            "version": platform.python_version(),
            "version_major": platform.python_version_tuple()[0],
            "version_minor": platform.python_version_tuple()[1],
            "version_patch": platform.python_version_tuple()[2],
            "c_api": sys.api_version
        }
    },
    "commands": {},
    "constants": {
        "string": {
            "empty": "",
        },
        "platform": {
            "windows": "Windows",
            "linux": "Linux",
            "mac": "Darwin",
            "java": "Java",
        },
        "windows_edition": {
            "enterprise": "Enterprise",
            "iotuap": "IoTUAP",
            "server": "ServerStandard",
            "nanoserver": "nanoserver"
        },
        "shell": {
            "pipe": "|",
            "pipe_err": "|&",
            "background": "&",
            "and": "&&",
            "or": "||",
            "not": "!",
            "tilda": "~",
            "file_descriptors": {
                "stdin": 0,
                "stdout": 1,
                "stderr": 2
            },
            "redirect": {
                "input": "<",
                "output": {
                    "out": ">",
                    "append": ">>",
                },
                "here": {
                    "document": "<<",
                    "word": "<<<"
                },
                "merge": {
                    "output": ">&",
                    "input": "<&",
                    "outerr": "2>&1"
                }
            },
            "eof": "EOF",
            "dev_null": "/dev/null"
        }
    }
}

if platform.system() == "Linux":
    VARIABLES["variables"]["linux"] = {
        "libc": platform.libc_ver()[0],
        "libc_version": platform.libc_ver()[1]
    }
elif platform.system() == "Windows":
    VARIABLES["variables"]["windows"] = {
        "win32_release": platform.win32_ver()[0],
        "win32_ver": platform.win32_ver()[1],
        "win32_service_pack": platform.win32_ver()[2],
        "win32_os_type": platform.win32_ver()[3],
        "win32_edition": platform.win32_edition(),
        "win32_iot_edition": platform.win32_is_iot() 
    }
    VARIABLES["constants"]["shell"]["ps_null"] = "$null"
    VARIABLES["constants"]["shell"]["cmd_null"] = "NUL"

    # On Windows alias to a reasonable default
    VARIABLES["constants"]["shell"]["dev_null"] = "$null"
elif platform.system() == "Darwin":
    VARIABLES["variables"]["mac"] = {
        "mac_release": platform.mac_ver()[0],
        "mac_version": platform.mac_ver()[1][0],
        "mac_dev_stage": platform.mac_ver()[1][1],
        "mac_non_release_version": platform.mac_ver()[1][2],
        "mac_machine": platform.mac_ver()[2]
    }
elif platform.system() == "Java":
    VARIABLES["variables"]["java"] = {
        "java_version":  platform.java_ver()[0],
        "java_vendor": platform.java_ver()[1],
        "java_vm_name": platform.java_ver()[2][0],
        "java_vm_release": platform.java_ver()[2][1],
        "java_vm_vendor": platform.java_ver()[2][3],
        "java_os_name": platform.java_ver()[3][0],
        "java_os_version": platform.java_ver()[3][1],
        "java_os_arch": platform.java_ver()[3][2]
    }