import unittest
import uuid

from qdk.main import QDK
from wengine.main import WEngine


class MainTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(MainTest, self).__init__(*args, **kwargs)
        self.wengine_test = WEngine('wdb', 'watchman', 'hect0r1337',
                                    '192.168.100.118', test_mode=True)
        self.qdk = QDK('localhost', 15500)
        self.status_qdk = QDK('localhost', 4455)
        self.status_qdk.make_connection()
        #self.status_qdk.subscribe()
        self.qdk.make_connection()

    def test_connections(self):
        """ Тест подключения + получения статуса """
        response = self.qdk.execute_method('get_status', get_response=True)
        self.assertEqual(True, response['info'])

    def create_delete_record(test_function):
        """ Декоратор, который создает запись о заезде, с которым будет работать
        тестовая функция, а затем удаляет ее, после отработки функции"""
        def wrapper(self, *args, **kwargs):
            car_number = str(uuid.uuid4())[:10]
            record = self.make_record(car_number=car_number)
            record_id = record['record_id']
            test_function(self, record_id)
            self.qdk.execute_method('delete_record', record_id=record_id,
                                    get_response=True)
        return wrapper

    def make_record(self, car_number='В060ХА702', weight=1337):
        """ Тесты на создание записи о заезде без самого заезда """
        response = self.qdk.execute_method('make_record', weight=weight,
                                           car_number=car_number,
                                           get_response=True)
        print("MAKE RECORD RESPONSE", response)
        self.assertTrue(response['status'])
        return response['info']

    @create_delete_record
    def test_add_comment(self, record_id):
        add_comm = 'Добавочный коммент через API'
        self.qdk.execute_method('add_comment', record_id=record_id,
                                           comment=add_comm,
                                           get_response=True)
        record_info = self.qdk.execute_method('get_record_info',
                                              record_id=record_id,
                                              get_response=True)

    def test_start_weight_round(self):
        response = self.qdk.execute_method('start_weight_round', car_number='alflsfa',
                                course='external', car_choose_mode='auto',
                                get_response=True)

        print('RESPONSE', response)

    @create_delete_record
    def test_get_record(self, record_id):
        record_info = self.qdk.execute_method('get_record_info',
                                              record_id=record_id,
                                              get_response=True)
        self.assertTrue(record_info['info']['id'] == record_id)

    @create_delete_record
    def test_upd_opened_record(self, record_id):
        record_info = self.qdk.execute_method('get_record_info',
                                              record_id=record_id,
                                              get_response=True)
        print("BEFORE_UPD_INFO", record_info)
        comm = 'Запись была изменена вручную'
        response = self.qdk.execute_method('change_opened_record', record_id=record_id,
                                car_number='О000О000', carrier=1,
                                trash_cat_id=1, trash_type_id=1, comment=comm,
                                polygon=1, get_response=True)
        new_record_info = self.qdk.execute_method('get_record_info',
                                              record_id=record_id,
                                              get_response=True)
        print("AFTER_UPD_INFO", new_record_info)
        self.assertTrue(record_info['info']['auto'] != new_record_info['info']['auto'])

    def test_barrier(self):
        """ Тестирование работы с точками доступа """
        response_unlock = self.qdk.execute_method('unlock_point',
                                           point_name_str='INTERNAL_GATE',
                                           get_response=True)
        response_state = self.qdk.execute_method('get_point_state',
                                                 point_name_str='INTERNAL_GATE',
                                                 get_response=True)
        self.assertEqual(response_state['info'], 'ONLINE_UNLOCKED')

    def test_barriers_manual_control(self):
        """ Тестирование ручного управления шлагбаумами """
        self.qdk.execute_method('operate_gate_manual_control',
                                operation='open', barrier_name='EXTERNAL_BARRIER',
                                get_response=True)
        response_open = self.qdk.execute_method('get_point_info',
                                                point_name='EXTERNAL_BARRIER',
                                                get_response=True)
        self.assertTrue(response_open['info'], 'ONLINE_UNLOCKED')
        self.qdk.execute_method('operate_gate_manual_control',
                                operation='close', barrier_name='EXTERNAL_BARRIER',
                                get_response=True)
        response_close = self.qdk.execute_method('get_point_info',
                                                point_name='EXTERNAL_BARRIER',
                                                get_response=True)
        print("RESPONSE_LOCK", response_close)
        self.assertTrue(response_close['info'], 'ONLINE_LOCKED')

    @create_delete_record
    def test_close_record(self, record_id):
        record_info = self.qdk.execute_method('get_record_info',
                                                  record_id=record_id,
                                                  get_response=True)
        self.assertTrue(not record_info['info']['tara'] and
                        not record_info['info']['time_out'])
        res = self.qdk.execute_method('close_opened_record', record_id=record_id,
                                get_response=True)
        print("RES", res)
        upd_info = self.qdk.execute_method('get_record_info',
                                                  record_id=record_id,
                                                  get_response=True)
        self.assertTrue(upd_info['info']['tara'] == 0 and
                        upd_info['info']['time_out'])

    @create_delete_record
    def test_get_unfinished_records(self, record_id):
        response = self.qdk.execute_method('get_unfinished_records', get_response=True)
        self.assertTrue(response['info']['status'] == 'success')

    @create_delete_record
    def test_get_history(self, record_id):
        response_history = self.qdk.execute_method('get_history', get_response=True)
        self.assertTrue(response_history['status'])
        response_history = self.qdk.execute_method('get_history',
                                                   time_start='2021.05.26',
                                                   time_end='2021.06.26',
                                                   get_response=True)
        self.assertTrue(response_history['status'])

    def test_auth_user(self):
        response_auth_success = self.qdk.execute_method('try_auth_user',
                                                        username='test_user_1',
                                                        password='123',
                                                        get_response=True)
        print("AUTH_SUCCESS", response_auth_success)
        self.assertTrue(response_auth_success['info']['status'] == 'success')
        response_auth_failed = self.qdk.execute_method('try_auth_user',
                                                       username='test_user_3',
                                                       password='123456',
                                                       get_response=True)
        print("AUTH_FAIL", response_auth_failed)
        self.assertTrue(response_auth_failed['info']['status'] == 'failed')


    def test_cm_start_catch(self):
        """ Тест функции фиксации запуска CM """
        response_cm_start = self.qdk.execute_method('capture_cm_launched',
                                                    get_response=True)
        self.assertTrue(response_cm_start['status'])

    def test_cm_stop_catch(self):
        """ Тест функции фиксации запуска CM """
        response_cm_start = self.qdk.execute_method('capture_cm_terminated',
                                                    get_response=True)
        self.assertTrue(response_cm_start['status'])

    def test_get_table_info(self):
        """ Тест функции фиксации запуска CM """
        table_info = self.qdk.execute_method('get_table_info',
                                             tablename='auto',
                                             get_response=True)
        self.assertTrue(table_info['status'])

    @create_delete_record
    def test_get_last_event(self, record_id):
        record_info = self.qdk.execute_method('get_record_info',
                                              record_id=record_id,
                                              get_response=True)
        print("RESPONSE_GET_RECORD_INFO", record_info)
        last_event_info = self.qdk.execute_method('get_last_event',
                                                  auto_id=record_info['info']['auto'],
                                                  get_response=True)
        print("RESPONSE_LAST_EVENT_INFO", last_event_info)

    def test_photocell_work(self):
        command = 'block_external_photocell'
        self.qdk.execute_method(command)
        response = self.qdk.get_data()
        self.assertTrue(response['status'] and
                        response['core_method'] == command)

        command = 'unblock_external_photocell'
        self.qdk.execute_method(command)
        response = self.qdk.get_data()
        self.assertTrue(response['status'] and
                        response['core_method'] == command)

        command = 'unblock_internal_photocell'
        self.qdk.execute_method(command)
        print("WAITING")
        response = self.qdk.get_data()
        self.assertTrue(response['status'] and
                        response['core_method'] == command)

        command = 'block_internal_photocell'
        self.qdk.execute_method(command)
        response = self.qdk.get_data()
        self.assertTrue(response['status'] and
                        response['core_method'] == command)

if __name__ == '__main__':
    unittest.main()
