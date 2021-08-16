""" Модуль, хранящий все функции, производящие проверку раунда взвшеивания
на алерты """
from gravityRecorder.alerts import settings as s
import datetime


def check_car_choose_mode(rfid, alerts, choose_mode, course, *args, **kwargs):
    # Проверить, как была выбрана машина (вручную/автоматоически)
    if choose_mode.lower() == 'manual' and not s.alerts_description['manual_pass']['description'] in alerts:
        # Если выбрали вручную и алерта еще нет
        try:
            if not rfid and not s.alerts_description['no_rfid']['description'] in alerts:
                # Если нет RFID, возбудить алерт, что машина привезла ТКО, но без метки
                alerts += s.alerts_description['no_rfid']['description']
            else:
                # Если же метка есть, возбудить алерт, что выбрали вручную машину с меткой
                full_alert = s.alerts_description['manual_pass']['description'].format(
                    s.skud_courses_description[course]['description'])
                alerts += full_alert
        except:
            pass
    return alerts


def cargo_null(cargo, alerts):
    # Проверить, не околонулевое ли нетто, если да - дополнить алерт кодом из wsettings и вернуть
    check = s.alerts_description['cargo_null']
    if int(cargo) < check['null']:
        alerts += check['description']
    return alerts


def check_fast_car(last_visit_date, timenow,  alerts):
    # Проверить, не слишком ли быстро вернулась машина, если да - дополнить алерт кодом из wsettings и вернуть
    print('\nИнициирована проверка на FastCar')
    check = s.alerts_description['fast_car']
    return_time = timenow - last_visit_date
    return_time = return_time.seconds
    print('\tВремя возвращения:', return_time)
    print('\tНеобходимо для возбуждения алерта:', check['time'])
    if return_time < check['time'] and not check['description'] in alerts:
        notes = str(int(return_time / 60)) + ' минут после прошлого заезда'
        alerts += check['description'].format(notes)
        print('\t\tАлерт возбужден')
        return alerts
    else:
        print('\t\tАлерт не возбужден')
        return alerts


def add_alert_manuall_close(sql_shell, record_id: int):
    """
    Выставить алерт о ручном закрытии заезда
    :param sql_shell: Объект взимодействия с базой данных
    :param record_id: ID заезда
    :return: Результат выполнения SQL функции
    """
    alert_description = s.get_alert_description('manual_close')
    resp = add_alerts(sql_shell, alerts=alert_description, rec_id=record_id)
    return resp


def add_alerts(sql_shell, alerts, rec_id):
    """
    Добавляет строку в таблицу disputs, где указываются данные об инциденте
    :param alerts: алерт
    :param rec_id: идентификатор записи
    :return:
    """
    timenow = datetime.datetime.now()
    if if_alert_mentioned(sql_shell=sql_shell, record_id=rec_id, alert=alerts):
        return
    command = "INSERT INTO disputs " \
              "(date, records_id, alerts) " \
              "VALUES ('{}', {}, '{}') " \
              "ON CONFLICT (records_id) DO UPDATE SET " \
              "alerts = disputs.alerts || '{}'"
    command = command.format(timenow, rec_id, alerts, alerts)
    return sql_shell.try_execute(command)


def if_alert_mentioned(sql_shell, record_id: int, alert: str):
    """
    Проверяет, указан ли этот алерт уже для этой записи.
    :param record_id: ID заезда
    :param alert: Сам алерт
    :return: Если алерт уже указан, возвращает True
    """
    alerts = get_alerts(sql_shell, record_id)
    if alerts and alert in alerts:
        return True


def get_alerts(sql_shell, record_id: int):
    """
    Возвращает все алерты по заезду.
    :param record_id: ID заезда
    :return: В строковом представлении алерты по заезду, ну или None
    """
    command = "SELECT alerts FROM disputs WHERE records_id={}"
    command = command.format(record_id)
    response = sql_shell.try_execute_get(command)
    if response:
        return response[0][0]
