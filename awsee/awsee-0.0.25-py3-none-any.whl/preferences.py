import os
import configparser
from os.path import expanduser
from awsee.emoticons import Emoticons
from awsee.utils import Utils
from awsee.general import *

FILE_INI                    = os.path.join(expanduser("~"),".awsee","awsee.ini")
GENERAL                     = "GENERAL"
WINDOWS                     = "WINDOWS"
LINUX                       = "LINUX"
GENERAL_DEFAULT_PROFILE     = "default-profile"
GENERAL_EMOTICONS_ENABLED   = "emoticons-enabled"
GENERAL_NO_COLOR            = "no-color"
GENERAL_DURATION_SECONDS    = "duration-seconds"
WINDOWS_TERMINAL_COMMAND    = "terminal-command"
LINUX_TERMINAL_COMMAND      = "terminal-command"
APPEND_AWSEE_TO_CREDENTIALS = "append-awsee-to-crendentials"

class Preferences:

    @property
    def defaultProfile(self):
        return self._defaultProfile
    
    @property
    def emoticonsEnabled(self):
        return self._emoticonsEnabled
    
    @property
    def noColor(self):
        return self._noColor

    @property
    def windows(self):
        return self._windows

    @property
    def linux(self):
        return self._linux
    
    @property
    def durationSeconds(self):
        return self._duration_seconds
    
    @property
    def append_awsee_to_crendentials(self):
        return self._append_awsee_to_crendentials

    def __init__(self):
        if not os.path.exists(FILE_INI):
            configFileIni = configparser.ConfigParser(allow_no_value=True)
            configFileIni.add_section(GENERAL)
            configFileIni.add_section(WINDOWS)
            configFileIni.add_section(LINUX)
            configFileIni.set(GENERAL, GENERAL_DEFAULT_PROFILE,"default")
            configFileIni.set(GENERAL, GENERAL_EMOTICONS_ENABLED,"true")
            configFileIni.set(GENERAL, GENERAL_NO_COLOR,"false")
            configFileIni.set(GENERAL, "; Duration, in seconds, of the role session. Range from 900 seconds (15 minutes) up to the maximum session duration that is set for the role (1h to 12h).")
            configFileIni.set(GENERAL, "; If you specify a value higher than this setting or the administrator setting (whichever is lower), the operation fails.")
            configFileIni.set(GENERAL, GENERAL_DURATION_SECONDS,"3600")
            configFileIni.set(GENERAL, APPEND_AWSEE_TO_CREDENTIALS,"false")

            configFileIni.set(WINDOWS, "; WINDOWS Options for New Terminal Window")
            configFileIni.set(WINDOWS, ";   Leave it blanks to use the default options CMDER or CMD")
            configFileIni.set(WINDOWS, ";   To use Git-Bash, use option 1 or 2 pointing to your installation path")
            configFileIni.set(WINDOWS, ";   To use Windows Terminal, use option 3")
            configFileIni.set(WINDOWS, "; Option 0) terminal-command =")
            configFileIni.set(WINDOWS, "; Option 1) terminal-command = C:\\Developer\\Git\\apps\\Git\\bin\\sh.exe")
            configFileIni.set(WINDOWS, "; Option 2) terminal-command = C:\\Developer\\Git\\apps\\Git\\git-bash.exe")
            configFileIni.set(WINDOWS, "; Option 3) terminal-command = wt")
            configFileIni.set(WINDOWS, WINDOWS_TERMINAL_COMMAND,"")

            configFileIni.set(LINUX, "; LINUX Options for New Terminal Window")
            configFileIni.set(LINUX, ";   Leave it blanks to use the default option (Still to be worked, not ready!)")
            configFileIni.set(LINUX, ";   ---")
            configFileIni.set(LINUX, "; Option 0) terminal-command =")
            configFileIni.set(LINUX, "; Option 1) terminal-command = ")
            configFileIni.set(LINUX, LINUX_TERMINAL_COMMAND ,"")

            with open(FILE_INI,'w') as configfile:
                configFileIni.write(configfile)
                configFileIni = configparser.ConfigParser(allow_no_value=True)
        else:
            # Add new configuration parameters (for those who have init file already created on the his/her system after)
            self.check_add_new_parameter(GENERAL, GENERAL_DURATION_SECONDS, 3600)
            self.check_add_new_parameter(GENERAL, APPEND_AWSEE_TO_CREDENTIALS, "false")
        
        configFileIni = configparser.ConfigParser()
        configFileIni.read(FILE_INI)
        self._defaultProfile   = configFileIni[GENERAL][GENERAL_DEFAULT_PROFILE]
        self._emoticonsEnabled = configFileIni[GENERAL][GENERAL_EMOTICONS_ENABLED] in ['True','true']
        
        if GENERAL_NO_COLOR in configFileIni[GENERAL]:
           self._noColor       = configFileIni[GENERAL][GENERAL_NO_COLOR] in ['True','true'] 
        else:
           self._noColor       = False

        if GENERAL_DURATION_SECONDS in configFileIni[GENERAL]:
           _vlr = configFileIni[GENERAL][GENERAL_DURATION_SECONDS]
           if Utils.isNumber(_vlr):
              self._duration_seconds = int(_vlr)
           else:
              self._duration_seconds = 3600 
        else:
           self._duration_seconds = 3600
        
        if APPEND_AWSEE_TO_CREDENTIALS in configFileIni[GENERAL]:
            _vlr = configFileIni[GENERAL][APPEND_AWSEE_TO_CREDENTIALS]
            self._append_awsee_to_crendentials = configFileIni[GENERAL][APPEND_AWSEE_TO_CREDENTIALS] in ['True','true']
        else:
            self._append_awsee_to_crendentials = False

        self._windows          = Windows(configFileIni[WINDOWS][WINDOWS_TERMINAL_COMMAND])
        self._linux            = Linux(configFileIni[LINUX][LINUX_TERMINAL_COMMAND])

        Emoticons.ENABLED = self._emoticonsEnabled
    
    def check_add_new_parameter(self, section, new_parameter, default_parameter_value):
        """ Add new configuration parameter (for those who have init their files already, after this parameter were added) """
        with open(FILE_INI, 'r') as file:
            data_ini = file.read()
        
        with open(FILE_INI, 'r+') as f:
            write_back = False
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line.startswith(f'[{section}]'):
                    if not new_parameter in data_ini:
                        lines[i] = lines[i].strip() + f'\n{new_parameter} = {default_parameter_value}\n'
                        write_back = True
            if write_back:
                f.seek(0)
                for line in lines:
                    f.write(line)

class Windows:

    @property
    def terminalCommand(self):
        return self._terminal_command

    def __init__(self, _terminal_command):
        self._terminal_command = _terminal_command

class Linux:

    @property
    def terminalCommand(self):
        return self._terminal_command

    def __init__(self, _terminal_command):
        self._terminal_command = _terminal_command
