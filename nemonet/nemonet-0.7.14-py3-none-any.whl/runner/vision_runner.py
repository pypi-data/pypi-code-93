# Created by Jan Rummens at 3/12/2020
from nemonet.engines.graph import Graph
from nemonet.engines.sequencer import Sequences
from nemonet.seleniumwebdriver.commands import Command
from nemonet.screencast.recording import ScreenRecorder
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import time

selenium_config = {
    "driver": {
        "headless": False,
        "browser": "chrome",
        "type": "selenium"
    },
    "recording": {
        "switch": False
    }
}

class TestDriver:

    def open(self):
        pass

    def close(self):
        pass

class ChromeTestDriver( TestDriver ):

    def __init__(self):
        self.driver = None
        self.options = None

    def set_options(self ,options):
        self.options = options

    def open(self):
        if self.options == None:
            self.driver = webdriver.Chrome()
            self.driver.maximize_window()
        else:
            chrome_local_state_prefs = {'browser.enabled_labs_experiments': self.options["experimental_flags"] }
            chrome_options = Options()
            chrome_options.add_experimental_option('localState', chrome_local_state_prefs)
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.maximize_window()

    def close(self):
        self.driver.close()

    def get_native_driver(self):
        return self.driver


class Runner( object ):

    def __init__( self, runner_config=None):
        self.data = None
        self.driver = None
        self.has_passed = False

        if runner_config == None:
            self.data = selenium_config
        else:
            with open(runner_config, 'r') as fp:
                self.data = json.load(fp)

        self.__configuration__()

    def __configuration__(self):
        if self.data["driver"]["type"] == "selenium":
            if self.data["driver"]["browser"] == "chrome":
                self.driver = ChromeTestDriver()
                if ('options' in self.data["driver"]) and ('experimental_flags' in self.data["driver"]["options"].keys() ):
                    self.driver.set_options( self.data["driver"]["options"] )
                self.driver.open()

    def turn_on_recording(self):
        if not self.is_recording:
            self.screenrecording.start()
            self.is_recording = True
            time.sleep(0.25)

    def turn_off_recording(self):
        if self.is_recording:
            self.screenrecording.stop()
            time.sleep(0.25)

    def scenario_passed(self):
        return self.has_passed

    def execute_scenario(self, xml_files_name):
        if self.data["recording"]['switch']:
            self.is_recording = False
            self.screenrecording = ScreenRecorder()
            self.turn_on_recording()
        graph = Graph()
        graph.build(xml_files_name)
        seqences = Sequences(graph)
        commands = Command(self.driver.get_native_driver())
        commands.executeSequences(seqences, graph)
        self.driver.close()
        self.has_passed = True
