""" Содержит общие, многоразовые функции"""
from weighting_platform.functions import logging_functions
from weighting_platform import cfg
from qpi.main import QPI
from wsqluse.wsqluse import Wsqluse


def form_point_name(course: str, point_type_str: str):
    """ Формирует название точки доступа, который передается в QSB, что бы тот его
    открыл. Как правило, оно состоит из направления (course) который передает
    QSB (оно может быть external или internal). Название точки формируется
    сложиение направления и слова point_type_str, т.е должно получиться что-то типа:
    EXTERNAL_GATE или INTERNAL_PHOTOCELL"""
    gate_name_full = '_'.join((course.upper(), point_type_str.upper()))
    return gate_name_full


def get_change_percent(first_weight, second_weight):
    """ Вернуть процент изменения second_weight относительно first_weight """
    difference = second_weight - first_weight
    percent = difference/first_weight * 100
    return abs(percent)


def if_dlinnomer_moved(first_weight, second_weight, min_percent=30):
    """ Возвращает True, если понимает, что машина переместилась по весам
    (весы изменились более чем на min_percent процентов) """
    percent = get_change_percent(first_weight, second_weight)
    if percent >= min_percent:
        return True


def send_round_status(stage, status=None, timer=None, weight=None):
    """ Отправляет статус заезда (stage) и дополнительную информацию для
     отображения статуса заезда.
    STAGE - BEFORE_WEIGHING; WEIGHING; AFTER_WEIGHING
    INFO - """
    info = {'STAGE': stage.upper(),
            'STATUS': status.upper(),
            'TIMER': timer,
            'WEIGHT': weight}
    send_status(info)


def send_status(*msg):
    """ Используется в других функциях для вывода статуса в стандартный поток,
    либо для отправки статуса выполнения клиентам """
    save_current_round_info(**msg[0])
    global sql_shell
    logging_functions.fix_event(sql_shell, cfg.current_round)
    info = {'status': True, 'info': msg[0], 'core_method': 'round_status'}
    print("ROUND_STATUS", info)
    cfg.qodex_pi.broadcast_sending(info)


def save_current_round_info(**kwargs):
    """ Сохраняет информацию о текущем раунде взвешивания в модуль cfg """
    for k, v in kwargs.items():
        cfg.current_round[k] = v
    return cfg.current_round


def clear_current_round():
    cfg.current_round = {'record_id': None, 'has_gross': None, 'auto_id': None}

sql_shell = Wsqluse('wdb', 'watchman', 'hect0r1337', '192.168.100.118')
