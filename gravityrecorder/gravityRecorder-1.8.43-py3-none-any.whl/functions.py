def get_weighting_stage(sqlshell, car_number: str):
    sqlshell


def get_cargo(gross, tare):
    """ Получает cargo (cargo), как разницу между gross и tare """
    cargo = int(gross) - int(tare)
    return cargo


def get_auto_protocol_settings(sql_shell, auto_protocol, auto_id,
                               *args, **kwargs):
    command = "SELECT p.name, ps.first_open_gate, ps.second_open_gate, ps.weighting " \
              "FROM round_protocols p INNER JOIN round_protocols_settings ps ON (p.id = ps.protocol) " \
              "WHERE p.name = '{}'".format(auto_protocol)
    response = sql_shell.get_table_dict(command)
    if response['status'] == 'success':
        response['info'][0]['auto_id'] = auto_id
        return response['info'][0]


def get_auto_protocol(sql_shell, auto_id):
    """ Возвращает протокол авто по его ID"""
    command = "SELECT id_type FROM auto WHERE id={}".format(auto_id)
    response = sql_shell.try_execute_get(command)
    return response[0][0]


def check_car_registered(sqlshell, car_number):
    """ Проверить регистрирована ли машина в таблице auto """
    command = "select id from auto where car_number='{}'".format(car_number)
    response = sqlshell.try_execute_get(command)
    response = response
    if response:
        # Если транзакция удалась
        return response[0][0]


def register_new_car(sqlshell, car_number):
    """ Зарегистрировать новую машину"""
    command = "insert into auto (car_number, id_type) values ('{}', 'tails') " \
              "ON CONFLICT (car_number) DO UPDATE SET id_type=EXCLUDED.id_type".format(car_number)
    response = sqlshell.try_execute(command)
    if response['status'] == 'success':
        return response['info'][0][0]


def register_act_to_polygon(sql_shell, polygon_id: int, record_id: int):
    """
    Зафиксировать акт за полигонов в duo_records_owning
    :param sql_shell: фреймворк для выполнения комманд
    :param polygon_id: id полигона
    :param record_id: id записи
    :return:
    """
    command = "INSERT INTO duo_records_owning (record, owner) " \
              "VALUES ({}, {}) ON CONFLICT (record) DO UPDATE SET owner={}"
    command = command.format(record_id, polygon_id, polygon_id)
    return sql_shell.try_execute(command)


def add_gross_notes(sql_shell, record_id: int, notes: str):
    """ Добавить комментарий на взвешивание брутто """
    return add_notes(sql_shell, record_id, notes, notes_type='gross_notes')


def add_additional_notes(sql_shell, record_id: int, notes: str):
    """ Добавить комментарий на взвешивание брутто """
    return add_notes(sql_shell, record_id, notes, notes_type='additional_notes')


def add_tare_notes(sql_shell, record_id: int, notes: str):
    """ Добавить комментарий на взвешивание тары """
    return add_notes(sql_shell, record_id, notes, notes_type='tare_notes')


def add_change_notes(sql_shell, record_id: int, notes: str):
    """ Добавить комментарий на изменение записи """
    return add_notes(sql_shell, record_id, notes, notes_type='change_notes')


def add_close_notes(sql_shell, record_id: int, notes: str):
    """ Добавить комментарий на закрытие записи """
    return add_notes(sql_shell, record_id, notes, notes_type='close_notes')


def add_notes(sql_shell, record_id, notes: str, notes_type: str):
    """ Добавить комментарий вида notes_type в таблицу с комментариями
    весовщиков (operator_notes) """
    command = "INSERT INTO operator_notes (record, {}) " \
              "values ({}, '{}') ON CONFLICT (record) " \
              "DO UPDATE SET {}='{}'"
    command = command.format(notes_type, record_id, notes, notes_type, notes)
    return sql_shell.try_execute(command)


def get_table_info(sqlshell, tablename, only_active=True):
    """ Возвращает данные о содержимом таблицы tablename
    для взаимодействия по API """
    command = "SELECT * FROM {}".format(tablename)
    if only_active:
        command += " WHERE active=True"
    response = sqlshell.get_table_dict(command)
    return response


def get_next_id(sqlshell):
    """ Получить следующий ID за максимальным """
    command = "SELECT last_value FROM records_id_seq;"
    next_val = sqlshell.try_execute_get(command)[0][0]
    next_val += 1
    return next_val


def get_current_id(sqlshell, auto_id):
    command = "SELECT id FROM records where auto={} and time_out is null"
    command = command.format(auto_id)
    response = sqlshell.try_execute_get(command)[0][0]
    return response


def get_local_trash_cat_id(sql_shell, wserver_trash_cat_id):
    """ Излвечь локальный ID категории груза по его wserver_id """
    command = "SELECT id FROM trash_cats where wserver_id={}"
    command = command.format(wserver_trash_cat_id)
    response = sql_shell.try_execute_get(command)
    if response:
        return response[0][0]
