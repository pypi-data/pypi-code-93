""" Модуль содержит класс WEngine, запсукающий работу программной модели
весовой площадки weighing_platform """
import datetime
import time
from whikoperator.main import Wpicoperator
from qodex_skud_bus.main import QodexSkudBus
from wengine.functions import start_functions
from weightsplitter.main import WeightSplitter
from weighting_platform.main import WeightingPlatform
from gravityRecorder.main import Recorder
from wengine.functions import api_functions
from qpi.main import QPI
from gc_module_cua.main import EventsCatcher


class WEngine:
    def __init__(self, dbname, dbuser, dbpass, dbhost, mode='quadro_typical',
                 test_mode=False):
        self.qdw = Recorder(dbname, dbuser, dbpass, dbhost)
        db_settings = start_functions.import_db_settings(self.qdw)
        if mode == 'quadro_typical':
            points_list = [
                {'point_name': 'EXTERNAL_BARRIER',
                    'point_num': db_settings['barrier_external_num'],
                    'point_type': 'EXTERNAL_GATE'},
                {'point_name': 'INTERNAL_BARRIER',
                    'point_num': db_settings['barrier_internal_num'],
                    'point_type': 'EXTERNAL_GATE'},
                {'point_name': 'INTERNAL_PHOTOCELL',
                    'point_num': db_settings['photocell_internal_num'],
                    'point_type': 'INTERNAL_PHOTOCELL'},
                {'point_name': 'EXTERNAL_PHOTOCELL',
                    'point_num': db_settings['photocell_external_num'],
                    'point_type': 'EXTERNAL_PHOTOCELL'}
                ]
        else:
            points_list = []
        self.qsb = QodexSkudBus(db_settings['skud_ip'],
                                int(db_settings['skud_port']),
                                points_list, test_mode)
        self.qco = Wpicoperator(db_settings['camera_ip'],
                                db_settings['camera_login'],
                                db_settings['camera_pass'])
        self.qws = WeightSplitter('0.0.0.0',
                                  int(db_settings['weighting_splitter_port']),
                                  port_names_list=[db_settings['weighting_terminal_port']],
                                  terminal_name=db_settings['weighting_terminal_name'],
                                  test_mode=test_mode, handicap_time=0)
        self.qwp = WeightingPlatform(self.qsb, self.qco, self.qdw, self.qws)
        self.qpi = QPI('0.0.0.0', int(db_settings['api_port']), self,
                       without_auth=True, auto_start=True,
                       mark_disconnect=False, name='WEngine QPI')
        self.events_catcher = EventsCatcher(self.qdw, 'cm_events_table',
                                            'cm_events_log')
        self.current_user_id = None

    def status_sender(self):
        """ Отправляет статус заезда подписчикам """
        while True:
            data = self.qwp.get_round_status()
            self.qpi.broadcast_sending(data)
            time.sleep(1)

    def get_round_status(self):
        """ Вернуть информацию о текущем заезде"""
        return self.qwp.get_round_status()

    def get_api_support_methods(self):
        """ Все методы класса, доступных для QDK """
        methods = {'get_status': {'method': self.get_status},
                   'start_weight_round': {
                       'method': self.start_round_thread},
                   'add_comment': {'method': self.add_comment},
                   'change_opened_record': {
                       'method': self.update_opened_record},
                   'close_opened_record': {'method': self.close_opened_record},
                   'get_unfinished_records': {
                       'method': self.get_unfinished_records},
                   'get_history': {'method': self.get_history},
                   'get_table_info': {'method': self.get_table_info},
                   'get_last_event': {'method': self.get_last_event},
                   'operate_gate_manual_control':
                       {'method': self.operate_barrier},
                   'try_auth_user': {'method': self.try_auth_user},
                   'capture_cm_launched': {'method': self.capture_cm_launched},
                   'capture_cm_terminated': {
                       'method': self.capture_cm_terminated},
                   'make_record': {'method': self.make_record},
                   'delete_record': {'method': self.delete_record},
                   'get_record_info': {'method': self.get_record_info},
                   'get_auto_info': {'method': self.get_auto_info},
                   'get_point_info': {'method': self.get_point_info},
                   'restart_core': {'method': self.restart_core},
                   'add_new_carrier': {'method': self.add_carrier},
                   'add_trash_cat': {'method': self.add_trash_cat},
                   'add_trash_type': {'method': self.add_trash_type},
                   'add_auto': {'method': self.add_auto},
                   'add_operator': {'method': self.add_operator},
                   'get_record_comments': {'method': self.get_record_notes},

                   'block_external_photocell':
                       {'method': self.block_external_photocell},
                   'unblock_external_photocell':
                       {'method': self.unblock_external_photocell},
                   'block_internal_photocell':
                       {'method': self.block_internal_photocell},
                   'unblock_internal_photocell':
                       {'method': self.unblock_internal_photocell},
                   }
        return methods

    def get_status(self, *args, **kwargs):
        return self.qwp.status_ready

    def start_round_thread(self, *args, **kwargs):
        """ Начать раунд взвешивания в паралелльном потоке """
        auto_id = self.qdw.register_car(kwargs['car_number'])
        record_id = self.qdw.get_record_id(auto_id)
        if self.qwp.status_ready:
            response = api_functions.execute_api_method(self.start_round,
                                                        *args, **kwargs)
        else:
            response = {'status': False,
                        'info': 'GCore занят в данный момент'}
        response['record_id'] = record_id
        return response

    def add_comment(self, record_id, comment, *args, **kwargs):
        """ Добавить комментарий к завершенному заезду командой из СМ """
        return self.qdw.add_comment(record_id, comment)

    def update_opened_record(self, record_id, car_number, carrier,
                             trash_cat_id, trash_type_id, comment, polygon,
                             auto_id=None, *args, **kwargs):
        """ Обновить открытую запись """
        return self.qdw.update_opened_record(record_id,  car_number,
                                             carrier, trash_cat_id, trash_type_id,
                                             comment, polygon, auto_id=None)

    def close_opened_record(self, record_id, *args, **kwargs):
        return self.qdw.close_opened_record(record_id)

    def get_unfinished_records(self, *args, **kwargs):
        return self.qdw.get_unfinished_cycles()

    def get_history(self, time_start=None, time_end=None, trash_cat=None,
                    trash_type=None, carrier=None, auto_id=None, polygon=None,
                    alerts=None, what_time='time_in', *args, **kwargs):
        if not time_start: time_start = datetime.datetime.now()
        if not time_end: time_end = datetime.datetime.now()
        return self.qdw.get_history(time_start, time_end, what_time, trash_cat,
                                    trash_type, carrier, auto_id, polygon,
                                    alerts)

    def get_table_info(self, tablename, only_active=True, *args, **kwargs):
        return self.qdw.get_table_info(tablename, only_active)

    def get_last_event(self, auto_id, *args, **kwargs):
        return self.qdw.get_last_event(auto_id)

    def operate_barrier(self, operation, barrier_name, *args, **kwargs):
        """ Производит открытие/закрытие шлагбаумов"""
        info = {'operation': operation, 'barrier_name': barrier_name}
        if operation == 'close':
            self.qsb.lock_point(barrier_name)
        else:
            self.qsb.unlock_point(barrier_name)
        return info

    def try_auth_user(self, username, password, *args, **kwargs):
        auth_result = api_functions.try_auth_user(self.qdw, username, password)
        if auth_result['status'] == 'success':
            self.current_user_id = auth_result['info'][0]['id']
            self.events_catcher.try_capture_new_event('LOGIN',
                                                      self.current_user_id)
        return auth_result

    def capture_cm_launched(self, *args, **kwarg):
        return self.events_catcher.try_capture_new_event('START',
                                                         self.current_user_id)

    def capture_cm_terminated(self, *args, **kwargs):
        """ Зафиксирововать факт выключения СМ """
        return self.events_catcher.try_capture_new_event('EXIT',
                                                         self.current_user_id)

    def make_record(self, weight, car_number, carrier=None, operator=None,
                    trash_cat=None, trash_type=None, notes=None,
                    polygon_int=None, *args, **kwargs):
        """ Создать запись о заезде без самого заезда (для тестов) """
        auto_id = self.qdw.register_car(car_number)
        record_id = self.qdw.create_empty_record(auto_id=auto_id)
        response = self.qdw.init_round(record_id, weight, car_number, carrier,
                                       operator, trash_cat, trash_type, notes,
                                       polygon_int)
        self.qdw.update_last_events(response['auto_id'], trash_cat, trash_type,
                                    carrier)
        return response

    def delete_record(self, record_id, *args, **kwargs):
        """ Удалить заезд """
        return self.qdw.delete_record(record_id, 'records')

    def get_record_info(self, record_id, *args, **kwargs):
        """ Возвращает данные о заезде"""
        return self.qdw.get_record_info(record_id)

    def get_auto_info(self, car_number=None, auto_id=None, *args, **kwargs):
        """ Возвращает об авто по его гос. номеру"""
        return self.qdw.get_auto_info(car_number=car_number, auto_id=auto_id)

    def get_point_info(self, point_name, *args, **kwargs):
        """ Возвращает данные о точке доступа """
        return self.qsb.get_point_state(point_name_str=point_name)

    def restart_core(self, *args, **kwargs):
        """ Перезапустить systemd unit runcore, обслуживающий gcore"""
        return api_functions.restart_core(self.qdw)

    def add_carrier(self, name, inn=None, kpp=None, ex_id=None, status=None,
                    wserver_id=None, *args, **kwargs):
        """ Добавить нового перевозчика """
        return self.qdw.add_carrier(name, inn, kpp, ex_id, status, wserver_id)

    def add_auto(self, car_number, wserver_id, model, rfid, id_type, rg_weight,
                 *args, **kwargs):
        """ Добавить новое авто """
        return self.qdw.add_new_auto(car_number, wserver_id, model, rfid,
                                     id_type, rg_weight)

    def add_trash_cat(self, cat_name, wserver_id, *args, **kwargs):
        """ Добавить новую категорию груза """
        return self.qdw.add_trash_cat(cat_name, wserver_id)

    def add_trash_type(self, type_name, wserver_id, wserver_cat_id,
                       *args, **kwargs):
        """ Добавить новый вид груза """
        return self.qdw.add_trash_type(type_name, wserver_cat_id, wserver_id)

    def add_operator(self, full_name, username, password, wserver_id,
                     *args, **kwargs):
        """ Добавить нового пользователя (весовщика)  """
        return self.qdw.add_new_user(full_name, username, password, wserver_id)

    def get_record_notes(self, record_id: int, *args, **kwargs):
        """
        Вернуть все комментарии весовщика по записи
        :param record_id: ID записи
        :return: Возвращает словарь
        """
        return self.qdw.get_operator_comments(record_id)

    def block_external_photocell(self, *args, **kwargs):
        return self.qsb.lock_point("EXTERNAL_PHOTOCELL")

    def unblock_external_photocell(self, *args, **kwargs):
        return self.qsb.normal_point("EXTERNAL_PHOTOCELL")

    def block_internal_photocell(self, *args, **kwargs):
        return self.qsb.lock_point("INTERNAL_PHOTOCELL")

    def unblock_internal_photocell(self, *args, **kwargs):
        return self.qsb.normal_point("INTERNAL_PHOTOCELL")

    def start_mainloop(self):
        """ Основной цикл работы"""
        while True:
            time.sleep(1)

    def start_round(self, car_number, course, car_choose_mode,
                   spec_protocol_dlinnomer_bool=False,
                   spec_protocol_polomka_bool=False,
                   carrier=None, trash_cat=None, trash_type=None, notes=None,
                   operator=None, duo_polygon=None, *args, **kwargs):
        """ Начать раунд взвешивания """
        response = self.qwp.init_round(car_number, course, car_choose_mode,
                   spec_protocol_dlinnomer_bool,
                   spec_protocol_polomka_bool,
                   carrier, trash_cat, trash_type, notes, operator, duo_polygon)
        return response
