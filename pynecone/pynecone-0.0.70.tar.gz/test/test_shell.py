import unittest
from pynecone import Shell, Cmd


class TestCmd(Cmd):

    def __init__(self):
        super().__init__('cmd')

    def add_arguments(self, parser):
        parser.add_argument('arg')

    def get_help(self):
        return 'test cmd'

    def run(self, args):
        return args.arg


class TestShell(Shell):

    def __init__(self):
        super().__init__('shell')

    def get_commands(self):
        return [TestCmd()]

    def add_arguments(self, parser):
        pass

    def get_help(self):
        return 'test shell'


class TestRootShell(Shell):

    def __init__(self):
        super().__init__('rootshell')

    def get_commands(self):
        return [TestShell()]

    def add_arguments(self, parser):
        pass

    def get_help(self):
        return 'test root shell'


class TestSuperRootShell(Shell):

    def __init__(self):
        super().__init__('superrootshell')

    def get_commands(self):
        return [TestRootShell()]

    def add_arguments(self, parser):
        pass

    def get_help(self):
        return 'test superroot shell'


class ShellTestCase(unittest.TestCase):

    def test_command_should_return_value(self):
        self.assertEqual(TestCmd()(['hello']), 'hello')

    def test_shell_should_return_value(self):
        self.assertEqual(TestShell()(['cmd', 'hello']), 'hello')

    def test_root_shell_should_return_value(self):
        self.assertEqual(TestRootShell()(['shell', 'cmd', 'hello']), 'hello')

    def test_superroot_shell_should_return_value(self):
        self.assertEqual(TestSuperRootShell()(['rootshell', 'shell', 'cmd', 'hello']), 'hello')


if __name__ == '__main__':
    unittest.main()
