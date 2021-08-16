""" Модуль содержит все функции, необходимые для взвешивания """
import time
from weighting_platform.functions import general_functions


def get_weight_single(weight_splitter):
    """ Единоразово вернуть текущий вес в строковом представлении """
    weight = weight_splitter.get_value()
    return int(weight['weight_data'])


def check_weight_stable(weight_slice, admitting_spikes=50):
    """
    Проверить список, все ли элементы равны друг другу в пределах
    admitting_spikes (50 кг обычно)
    :param weight_slice: список строк, означающих весы
    :param admitting_spikes: допустимая погрешность
    :return:
    """
    weight_slice = iter(weight_slice)
    try:
        first = next(weight_slice)
    except StopIteration:
        return True
    return all(int(first) in range(int(rest) - admitting_spikes,
                                   int(rest) + admitting_spikes) for rest in
               weight_slice)


def get_stable_data(weight_splitter, weight_count=5, stable_min_weight=500,
                    start_diff=50, wait_time=60):
    """ Вернуть стабилизированный вес. """
    weight_slice = []
    while wait_time != 0:
        # Сначала набираем нужное количество взвешиваний
        weight_now = get_weight_single(weight_splitter)
        weight_slice.append(weight_now)
        #weight_changed = if_weight_changed(start_weight, weight_now, start_diff)
        if len(weight_slice) >= weight_count:
            # Как только набрали, ждем, пока вес стабилизуется
            general_functions.send_round_status(stage='weighing',
                                                status='stabling_weight',
                                                timer=0)
            target_slice = weight_slice[-weight_count:]
            while not check_weight_stable(target_slice) and \
                    check_min_stable_weight(weight_now, stable_min_weight):
                weight_now = get_weight_single(weight_splitter)
                weight_slice.append(weight_now)
                target_slice = weight_slice[-weight_count:]
            return weight_slice[-1]
        wait_time -= 1
        time.sleep(1)


def if_weight_changed(start_weight: int, weight_now: int, start_diff: int):
    """ Сравнивает изначальный вес на весах (start_weight) и
    текущий (weight_now), если обнаруживается, что разница между ними больше,
    чем start_diff, то возвращается True """
    diff = start_weight - weight_now
    diff_abs = abs(diff)
    if diff_abs >= start_diff:
        return True


def check_min_stable_weight(weight: int, stable_min_weight=500):
    """ Возвращает True, если заданный вес weight больше минимального значения
    stable_min_weight"""
    if weight >= stable_min_weight:
        return True
