from portdatasplitter import settings as s
import serial


def get_data_from_port(port):
    """ Прочитать и вернуть данные из переданного порта """
    try:
        data = port.readline()
    except serial.serialutil.SerialException:
        # Если не выйдет - вернуть код ошибки
        data = s.scale_disconnected_code
    return data


def get_manual_set_value(value, value_def='101010'):
    """ Вернуть отформатированное значение, установленное вручную. Если оно не установлено - вернуть value_def"""
    if not value and value != 0:
        return value_def
    return value


def get_format_send_message(weight_data, port_name=None, test_mode=None,
                            manual_value_set=True, *args, **kwargs):
    locals_copy = locals().copy()
    locals_copy.pop('kwargs')
    locals_copy.pop('args')
    locals_copy.update(kwargs)
    return locals_copy


def set_manual_value(ports_dict, manual_value, port_name=None, *args, **kwargs):
    """ Вручную установить значение manual_value, которое будет отправляться подписчикам от якобы port_name, если
    port_name не указан, то это значение будет отправляться от всех портов из словаря ports_dict
    """
    return change_manual_value(set_port_manual_value, ports_dict, manual_value, port_name)


def unset_manual_value(ports_dict, manual_value, port_name=None, *args, **kwargs):
    """ Вручную установить значение manual_value=None, которое будет отправляться подписчикам от якобы port_name, если
    port_name не указан, то это значение будет отправляться от всех портов из словаря ports_dict
    """
    return change_manual_value(unset_port_manual_value, ports_dict, manual_value, port_name)


def change_manual_value(change_function, ports_dict, manual_value, port_name=None, *args, **kwargs):
    """ Вручную установить значение manual_value, которое будет отправляться подписчикам от якобы port_name, если
    port_name не указан, то это значение будет отправляться от всех портов из словаря ports_dict.
    Значения меняются функцие change_function, которое может как устанавливать отправку, так ее и отключать
    """
    if port_name:
        try:
            return change_function(ports_dict, manual_value, port_name)
        except KeyError:
            return {'status': False,
                    'info': 'Проверьте правильно названия порта! Доступно: {}'.format(ports_dict)}
    else:
        for port_name in ports_dict:
            change_function(ports_dict, manual_value, port_name)
        return {'status': True,
                'info': 'Были изменены manual_value={} для всех портов.'.format(manual_value)}


def set_port_manual_value(ports_dict, manual_value, port_name, *args, **kwargs):
    """ Установить в словаре ports_dict ({'port_name': {'port_object': object, 'manual_value': None,
    'manual_value_set': False}}),в значение ключа port_name, значение ключа 'manual_value' = True """
    return change_port_manual_value(ports_dict, manual_value, port_name, True, *args, **kwargs)


def unset_port_manual_value(ports_dict, port_name, *args, **kwargs):
    """ Установить в словаре ports_dict ({'port_name': {'port_object': object, 'manual_value': None,
    'manual_value_set': False}}),в значение ключа port_name, значение ключа 'manual_value' = True """
    return change_port_manual_value(ports_dict, None, port_name, False, *args, **kwargs)


def change_port_manual_value(ports_dict, manual_value, port_name, manual_value_set, *args, **kwargs):
    """ Установить в словаре ports_dict ({'port_name': {'port_object': object, 'manual_value': None,
    'manual_value_set': False}}),в значение ключа port_name, значение ключа 'manual_value' = manual_value """
    ports_dict[port_name]['manual_value'] = manual_value
    ports_dict[port_name]['manual_value_set'] = manual_value_set
    return {'status': True, 'info': 'Для порта {} установлено manual_value={}, manual_value_set={}'.format(port_name,
                                                                                                           manual_value,
                                                                                                           manual_value_set)}


def get_last_data_dict(data_list: list, port_name=None, *args, **kwargs):
    """ Возвращает последний массив из списка массивов data_list. Если указан port_name возвращает такой последний
    массив, у которого port_name=port_name """
    if port_name:
        return get_data_time_by_port(data_list, port_name)
    else:
        return sort_data_list_by_date(data_list)[-1]


def sort_data_list_by_date(data_list: list, *args, **kwargs):
    """ Сортирует список массивов данных по дате их создания. """
    return sorted(data_list, key=get_data_time,  *args, **kwargs)


def get_data_time_by_port(data_list: list, port_name: str, *args, **kwargs):
    """ Вернуть последний массив данных из нужного порта """
    # reverse, что бы самые свежие данные были вначале
    data_list = sort_data_list_by_date(data_list, reverse=True)
    for data in data_list:
        # Как только наткнулись на нужный - вернули
        if data['port_name'] == port_name:
            return data
    # Если же данных с порта нет, вернуть уведомление
    return {'status': False, 'info': 'Нет данных с порта {}.'.format(port_name)}


def get_data_time(data_dict: dict, created_date_name='creation_date', *args, **kwargs):
    """ Возвращает дату создания (created_date_name) массива данных (data_dict). """
    return data_dict[created_date_name]

