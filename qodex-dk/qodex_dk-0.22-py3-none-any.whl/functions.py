def extract_supported_methods(sdk_cliend):
    """ Извлечь все методы из самого API """
    command = {'get_methods': None}
    sdk_cliend.send_data(command)
    response = sdk_cliend.get_data()
    return response


def execute_method(sdk_client, methods_dict, method_name, get_response=False, *args, **kwargs):
    """ Сформировать и отправить запрос """
    method = get_method(methods_dict, method_name, *args, **kwargs)
    sdk_client.send_data(method)
    if get_response:
        return sdk_client.get_data()


def get_method(methods_dict, method_name, *args, **kwargs):
    """ Сделать шаблонный запрос  """
    method = {'method': method_name,  'data': kwargs}
    return method


def get_method_unactual(methods_dict, method_name, *args, **kwargs):
    """ Сделать шаблонный запрос  """
    try:
        method_from_dict = methods_dict[method_name]
    except KeyError:
        return {'status': False, 'info': 'Метод {} не поддерживается в QDK. Что бы получить список поддреживаемых '
                                            'методов выполните get_qdk_methods.'.format(method_name)}
    try:
        all_arguments = method_from_dict['kwargs']
    except KeyError:
        all_arguments = {}
    all_arguments.update(kwargs)
    method = {'method': method_from_dict['command'],  'data': all_arguments}
    return method


def expand_support_methods(current_methods_dict, new_methods_dict):
    """ Обновить существующий словарь методов QPI (current_methods_dict) добавочным словарем new_methods_dict """
    current_methods_dict.update(new_methods_dict)
    return current_methods_dict
