""" Модуль содержит функционал, требуемый для начала работы WEngine """


def import_db_settings(sql_shell, settings_table='gcore_settings'):
    """ Возвращает словарь, содержащий настройки GCore """
    new_dict = {}
    command = "SELECT * FROM {}".format(settings_table)
    response = sql_shell.get_table_dict(command)
    if response['status'] == 'success':
        for el in response['info']:
            new_dict[el['key']] = el['value']
    return new_dict
