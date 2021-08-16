""" Модуль содержит функции, задействованные в API """

import threading
from traceback import format_exc
import os
from wengine.functions import start_functions


def execute_api_method(core_method, *args, **kwargs):
    """ Выполнить метод core_method ядра core, передать ему аргументы """
    threading.Thread(target=core_method, args=args, kwargs=kwargs).start()
    response = {'status': True, 'info': 'Поток выполнения запущен успешно'}
    return response


def try_auth_user(sqlshell, username, password, *args, **kwargs):
    """ Попытка авторизации. Возвращает
    {'status': 'success', info:[{'role':...,'password':..., 'id':...}],
    если все прошло успешно. status - failed 0, если пароль или логин неверные
    """
    command = "SELECT password = crypt('{}', password) as auth_status, id " \
              "FROM users where username='{}'"
    command = command.format(password, username)
    response = sqlshell.get_table_dict(command)
    if response['info'][0]['auth_status']:
        return response
    else:
        return {'status': 'failed', 'info': None}


def restart_core(qdw, *args, **kwargs):
    """ Перезапустить GCore"""
    db_settins = start_functions.import_db_settings(qdw)
    command = 'systemctl restart runcore'
    command = "echo {}|sudo -S {}".format(db_settins['sudo_password'],
                                          command)
    os.system(command)
