# Описания алертов
alerts_description = {'fast_car': {'code': 'A7|',
                                   'description': 'Машина слишком быстро вернулась ({})|',
                                   'time': 900},
                      'cargo_null': {'code': 'W3|',
                                     'description': 'Нетто около нуля|',
                                     'null': 10},
                      'no_exit': {'code': 'A9|',
                                  'description': 'Для данного авто не была взвешена тара|'},
                      'manual_pass': {'code': 'A0|',
                                      'description': 'Ручной пропуск. Направление {}|'},
                      'no_rfid': {'code': 'A1|', ''
                                                 'description': 'Машина без метки|'},
                      'ph_el_locked': {'code': 'A1|',
                                       'description': 'Фотоэлемент заблокирован|'},
                      'manual_close': {'code': 'A2|',
                                       'description': 'Запись была закрыта вручную|'}
                      }

skud_courses_description = {"IN": {'description': 'Въезд', 'position': 'internal'},
                            "OUT": {'description': 'Выезд', 'position': 'external'}}


def get_alert_description(alert_name):
    """
    Вернуть описание алерта по его названию
    :param alert_name: название алерта
    :return:
    """
    return alerts_description[alert_name]['description']
