#!/usr/bin/env python3

from bs4 import BeautifulSoup
from json import loads
from os import listdir, mkdir
from os.path import abspath, exists, join
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FO
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from shutil import move, rmtree
from tempfile import gettempdir
from time import sleep
from traceback import print_exc

def print_driver_instructions():
    """
    Print instructions for installing Selenium drivers.
    """
    print("This program uses Selenium to process JavaScript.")
    print("To run, you must install Selenium web drivers.")
    print("Download the drivers for your preferred browser:")
    print("")
    print("Firefox:")
    print("https://github.com/mozilla/geckodriver/releases")
    print("")
    print("Copy Selenium driver(s) to your PATH directory.")
    print("(On Windows, find PATH with command \"echo %PATH%\" )")
    print("(On Mac/Linux, find PATH with command \"echo $PATH\" )")

class HeavyConnect:

    def __init__(self, headless:bool=True):
        """
        Initialize the HeavyConnect class.
        """
        self.initialize_driver(headless)

    def initialize_driver(self, headless:bool=True):
        """
        Starts the Selenium driver.

        :param headless: Whether to run in headless mode, defaults to True
        :type headless: bool, optional
        """
        try:
            # SET UP TEMP DIR
            self.tempdir = abspath(gettempdir())
            self.tempdir = abspath(join(self.tempdir, "dvk_connection"))
            if not exists(self.tempdir):
                mkdir(self.tempdir)
            # TRY FIREFOX DRIVER
            options = FO()
            options.headless = headless
            options.page_load_strategy = "none"
            # SET DOWNLOAD FOLDER OPTIONS
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.download.useDownloadDir", True)
            options.set_preference("browser.download.dir", self.get_download_dir())
            options.set_preference("browser.download.viewableInternally.enabledTypes", "")
            options.set_preference("browser.helperApps.neverAsk.saveToDisk", "image/gif;image/jpeg;image/png;image/webp;image/svg+xml")
            # CREATE DRIVER
            profile = webdriver.FirefoxProfile()
            log_file = abspath(join(self.tempdir, "dvkgeckodriver.log"))
            self.driver = webdriver.Firefox(
                    options=options,
                    service_log_path=log_file,
                    firefox_profile=profile)
        except WebDriverException:
            # PRINTS INSTRUCTIONS FOR GETTING SELENIUM DRIVER
            self.driver = None
            print_driver_instructions()

    def get_download_dir(self) -> str:
        """
        Creates and returns a directory for storing downloaded files.

        :return: File path of the download directory
        :rtype: str
        """
        ddir = abspath(join(self.tempdir, "downloads"))
        if exists(ddir):
            rmtree(ddir)
        mkdir(ddir)
        return ddir

    def get_page(self,
                    url:str=None,
                    element:str=None,
                    timeout:int=10) -> BeautifulSoup:
        """
        Connects to a URL and returns a BeautifulSoup object.
        Capable of loading JavaScript, AJAX, etc.

        :param url: URL to retrieve, defaults to None
        :type url: str, optional
        :param element: XPATH Element to wait for, defaults to None
        :type element: str, optional
        :param timeout: Seconds before timeout, defaults to 10
        :type timeout: int, optional
        :return: BeautifulSoup object for the web page
        :rtype: BeautifulSoup
        """
        # RETURN NONE IF URL OR LOADED DRIVER IS INVALID
        if url is None or url == "" or self.driver is None:
            return None
        # ATTEMPT LOADING WEB PAGE
        try:
            self.driver.get(url)
            # WAIT FOR ELEMENT TO LOAD, IF SPECIFIED
            if element is not None and not element == "":
                WebDriverWait(self.driver, timeout).until(
                     EC.presence_of_all_elements_located((By.XPATH, element)))
            bs = BeautifulSoup(self.driver.page_source, "lxml")
            return bs
        except:
            return None
        return None

    def get_json(self, url:str=None) -> dict:
        bs = self.get_page(url, "//div[@id='json']")
        try:
            element = bs.find("div", {"id": "json"})
            html = element.get_text()
            # CONVERT TO JSON
            json = loads(html)
            return json
        except:
            return None

    def get_driver(self) -> webdriver:
        """
        Returns the current Selenium Web Driver

        :return: Selenium Web Driver
        :rtype: webdriver
        """
        return self.driver

    def close_driver(self):
        """
        Closes the Selenium driver if possible.
        """
        if self.driver is not None:
            self.driver.close()

    def download(self, url:str=None, file_path:str=None) -> dict:
        """
        Downloads a file from given URL to given file.

        :param url: Given URL, defaults to None
        :type url: str, optional
        :param file_path: Given file path, defaults to None
        :type file_path: str, optional
        :return: Headers retrieved from the given media URL
        :rtype: dict
        """
        try:
            # CHECK IF PARAMETERS ARE VALID
            assert url is not None
            assert file_path is not None
            # GET DOWNLOAD DIRECTORY
            directory = self.get_download_dir()
            self.get_page(url, "//img")
            # DOWNLOAD FILE TO TEMP DOWNLOAD DIRECTORY
            js_command = "var link = document.createElement(\"a\");"\
                         + "link.href = \"" + url + "\";"\
                         + "link.download = \"d.dvk\";"\
                         + "document.body.appendChild(link);link.click();"
            self.driver.execute_script(js_command)
            # WAIT UNTIL FILE STARTED DOWNLOADING OR TIMES OUT
            sec = 0
            while sec < 10 and len(listdir(directory)) == 0:
                sleep(1)
                sec += 1
            assert not len(listdir(directory)) == 0
            # WAIT UNTIL FILE FINISHED DOWNLOADING OR TIMES OUT
            sec = 0
            while sec < 10 and len(listdir(directory)) > 1:
                sleep(1)
                sec += 1
            assert len(listdir(directory)) == 1
            # GET DOWNLOADED FILE
            file = abspath(join(directory, listdir(directory)[0]))
            assert exists(file)
            # WAIT
            sleep(2)
            # MOVE FILE
            move(file, abspath(file_path))
        except:
            self.get_download_dir()
