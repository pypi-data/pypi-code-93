""" Модуль содержит функции, фиксирующие актвиность пользователя (вход в программу, авторизация, выход и другие) """
import datetime


def capture_user_activity(sqlshell: object, user: int, event: str, events_table: str, events_log_table: str,
                          timenow=datetime.datetime.now()):
    """ Фиксирует событие event в таблицу events_log_table за юзером user, время timenow"""
    event_id = get_event_id(sqlshell, events_table, event)                      # Получить ID события по его описанию
    if type(event_id) == dict:
        # Если появилась ошибка - вернуть ее
        return event_id
    response = insert_data_db(sqlshell, events_log_table, event_id, timenow, user) # Зафиксировать событие в базе
    return response


def get_event_id(sqlshell, events_table, event_description):
    """ Вернуть ID события по его description из таблицы events_table """
    command = "SELECT id FROM {} WHERE description='{}' LIMIT 1".format(events_table, event_description)
    try:
        response = sqlshell.try_execute_get(command)[0][0]
    except IndexError:
        return {'status': 'failed', 'info': 'Не найдено событие с именем: {}'.format(event_description)}
    return response


def insert_data_db(sqlshell, events_log_table, event_id, timenow, user=None):
    """ Зафиксировать произошедшее событие в WDB"""
    if not user:
        command = """ INSERT INTO cm_events_log (event, datetime, operator) 
                    values (%s, %s, %s) RETURNING id"""
        cursor, conn = sqlshell.get_cursor_conn()
        values = (event_id, timenow, user)
        cursor.execute(command, values)
        response = cursor.fetchall()
        conn.commit()
    else:
        command = "INSERT INTO {} (event, datetime, operator) VALUES ({},'{}', {})".format(events_log_table, event_id,
                                                                                           timenow, user)
        response = sqlshell.try_execute(command)
    return response


def get_all_events(sqlshell, events_table):
    """ Вернуть все данные о всех событиях в таблице events_table """
    command = "SELECT * FROM {}".format(events_table)
    response = sqlshell.get_table_dict(command)
    if response['status'] == 'success':
        return response['info']
    else:
        return {}


def is_event_valid(all_events, event_name):
    """ Проверить название события, переданног юзером на валидность """
    for event in all_events:
        if event['description'] == event_name:
            return True
    return False