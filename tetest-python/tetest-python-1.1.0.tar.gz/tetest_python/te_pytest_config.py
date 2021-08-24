import sys

class te_pytest_config:
    def __init__(self, confJSON=None):
        self.confJSON=confJSON

    def pytest_addoption(self, parser):
        parser.addoption("--TaskID", help="[TE] Task id from client agent", action="store")
        parser.addoption("--Token",  help="[TE] Backend api token", action="store")
        parser.addoption("--BuildID",  help="[TE] Build ID by task execution")
        parser.addoption("--TimeSpan", help="[TE] Time span for task", action="store")
        parser.addoption("--Config", help="[TE] Config json file path", action="store")
