""" Модуль содержит тестовые объеткы, используемые в других тестах """
from gravityRecorder.main import Recorder
from wsqluse.wsqluse import Wsqluse

test_recorder = Recorder('wdb', 'watchman', 'hect0r1337', '192.168.100.118')
test_sqlshell = Wsqluse('wdb', 'watchman', 'hect0r1337', '192.168.100.118')

