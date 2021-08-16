""" Различные механизмы (функции, выполняющую сложную работу, включающую
 работу других модулей """
import threading
import time
import datetime
from weighting_platform import settings
from weighting_platform import cfg
from weighting_platform.functions import weigthing_functions
from weighting_platform.functions import barrier_functions
from weighting_platform.functions import general_functions
from weighting_platform.functions import logging_functions


def close_barrier_after_round(qsb, weight_splitter, course, admit_weight=100,
                              check_frequency=1, block_timeout=5):
    """ Механизм закрытия шлагбаума после взвешивания. Отличается от обычного
    закрытия тем, что шлагбаум не закроется, пока весы показывают вес, больший
    чем admit_weight (условный вес машины). """
    photocell_name = general_functions.form_point_name(course, 'PHOTOCELL')
    while weigthing_functions.get_weight_single(weight_splitter) > admit_weight \
            or not qsb.get_last_normal_info(photocell_name)['current']\
            or datetime.datetime.now() < qsb.get_last_normal_info(photocell_name)['last_change_timestamp'] + datetime.timedelta(seconds=block_timeout):
        general_functions.send_round_status(stage='after_weighing',
                                            status='waiting_escaping',
                                            weight=weigthing_functions.get_weight_single(weight_splitter),
                                            timer=0)
        #print("BLOCK, ибо weight:", weigthing_functions.get_weight_single(weight_splitter) > admit_weight,
        #     '\n',weigthing_functions.get_weight_single(weight_splitter),
        #      '\nCurrent:', not qsb.get_last_normal_info(photocell_name)['current'],
        #      '\n',datetime.datetime.now() < qsb.get_last_normal_info(photocell_name)['last_change_timestamp'] + datetime.timedelta(seconds=block_timeout))
        time.sleep(check_frequency)
    barrier_functions.close_barrier(qsb, course)


def open_first_barrier(qsb, first_gate: str, course: str):
    """ Открыть первый шлагбаум согласно протоколу проезда car_protocol,
     и направлению приезда авто course """
    first_gate_course = settings.protocol_gate_description_dict[course][
        first_gate]
    barrier_functions.open_barrier(qsb, course=first_gate_course)


def close_both_gates(qsb):
    """ Закрыть оба шлагбаума """
    for course in list(settings.protocol_gate_description_dict.keys()):
        barrier_functions.close_barrier(qsb, course)


def open_both_gates(qsb):
    """ Открыть оба шлагбаума """
    for course in list(settings.protocol_gate_description_dict.keys()):
        barrier_functions.open_barrier(qsb, course)


def dlinnomer_scaling_mechanism(weight_splitter, first_weight, wait_time=60):
    """ Механизм измерения машин по спец. протоколу длинномер.
    Вызывается для второго взвешивания (взвешивания прицепа).
    Механизму передается вес кузова (first_weight), после чего, он начианет
    следить, что бы на весах произошли скачки в пределах 30% от first_weight
    (это будет означать, что машина поехала дальше и встала прицепом). После
    этого система опять начинает ловаить вес (второй), затем возваращает сумму
    первого и второго весов """
    general_functions.send_round_status(stage='weighing',
                                        status='first_weight_got',
                                        weight=first_weight,
                                        timer=wait_time)
    while wait_time != 0:
        new_weight = weigthing_functions.get_weight_single(weight_splitter)
        wait_time -= 1
        general_functions.send_round_status(stage='weighing',
                                            status='waiting_auto_moving',
                                            timer=wait_time)
        if general_functions.if_dlinnomer_moved(first_weight, new_weight):
            second_weight = weigthing_functions.get_stable_data(weight_splitter)
            amount_weight = new_weight + second_weight
            general_functions.send_round_status(stage='weighing',
                                                status='amount_weight_got',
                                                weight=amount_weight,
                                                timer=0)
            return amount_weight
    amount_weight = weigthing_functions.get_weight_single(weight_splitter)
    return amount_weight


def log_auto_delete_thread(sql_shell):
    """ Запускает параллеельный поток, который удаляет отчеты, старше 30 дней,
    раз в сутки"""
    del_thread = threading.Thread(target=log_auto_delete_cycle,
                                  args=(sql_shell,))
    del_thread.start()


def log_auto_delete_cycle(sql_shell, interval=8600):
    """ Автоматически удаляет логи, старше одного месяца, с интервалом в
    interval секунд"""
    logging_functions.delete_old_logs(sql_shell)
    time.sleep(interval)


def start_log(sql_shell):
    """ Начать логгирование """
    has_gross = cfg.current_round['has_gross']
    if has_gross:
        log_id = logging_functions.init_tare_log(sql_shell)
    else:
        log_id = logging_functions.init_gross_log(sql_shell)
    return log_id

