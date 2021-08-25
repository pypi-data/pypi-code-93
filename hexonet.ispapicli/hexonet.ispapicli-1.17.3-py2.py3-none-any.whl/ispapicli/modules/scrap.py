import sys
from typing import Text
from bs4 import BeautifulSoup
from .db import DB
from git import Repo
import os
from pathlib import Path
import re
import shutil


class Scrap:
    def __init__(self, URL=""):
        # init db
        self.dbObj = DB()
        # init repo dir
        self.__initAppDirectories()
        self.__initCloneAPIDocsDir()

    def __initAppDirectories(self):
        """
        Init app directories

        Returns:
        --------
        True
        """
        if getattr(sys, "frozen", False):
            self.absolute_dirpath = os.path.dirname(sys.executable)
            self.repo_path = os.path.join(self.absolute_dirpath, "APIDocsRepo")
        elif __file__:
            self.absolute_dirpath = os.path.dirname(__file__)
            self.repo_path = os.path.join(self.absolute_dirpath, "../APIDocsRepo/")
        return True

    def __initCloneAPIDocsDir(self):
        """
        Init cloning repo

        Returns:
        --------
        True
        """
        if os.path.exists(self.repo_path):
            # remove old repo
            shutil.rmtree(self.repo_path)
        if not os.path.exists(self.repo_path):
            os.makedirs(self.repo_path)
        return True

    def __saveCommandToDB(self, commandName, data):
        """
        Creates a record in DB for the command: commandName

        Returns:
        --------
        True | Raise exception
        """
        try:
            self.dbObj.insertCommand(commandName, data)
            return True
        except Exception:
            raise Exception("Couldn't insert the command: " + commandName)

    def __getCommandData(self, commandName, description, availability, parameters):
        """
        Gather all command data in a list and return it

        Returns:
        --------
        Dict{}: data
        """
        try:
            data = {}
            data["command"] = commandName
            data["description"] = description
            data["availability"] = availability
            data["paramaters"] = parameters
            return data
        except Exception as e:
            raise e

    def __cloneRepo(self):
        """
        Clone remote Docs repo

        Returns:
        --------
        True || False
        """
        if self.__initCloneAPIDocsDir():
            repo = Repo.clone_from(
                "https://github.com/hexonet/hexonet-api-documentation.git",
                self.repo_path,
                branch="master",
            )
            return True
        return False

    def __getCommandsParams(self, raw):
        """
        Parse parameters from raw md data

        Returns:
        --------
        List[]: params
        """
        # split the rows based on | delimiter
        # this will return a list of paramname, min, type, etc.
        headers = raw[2].split("|")
        params = []
        param = {}
        # skip uncessary spaces, start from line/row 4
        for i in range(4, len(raw)):
            if raw[i] != "----":
                try:
                    cols = raw[i].split("|")  # split each row data to match the headers
                    for j in range(0, len(cols)):
                        headType = headers[j].strip(" \t\n\r")
                        headValue = cols[j].strip(" \t\n\r")
                        param[headType] = headValue
                    # append params | add only valid params
                    if len(param) == 4:
                        params.append(param)
                    param = {}
                except Exception as e:
                    return params
            else:
                return params
        return params

    # scrap commands
    def scrapCommands(self):
        """
        Executes the scrap process

        Returns:
        --------
        True || False
        """
        # clone repo
        if self.__cloneRepo():
            try:
                # init database | delete old database
                # self.dbObj.db.drop_table("commands")
                commandName = ""
                description = ""
                availability = ""
                parameters = []
                # get all commands urls, ending with .md
                mainDir = os.path.join(self.repo_path, "API")
                result = list(Path(mainDir).glob("**/*.md"))
                # section regex
                secionRegex = r"^#{2}\s\w+$"
                for dir in result:
                    # Load the file into file_content
                    file_content = []
                    for line in open(dir).readlines():
                        file_content.append(line.strip(" \t\n\r"))
                    # parse the content
                    for i in range(len(file_content)):
                        # first line is the command name
                        if i == 0:
                            commandName = (file_content[i]).split(" ")[1]
                        # checkSection
                        section = re.findall(secionRegex, file_content[i])
                        if len(section) == 1:
                            sectionName = (section[0].split(" "))[1]
                            if sectionName == "DESCRIPTION":
                                description = file_content[i + 1]
                            if sectionName == "AVAILABILITY":
                                availability = file_content[i + 1]
                            if sectionName == "COMMAND":
                                parameters = self.__getCommandsParams(file_content[i:])
                                break
                    data = self.__getCommandData(
                        commandName, description, availability, parameters
                    )
                    self.__saveCommandToDB(commandName, data)

                print("\nCommands count: " + str(len(result)))
                print("Command finished.")
                return True
            except Exception as e:
                print("scraping failed due to: " + e)
        else:
            return False  # failed cloning the repo
