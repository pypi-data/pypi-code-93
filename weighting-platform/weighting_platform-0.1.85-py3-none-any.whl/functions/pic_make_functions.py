""" Модуль содержит все функции для фотографирования заезда """


def photo_record(camera_operator, record_id, photo_flag):
    """ Сделать фотографию заезда """
    pic_name = get_pic_name(record_id, photo_flag)
    camera_operator_response = make_pic(camera_operator, pic_name)
    return camera_operator_response


def make_pic(camera_operator, pic_name):
    """ Делает фотографию через сторонний модуль camera_operator, у которого
    должен быть метод make_pic, принимающий название фото в кач-ве аргумента"""
    return camera_operator.make_pic(pic_name)


def get_pic_name(record_id, flag):
    """ Формирует и возвращает название фото """
    record_id_str = str(record_id)
    flag_str = str(flag)
    full_pic_name = '_'.join((record_id_str, flag_str))
    return full_pic_name
