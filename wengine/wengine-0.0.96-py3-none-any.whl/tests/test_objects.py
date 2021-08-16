""" Модуль содержит объекты, которые используются во всех тестах """

from wsqluse.wsqluse import Wsqluse


sql_shell = Wsqluse('wdb', 'watchman', 'hect0r1337', '192.168.100.118')
