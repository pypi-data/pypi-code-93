from savvihub.cli.commands.main import __version__
from tests.conftest import BaseTestCase


class BasicTest(BaseTestCase):
    def test_version(self):
        result = self.runner.invoke(['--version'])
        assert f'SavviHub CLI Version: {__version__}' in result.stdout

    def test_ping(self):
        result = self.runner.invoke(['ping'])
        assert 'Response code: 200' in result.stdout
        assert 'Response text: pong' in result.stdout
