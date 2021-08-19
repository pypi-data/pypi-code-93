#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
import codecs
import os
import re
import subprocess
import sys

from fias.version import __version__
from setup_kwargs import setup_kwargs


def execute(cmd):
    assert isinstance(cmd, (list, tuple)), 'cmd must be a list or tuple'

    proc = subprocess.Popen(cmd, cwd=os.path.abspath(os.path.dirname(__name__)),
                            stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    return proc.communicate()


def check_tag_exists():
    tag_out, tag_err = execute(['git', 'tag', '-l', __version__])

    if tag_out.strip():
        print("Уже существует тег для версии: {0}.".format(__version__))
        sys.exit()


PY3 = sys.version_info[0] == 3

sys.path.insert(0, '..')

if sys.argv[-1] == 'test':
    req_split = re.compile(r'[a-z_][a-z0-9_]+', re.I | re.U | re.M)

    req_file = codecs.open('requirements.txt', mode='r').read()
    test_req_file = codecs.open('test_requirements.txt', mode='r').read()
    test_requirements = req_split.findall(req_file) + req_split.findall(test_req_file)

    try:
        modules = list(map(__import__, test_requirements))
    except ImportError as e:
        err_msg = e.msg.replace("No module named ", "")
        msg = "%s is not installed. Install your test requirments." % err_msg
        raise ImportError(msg)

    os.system('py.test')
    sys.exit()


if sys.argv[-1] == 'tag':
    check_tag_exists()

    os.system("git tag -a %s -m 'version %s'" % (__version__, __version__))
    os.system("git push --tags")
    sys.exit()


if sys.argv[-1] == 'publish':
    check_tag_exists()

    tox_out, tox_err = execute(['tox'])
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout.buffer.write(tox_out)
    else:
        sys.stdout.write(tox_out)

    if 'FAILURES' in str(tox_out):
        print('Не все тесты прошли. Нельзя публиковать!')
        sys.exit()

    os.system("python setup.py sdist upload")
    os.system("python setup.py bdist_wheel upload")
    print("Не забудь добавить тег:")
    print("  git tag -a %s -m 'ver.%s'" % (__version__, __version__))
    print("  git push --tags")
    print("Или:")
    print(" python setup.py tag")
    sys.exit()

setup(**setup_kwargs)
