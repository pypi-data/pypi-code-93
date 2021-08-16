from traceback import format_exc
import datetime
from gravityRecorder import functions
from gravityRecorder.alerts import alert_funcs
from wsqluse.wsqluse import Wsqluse
from gravityRecorder import settings


class Recorder(Wsqluse):
    """ Класс, генерирующий факты взвешивания """
    def __init__(self, dbname, user, password, host, debug=False,
                 auto_table_name='auto',
                 records_table_name='records',
                 disputs_table_name='disputs'):
        Wsqluse.__init__(self, dbname, user, password, host, debug=debug)
        self.auto_table_name = auto_table_name
        self.records_table_name = records_table_name
        self.disputs_table_name = disputs_table_name

    def get_auto_protocol_info(self, auto_id):
        """ Вернуть информацию о протоколе авто по его id """
        protocol_name = functions.get_auto_protocol(self, auto_id)
        protocol_settings = functions.get_auto_protocol_settings(self,
                                                                 protocol_name,
                                                                 auto_id)
        return protocol_settings

    def register_car(self, car_number):
        """ Проверить, есть ли в таблице auto машина с таким гос.номером,
        если нет - зарегистрировать """
        auto_id = functions.check_car_registered(self, car_number)
        if not auto_id:
            auto_id = functions.register_new_car(self, car_number)
        return auto_id

    def init_round(self, record_id, weight, car_number, carrier=None,
                   operator=None, trash_cat=None, trash_type=None, notes=None,
                   polygon_int=1, *args, **kwargs):
        """
        Обработать взвешивание
        :param trash_cat:
        :param car_number:
        :param carrier:
        :param operator:
        :param trash_type:
        :param notes:
        :param polygon_int:
        :param record_id:
        :param args:
        :param kwargs:
        :return:
        """
        # Извлечь auto_id (уже зареганного или зарегать, если не зареган)
        auto_id = self.register_car(car_number)
        response = self.fix_weight_general(record_id, weight, trash_cat,
                                           trash_type, notes,
                                           operator, auto_id, carrier,
                                           datetime=datetime.datetime.now())
        self.reg_act_to_polygon(polygon_int, response['record_id'])
        response['auto_id'] = auto_id
        return response

    def get_rfid_by_carnum(self, carnum):
        """ Вернуть RFID-номер машины по его гос.номеру """
        command = "SELECT rfid FROM auto WHERE car_number='{}'".format(carnum)
        response = self.try_execute_get(command)
        return response

    def check_car_choose_mode(self, alerts, choose_mode, car_number, course):
        # Проверить, как была выбрана машина (вручную/автоматоически)
        rfid = self.get_rfid_by_carnum(car_number)[0][0]
        alerts = alert_funcs.check_car_choose_mode(rfid, alerts, choose_mode,
                                                   car_number, course)
        return alerts

    def get_rfid_by_id(self, auto_id):
        """ Вернуть RFID-номер машины по его ID """
        command = "SELECT rfid FROM auto WHERE id={}".format(auto_id)
        response = self.try_execute_get(command)
        return response

    def check_car(self, cargo, alerts):
        alerts = alert_funcs.cargo_null(cargo, alerts)
        return alerts

    def fast_car(self, carnum, alerts):
        # Проверить, не слишком ли быстро вернулась машина,
        # если да - дополнить алерт кодом из wsettings и вернуть
        print('\nИнициирована проверка на FastCar')
        timenow = datetime.datetime.now()
        command = "SELECT le.date from last_events le " \
                  "INNER JOIN auto a ON (le.car_id=a.id) " \
                  "where a.car_number='{}'".format(carnum)
        try:
            last_visit_date = self.try_execute_get(command)[0][0]
            alerts = alert_funcs.check_fast_car(last_visit_date, timenow,
                                                alerts)
        except:
            print('\tОшибка при проверке заезда')
            print(format_exc())
        return alerts

    def check_car_has_gross(self, auto_id):
        """
        :param auto_id:
        :return:
        Проверить взвешивала ли машина брутто
        """
        command = "select id from {} where auto='{}' and time_out is " \
                  "null and not time_in is null".format(self.records_table_name, auto_id)
        response = self.try_execute_get(command)
        if len(response) > 0:
            return response[0][0]

    def update_last_events(self, auto_id, trash_cat, trash_type, carrier,
                           timestamp=None):
        """
        Обновляет запись в таблице last_events, где хранятся данные о последнем
        посещении авто
        :param auto_id: ID авто
        :param carrier: ID перевозчика
        :param trash_type: ID вида груза
        :param trash_cat: ID категории груза
        :param timestamp: Время посещения
        :return:
        """
        if not timestamp:
            timestamp = datetime.datetime.now()
        comm = "INSERT INTO last_events " \
               "(car_id, carrier, trash_type, trash_cat, date) " \
               "values (%s,%s, %s, %s, %s) " \
               "ON CONFLICT (car_id) DO UPDATE " \
               "SET carrier=%s, trash_cat=%s, trash_type=%s, date=%s"
        values = (auto_id, carrier, trash_type, trash_cat, timestamp,
                  carrier, trash_cat, trash_type, timestamp)
        response = self.try_execute_double(comm, values)
        return response

    def get_last_event(self, auto_id: int):
        """ Вернуть запись о последнем посещении авто из last_events """
        command = "SELECT * FROM last_events WHERE car_id={}".format(auto_id)
        response = self.get_table_dict(command)
        if response['status'] == 'success':
            return response['info'][0]

    def upd_old_num(self, old_carnum, new_carnum):
        # Обновляет старый номер на новый
        command = "UPDATE {} SET car_number='{}' WHERE car_number='{}'"
        command = command.format('auto', new_carnum, old_carnum)
        self.try_execute(command)

    def check_access(self, rfid):
        ''' Проверяет, разрешается ли машине въезд '''
        command = "SELECT rfid FROM {} WHERE rfid='{}'".format(s.auto, rfid)
        response = self.try_execute_get(command)
        if len(response) > 0:
            return True

    def create_empty_record(self, auto_id):
        """ Создает пустую запись в records (есть только id авто) """
        command = "INSERT INTO records (auto) VALUES (%s)"
        values = (str(auto_id),)
        response = self.try_execute_double(command, values)
        if response['status'] == 'success':
            return response['info'][0][0]

    def fix_weight_general(self, record_id, weight, trash_cat, trash_type,
                           notes, operator, auto_id, carrier=None,
                           datetime=datetime.datetime.now()):
        have_gross = self.check_car_has_gross(auto_id)
        if have_gross:
            response = self.fix_weight_tare(record_id, auto_id, weight,
                                            datetime)
            functions.add_tare_notes(self, record_id, notes)
            response['weight_stage'] = 'tare'
        else:
            response = self.fix_weight_gross(record_id, weight, carrier,
                                             trash_cat, trash_type,
                                             operator, datetime)
            self.update_last_events(auto_id, trash_cat, trash_type, carrier)
            functions.add_tare_notes(self, record_id, notes)

            response['weight_stage'] = 'gross'
        return response

    def fix_weight_tare(self, record_id, auto_id, weight_tare,
                        datetime=datetime.datetime.now()):
        """ Зафиксировать вес ТАРА """
        gross = self.get_gross(record_id, self.records_table_name)        # Извлечь вес БРУТТО
        cargo = functions.get_cargo(gross, weight_tare)                 # Вычислить вес НЕТТО
        if weight_tare > gross and self.get_auto_protocol_info(auto_id)['name'] != 'rfid':
            old_gross = gross
            gross = weight_tare
            weight_tare = old_gross
        # Сформировать команду на обновление записи по auto_id
        sql_command = "UPDATE {} SET brutto={}, tara={}, cargo={}, time_out='{}' " \
                      "WHERE id = {}"
        sql_command = sql_command.format(self.records_table_name,
                                         gross, weight_tare, abs(cargo),
                                         datetime, record_id)
        response = self.try_execute(sql_command)                        # Выполнить команду
        return {'status': response['status'], 'record_id': record_id}

    def get_gross(self, record_id, records_table_name: str):
        command = "SELECT brutto FROM {} WHERE id={}"
        command = command.format(records_table_name, record_id)
        gross = self.try_execute_get(command)
        return gross[0][0]

    def fix_weight_gross(self, record_id, weight, carrier, trash_cat, trash_type,
                         operator, timenow=datetime.datetime.now()):
        """ Создать новую запись с брутто """
        command = """UPDATE records SET brutto=%s, time_in=%s, carrier=%s, 
                        trash_cat=%s, trash_type=%s, operator=%s 
                        WHERE id=%s"""
        cursor, conn = self.get_cursor_conn()
        values = (weight, timenow, carrier,
                  trash_cat, trash_type, operator,
                  record_id)
        cursor.execute(command, values)
        conn.commit()
        return {'status': 'success', 'record_id': record_id}    # response = [(int)]

    def delete_record(self, record_id, table_name=None):
        """ Удалить запись с id=record_id"""
        if not table_name:
            table_name = self.records_table_name
        command = "DELETE FROM {} WHERE id={}".format(table_name, record_id)
        response = self.try_execute(command)
        return response

    def reg_act_to_polygon(self, polygon_id:int, record_id:int):
        """ Зафиксировать акт за полигоном """
        return functions.register_act_to_polygon(self, polygon_id, record_id)

    def add_comment_old(self, record_id, comment, *args, **kwargs):
        """ ДОбавить комментарий к записи (устаревшее) """
        command = "UPDATE {} set notes = notes || '... Добавочно: {}' where id={}"
        command = command.format(self.records_table_name, comment, record_id)
        self.try_execute(command)

    def add_comment(self, record_id, comment, *args, **kwargs):
        """ Добавить комментарий к записи """
        return functions.add_additional_notes(self, record_id, comment)

    def close_opened_record(self, record_id, close_notes='Без комментария',
                            time_out=None, *args, **kwargs):
        """
        Закрыть запись вручную
        :param record_id: ID записи (заезда)
        :param close_notes: Комментарий юзера, закрывающего запись
        :param time_out: Какое время выезда установить? По умолчанию - текущее
        :param args:
        :param kwargs:
        :return: Возвращает либо None, если нет такого заезда, либо его ID
        """
        if not time_out:
            time_out = datetime.datetime.now()
        command = "UPDATE {} SET time_out='{}', tara=0, cargo=brutto WHERE id={}"
        command = command.format(self.records_table_name, time_out, record_id)
        response = self.try_execute(command)
        if response['info']:
            functions.add_close_notes(self, record_id, close_notes)
            alert_funcs.add_alert_manuall_close(self, record_id)
            return response['info'][0][0]

    def update_opened_record(self, record_id, car_number=None, carrier=None,
                             trash_cat_id=None, trash_type_id=None,
                             comment=None, polygon=None, auto_id=None,
                             *args, **kwargs):
        """ Изменить запись, у которой уже есть брутто
        Можно изменить все основные черты, а можно только некоторые """
        if auto_id is None:                 # Если auto_id = None (гос. номер вбит вручную, такой машины нет в таблице auto)
            auto_id = self.register_car(car_number)    # Зарегистрировать ее (завести запсиь в таблице auto)
        # Собираем все указанные настройки в список
        settings = []
        if auto_id: settings.append("auto={}".format(auto_id))
        if carrier: settings.append("carrier={}".format(carrier))
        if trash_cat_id: settings.append("trash_cat={}".format(trash_cat_id))
        if trash_type_id: settings.append("trash_type={}".format(trash_type_id))
        # Конвертируем элементы списка в строку, которую вставим в SQL запрос
        settings_str = ','.join(settings)
        command = "UPDATE {} SET {} WHERE id={}"
        command = command.format(self.records_table_name, settings_str,
                                 record_id)
        response = self.try_execute(command)
        if response['status'] == 'success':
            functions.add_change_notes(self, response['info'][0][0], comment)
            if polygon:
                # Если поддерживается DUO - изменить присваивание
                self.reg_act_to_polygon(polygon, response['info'][0][0])
            return {'status': 'success', 'info': 'Данные успешно изменены'}
        else:
            return response

    def get_unfinished_cycles(self, *args, **kwargs):
        """ Вернуть все открытые записи (без тары)
        :return: Возвращает либо None, либо список словарей, отображающих
        заезды """
        my_timedelta = datetime.datetime.now() - datetime.timedelta(minutes=5)
        command = "SELECT * FROM records WHERE time_out is null or time_out > '{}'"
        command = command.format(my_timedelta)
        response = self.get_table_dict(command)
        if response['status'] == 'success':
            return response['info']

    def get_history(self, time_start, time_end, what_time='time_in',
                    trash_cat=None, trash_type=None, carrier=None, auto_id=None,
                    polygon_object_id=None, alerts=None, *args, **kwargs):
        """ Вернуть статистику по заданным фильтрам """
        command = "SELECT rt.id as record_id, rt.trash_cat, rt.trash_type, rt.brutto, rt.cargo, rt.tara, rt.time_in, " \
                  "rt.time_out, rt.carrier, rt.operator, rt.wserver_sent, rt.wserver_get, " \
                  "rt.wserver_id, rt.auto, auto_table.rfid, dpo.id, at.alerts FROM {} rt " \
                  "LEFT JOIN {} auto_table ON (rt.auto=auto_table.id) " \
                  "LEFT JOIN {} dro ON (rt.id=dro.record) " \
                  "LEFT JOIN {} dpo ON (dro.owner = dpo.id) " \
                  "LEFT JOIN {} at ON (at.records_id=rt.id) " \
                  "WHERE {}::date>='{}' and {}::date<='{}'"
        command = command.format(self.records_table_name,
                                 self.auto_table_name,
                                 'duo_records_owning',
                                 'duo_pol_owners',
                                 'disputs',
                                 what_time, time_start, what_time, time_end)
        if auto_id:
            command += " and auto_table.id={}".format(auto_id)
        if alerts == 'да':
            command += " and not at.alerts is null"
        if alerts == 'нет':
            command += " and at.alerts is null"
        if trash_cat:
            command += " and trash_cat={}".format(trash_cat)
        if trash_type:
            command += " and trash_type={}".format(trash_type)
        if carrier:
            command += " and carrier={}".format(carrier)
        if polygon_object_id:
            command += " and dpo.id={}".format(polygon_object_id)
        response = self.get_table_dict(command)
        return response

    def get_table_info(self, tablename, only_active=True, *args, **kwargs):
        """ Возвращает все содержимое таблицы tablename для взаимодействия по API """
        # Проверить, разрешается ли отправлять данные об этой табоице
        if tablename in list(settings.send_allowed_table_rules.keys()):
            response = functions.get_table_info(self, tablename, only_active)
            for except_column in settings.send_allowed_table_rules[tablename]['except_columns']:
                # Перебрать все поля таблицы и удалить из отправки запрещенные
                for record_info in response['info']:
                    record_info.pop(except_column)
        else:
            response = {'status': 'failed',
                        'info': 'У вас нет доступа к просмотру информации с данной таблицы!'}
        response['tablename'] = tablename
        return response

    def get_record_info(self, record_id, tablename='records', *args, **kwargs):
        """ Получить всю информацию по записи """
        command = "SELECT * FROM {} WHERE id={}".format(tablename, record_id)
        response = self.get_table_dict(command)
        if response['status'] == 'success':
            return response['info'][0]

    def get_record_id(self, auto_id):
        """ Вернуть будущий ID этого заезда, перед его совершением """
        if self.check_car_has_gross(auto_id):
            response = functions.get_current_id(self, auto_id)
        else:
            response = functions.get_next_id(self)
        return response

    def add_carrier(self, name, inn=None, kpp=None, ex_id=None, status=None,
                    wserver_id=None):
        """ Добавить нового перевозчика """
        command = "INSERT INTO clients (name, inn, kpp, ex_id, status, wserver_id) " \
                  "VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (name, inn, kpp) " \
                  "DO UPDATE SET ex_id=%s, status=%s, wserver_id=%s"
        values = (name, inn, kpp, ex_id, status, wserver_id,
                  ex_id, status, wserver_id)
        response = self.try_execute_double(command, values)
        return response

    def add_trash_cat(self, cat_name, wserver_id=None):
        command = "INSERT INTO trash_cats (cat_name, wserver_id) " \
                  "VALUES (%s, %s) ON CONFLICT (wserver_id) " \
                  "DO UPDATE SET cat_name=%s"
        values = (cat_name, wserver_id, cat_name)
        response = self.try_execute_double(command, values)
        return response

    def add_trash_type(self, trash_type, wserver_trash_cat_id, wserver_id=None):
        """ Добавить вид груза """
        cat_id = functions.get_local_trash_cat_id(self, wserver_trash_cat_id)
        command = "INSERT INTO trash_types (name, category, wserver_id) " \
                  "VALUES (%s, %s, %s) ON CONFLICT (wserver_id) " \
                  "DO UPDATE SET name=%s, category=%s"
        values = (trash_type, cat_id, wserver_id, trash_type, cat_id)
        response = self.try_execute_double(command, values)
        return response

    def add_new_auto(self, car_number, wserver_id,
                     model=0, rfid=None, id_type='tails', rg_weight=0):
        """ Добавить новое авто """
        command = "INSERT INTO auto (car_number, rfid, auto_model, id_type, " \
                  "rg_weight, wserver_id) " \
                  "VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (wserver_id) " \
                  "DO UPDATE SET id_type=%s, rg_weight=%s, rfid=%s"
        values = (car_number, rfid, model, id_type, rg_weight, wserver_id,
                  id_type, rg_weight, rfid)
        return self.try_execute_double(command, values)


    def add_new_user(self, full_name, username, password, wserver_id):
        """ Добавить нового юзера """
        command = "INSERT INTO users (username, full_name, password, wserver_id) " \
                  "VALUES (%s, %s, %s, %s) ON CONFLICT  (wserver_id) DO UPDATE " \
                  "SET username=%s, full_name=%s, password=%s"
        values = (username, full_name, password, wserver_id,
                  username, full_name, password)
        return self.try_execute_double(command, values)

    def change_record_activity(self, table_name, wserver_id, activivty):
        """ Переключить флажок active в table_name на False, где
        wserver_id=wserver_id"""
        command = "UPDATE {} set active={} WHERE wserver_id={}"
        command = command.format(table_name, activivty, wserver_id)
        return self.try_execute(command)

    def get_auto_info(self, car_number=None, auto_id=None):
        """ Вернуть информацию об авто в виде словаря по его гос.номеру либо
        auto_id"""
        command = "SELECT * FROM auto WHERE "
        if auto_id:
            command += "id={}".format(auto_id)
        else:
            command += "car_number='{}'".format(car_number)
        response = self.get_table_dict(command)
        if response['status'] == 'success':
            return response['info'][0]

    def get_alerts(self, record_id):
        """
        Вернуть алерты по заезду
        :param record_id: ID заезда
        :return: Строка
        """
        return alert_funcs.get_alerts(self, record_id)

    def get_operator_comments(self, record_id):
        """
        Вернуть все комментарии весовщиков по заезду, обычно из таблицы
        operator_notes
        :param record_id: id заезда
        :return: словарь
        """
        command = "SELECT * FROM operator_notes WHERE record={}"
        command_frmt = command.format(record_id)
        response = self.get_table_dict(command_frmt)
        if response['status'] == 'success':
            return response['info'][0]
