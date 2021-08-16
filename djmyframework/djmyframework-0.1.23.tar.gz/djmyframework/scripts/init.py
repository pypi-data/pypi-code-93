#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil

djframework_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def init_djframework():
    from django.core.management.utils import get_random_secret_key

    settings_text = '''
from __future__ import absolute_import

import os
import sys

DEBUG = True
SECRET_KEY = '%s'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

APPS = ['djmyframework','myadmin', 'analysis', 'celery_task', 'log_def', 'upload', 'sync_model', 'ws_gateway','dynamic_settings']

APPS_ROOT = os.path.join(BASE_DIR, 'apps')

from djmyframework.settings import *
LANGUAGES = (
        ('de', _('German')),
        ('en', _('English')),
        ('zh-hans', _('简体')),
        ('zh-hant', _('繁体')),
)

PROJECT_ROOT = BASE_DIR

    ''' % get_random_secret_key()

    target_project_dir = os.getcwd()
    dir_name = 'config'
    config_dir = os.path.join(djframework_dir, dir_name)
    project_dir = target_project_dir
    project_conf_dir = os.path.join(project_dir, dir_name)

    requirements_file = os.path.join(target_project_dir, 'requirements.txt')
    settings_file = os.path.join(project_dir, 'settings.py')
    apps_dir = os.path.join(project_dir, 'apps')

    if not os.path.isfile(requirements_file):
        open(requirements_file, 'w').write('')

    if not os.path.isdir(apps_dir):
        os.mkdir(apps_dir)

    project_configfile_dir = os.path.join(project_dir, 'configfile')
    if not os.path.isdir(project_configfile_dir):
        shutil.copytree(os.path.join(djframework_dir, 'configfile'), project_configfile_dir)

    if not os.path.isdir(project_conf_dir):

        shutil.copytree(config_dir, project_conf_dir)
        print('add config %s' % project_conf_dir)

        shutil.copyfile(os.path.join(djframework_dir, 'wsgi.py'), os.path.join(project_dir, 'wsgi.py'))
        shutil.copyfile(os.path.join(djframework_dir, 'asgi.py'), os.path.join(project_dir, 'asgi.py'))
        shutil.copyfile(os.path.join(djframework_dir, 'manage.py'), os.path.join(project_dir, 'manage.py'))
        if not os.path.isfile(settings_file):
            open(os.path.join(project_dir, 'settings.py'), 'w').write(settings_text)

        framework_link_dir = os.path.join(project_dir, 'framework')
        if not os.path.isdir(framework_link_dir):
            os.symlink(os.path.join(djframework_dir, 'framework'),framework_link_dir)

        djframework_link_dir = os.path.join(project_dir, os.path.split(djframework_dir)[-1])
        if not os.path.isdir(djframework_link_dir):
            os.symlink(os.path.join(djframework_dir), djframework_link_dir)


    else:
        raise Exception('%s already exists' % project_conf_dir)


if __name__ == '__main__':
    os.system('yum install openldap-devel')
    os.system('pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --ignore-installed')
