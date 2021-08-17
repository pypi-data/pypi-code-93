""" Модуль содержит все функции, необходимые для работы с фотоэлементами """
import datetime
import time
from weighting_platform.functions import general_functions


def start_course_trace(qsb, course: str, spare_time=4, waiting_time=60,
                     start_datetime=datetime.datetime.now()):
    photocell_name = general_functions.form_point_name(course, 'PHOTOCELL')
    general_functions.send_round_status(stage='before_weighing',
                                        status='start_photocell_trace_{}'.format(
                                            photocell_name),
                                        timer=waiting_time)
    return photocell_tracer(qsb, photocell_name, spare_time, waiting_time,
                            start_datetime)


def photocell_tracer(qsb, photocell_name: str, spare_time=4, waiting_time=60,
                     start_datetime=datetime.datetime.now()):
    """ Функция, следящая за фотоэлементами. Она извлекает ежесекундно
    состояние заданного фотоэлменета, если он понимает,
    что с начала слежения фотоэлементы были заблокированы (lock_state),
    а затем осовободились (normal_state), то он ждет spare_time секунд,
    и, если за это время фотоэлементы больше не были блокированы, возвращает True.
    Если же за это время spare_time фотоэлементы блокировались вновь - таймер
    сбрасывается.
    Если же фотоэлементы не были блокированы
    то он возвращает False """

    # Получаем наименование состояний фотоэлементов в СКУД
    while waiting_time != 0:                           # Запускаем цикл
        # Нас сейчас интересует именно состояние блокировки
        lock_state_info = qsb.get_last_lock_info(photocell_name)
        lock_state_last_time = lock_state_info['last_change_timestamp']
        if not lock_state_last_time:
            # Если не известна дата последней блокировки фотоэлемента
            lock_state_last_time = datetime.datetime(1997, 8, 24)
        if lock_state_last_time > start_datetime:
            # Значит фотоэлементы заблокировались после начала слежения
            general_functions.send_round_status(stage='before_weighing',
                                                status='photocell_was_blocked_{}'.format(photocell_name),
                                                timer=waiting_time)
            result = normalize_waiting_cycle(qsb, photocell_name, spare_time)
            return result
        else:
            time.sleep(1)
            waiting_time -= 1
            general_functions.send_round_status(stage='before_weighing',
                                                status='wait_photocell_block_{}'.format(photocell_name),
                                                timer=waiting_time)
    return False


def normalize_waiting_cycle(qsb, photocell_name, spare_time=4, relieve_timer=60):
    """ Цикл, наступающий после того, как фотоэлемент был заблокирован.
    Данный цикл крутится до тех пор, пока фотоэлемент не будет нормализован,
    либо не пройдет таймер """
    while relieve_timer != 0:
        # Теперь следим за состоянием нормализации
        general_functions.send_round_status(stage='before_weighing',
                                            status='wait_photocell_relieve_{}'.format(
                                                photocell_name),
                                            timer=relieve_timer)
        normal_state_info = qsb.get_last_normal_info(photocell_name)
        if normal_state_info['current']:
            general_functions.send_round_status(stage='before_weighing',
                                                status='photocell_was_relieved_{}'.format(
                                                    photocell_name),
                                                timer=relieve_timer)
            # Если нормализация наступила после блокировки
            result = spare_waiting_cycle(qsb, photocell_name, spare_time)
            return result
        else:
            # Если же нормализации не было (машина просто заблокировала
            # и стоИт, то ждем деблокировки
            time.sleep(1)
            relieve_timer -= 1

def spare_waiting_cycle(qsb, photocell_name, spare_time=4):
    """ Цикл, начинающийся после того, как фотоэлементы нормализовались.
    По сути, ее задача - ждать, не заблокируются ли фотоэлементы еще в течение
    spare_time секунд (например, машина проезжая линию фотоэлменетов, блокирует
    их своим кузовом, но по мере движения, линия фотоэлементов на короткое
    время восстанавливается, когда перед фотоэлементами появляется
    пустое пространство между кузовом и прицепом. И вот что бы в это время
    цикл ожидания не прервался, система ждет spare_time, что бы убедиться, что
    машина точно заехала на весы полностью)"""
    spare_timer = spare_time  # Ставим таймер
    while spare_timer != 0:
        normal_state_info = qsb.get_last_normal_info(photocell_name)
        if normal_state_info['current']:
            general_functions.send_round_status(stage='before_weighing',
                                                status='PHOTOCELL_AFTER_RELIEVE_WAIT_{}'.format(
                                                    photocell_name),
                                                timer=spare_timer)
            spare_timer -= 1
        else:
            print('Прервалось... Ожидаем нормализацию снова')
            general_functions.send_round_status(stage='before_weighing',
                                                status='photocell_was_blocked_again_{}'.format(
                                                    photocell_name),
                                                timer=spare_timer)
            spare_timer = spare_time
        time.sleep(1)
    return True


def barrier_gate_decorator(func):
    """ Декоратор, оборачивающий все функции работы со шлагбаумами """
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
    return wrapper


def form_gate_name(course, gate_name_str='GATE'):
    """ Формирует название шлагбаума, который передается в QSB, что бы тот его
    открыл. Как правило, оно состоит из направления (course) который передает
    QSB (оно может быть external или internal). Название шлагбаума формируется
    сложиение направления и слова gate, т.е должно получиться что-то типа:
    EXTERNAL_GATE"""
    gate_name_full = '_'.join((course.upper(), gate_name_str.upper()))
    return gate_name_full
