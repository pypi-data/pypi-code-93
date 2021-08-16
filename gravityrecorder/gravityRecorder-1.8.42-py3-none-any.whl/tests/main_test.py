import unittest
from gravityRecorder.main import Recorder
from gravityRecorder.alerts import settings as alert_settings
import datetime
import uuid


class MainTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recorder = Recorder('wdb', 'watchman', 'hect0r1337',
                                 '192.168.100.118')

    def test_fix_weight_general(self):
        carrier = 1
        weight = 10000
        auto_id = 1022
        operator = 5
        trash_cat = 1
        trash_type = 1
        notes = "SOME NOTES"
        timenow = datetime.datetime.now()
        record_id = self.recorder.create_empty_record(auto_id)
        if self.recorder.check_car_has_gross(auto_id):
            # Если авто взвешивала брутто, функция должна взвесить тару, и check_car_has_gross после этого вернет False
            response = self.recorder.fix_weight_general(record_id, weight, trash_cat, trash_type, notes, operator, auto_id, carrier,
                                                        timenow)
            self.assertTrue(response['weight_stage'] == 'tare')
            self.assertTrue(self.recorder.check_car_has_gross(auto_id) is not True)
            # Проверить на правильность заполнения полей
            command = "SELECT * FROM records WHERE id={}".format(response['info'][0][0])
            response = self.recorder.get_table_dict(command)
            result = response['info'][0]
            self.assertTrue(result['brutto'] == weight)
            self.assertTrue(result['tara'] == weight)
            self.assertTrue(result['cargo'] == 0)
            self.assertTrue(result['carrier'] == carrier)
            self.assertTrue(result['trash_type'] == trash_type)
            self.assertTrue(result['trash_cat'] == trash_cat)
            self.assertTrue(result['operator'] == operator)
            self.assertTrue(result['auto'] == auto_id)
        else:
            # Если же брутто нет, то функция должна всесить брутто, и check_car_has_gross после этого вернет True
            response = self.recorder.fix_weight_general(record_id, weight, trash_cat, trash_type, notes, operator, auto_id, carrier,
                                                        timenow)
            self.assertTrue(response['weight_stage'] == 'gross')
            self.assertTrue(self.recorder.check_car_has_gross(auto_id))
            # Проверить на правильность заполнения полей
            command = "SELECT * FROM records WHERE auto={} and time_out is null".format(auto_id)
            response = self.recorder.get_table_dict(command)
            result = response['info'][0]
            self.assertTrue(result['brutto'] == weight)
            self.assertTrue(result['tara'] == None)
            self.assertTrue(result['cargo'] == None)
            self.assertTrue(result['time_out'] == None)
            self.assertTrue(result['carrier'] == carrier)
            self.assertTrue(result['trash_type'] == trash_type)
            self.assertTrue(result['trash_cat'] == trash_cat)
            self.assertTrue(result['operator'] == operator)
            self.assertTrue(result['auto'] == auto_id)
        self.recorder.delete_record(result['id'])

    def test_get_protocol_settings(self):
        auto_id = 1022
        response = self.recorder.get_auto_protocol_info(auto_id)
        response_must = {'name': 'rfid', 'first_open_gate': 'near',
                         'second_open_gate': 'far', 'weighting': True,
                         'auto_id': auto_id}
        self.assertTrue(response == response_must)

    def test_register_car(self):
        car_number_uuid = uuid.uuid1()
        car_number_str = str(car_number_uuid)[0:10]
        auto_id_after_register = self.recorder.register_car(car_number_str)
        auto_id_without_register = self.recorder.register_car(car_number_str)
        self.assertTrue(auto_id_without_register == auto_id_after_register)
        self.recorder.delete_record(record_id=auto_id_without_register, table_name='auto')

    def test_init_round(self):
        """ Тестирование записи о раунде """
        auto_id = self.recorder.register_car('А845АТ702')
        record_id = self.recorder.create_empty_record(auto_id=auto_id)
        response = self.recorder.init_round(record_id, 25000, 'В060ХА702',trash_cat=1, trash_type=1,
                                            carrier=1, operator=5)
        self.recorder.delete_record(record_id=response['record_id'],
                                    table_name='records')

    def test_reg_act_to_pol(self):
        """ Тестирование регистрации акта за полигоном """
        random_act_id = self.recorder.try_execute_get('SELECT id FROM records LIMIT 1')[0][0]
        response = self.recorder.reg_act_to_polygon(1, random_act_id)
        if response['info']:
            self.recorder.delete_record(record_id=response['info'][0][0],
                                       table_name='duo_records_owning')
        self.assertTrue(response['status'] == 'success')

    def test_add_comment(self):
        """ Добавить комментарий к завершенной записи """
        record_id = self.recorder.try_execute_get('SELECT max(id) FROM records')
        record_id = record_id[0][0]
        self.recorder.add_comment(record_id, 'TEST_COMMENT')
        comment = self.recorder.try_execute_get('SELECT additional_notes FROM '
                                                'operator_notes '
                                                'WHERE record={}'.format(record_id))[0][0]
        self.assertTrue('TEST_COMMENT' in comment)

    def test_upd_last_event(self):
        """ Тестирование обновления записи о последнем заезде этого авто """
        auto_id = 886
        trash_cat = 1
        trash_type = 3
        carrier = 1
        self.recorder.update_last_events(auto_id, trash_cat, trash_type,
                                         carrier)
        change_result = self.recorder.get_last_event(auto_id)
        self.assertEqual(change_result['trash_cat'], trash_cat)
        self.assertEqual(change_result['trash_type'], trash_type)
        self.assertEqual(change_result['carrier'], carrier)

    def test_close_opened_record(self):
        """ Тестирование закрытия открытой записи """
        response = self.recorder.close_opened_record(record_id=2)
        self.assertTrue(response)
        response = self.recorder.close_opened_record(record_id=0)
        print(response)
        self.assertTrue(not response)

    def test_get_unfinished_cycles(self):
        response = self.recorder.get_unfinished_cycles()
        self.assertTrue(not response or type(response) is list)

    def test_update_opened_record(self):
        """ Тестирование механизма обновления открытой записи """
        auto_id = 895
        has_gross = self.recorder.check_car_has_gross(auto_id)
        record_id = self.recorder.create_empty_record(auto_id=auto_id)
        if has_gross:
            self.recorder.update_opened_record(has_gross,
                                               'А845АТ702', 1,
                                               1, 1, 'Изменили запись')
            response = self.recorder.init_round(record_id, 5000, 'А845АТ702')
        else:
            response = self.recorder.init_round(record_id, 1385, 'А845АТ702',trash_cat=1,
                                                trash_type=6, carrier=1,
                                                operator=5)
            self.recorder.update_opened_record(response['record_id'],
                                               'А845АТ702', carrier=1,
                                               trash_cat_id=4, trash_type_id=1,
                                               comment='Изменили запись')
        self.recorder.delete_record(response['record_id'], 'records')

    def test_get_history(self):
        response = self.recorder.get_history('22.07.2021', '22.07.2021')
        self.assertTrue(response['status'] == 'success')

    def test_get_table(self):
        response = self.recorder.get_table_info('auto')
        self.assertTrue(response['status'] == 'success' and
                        len(response['info']) > 0)
        response_unsuccess = self.recorder.get_table_info('core_settings')
        self.assertTrue(response_unsuccess['status'] == 'failed')

    def test_get_record_info(self):
        response = self.recorder.get_record_info(371)

    def test_get_further_record_id(self):
        response = self.recorder.get_record_id(1274)
        #self.assertEqual(response, 482)
        response = self.recorder.get_record_id(1344)
        print("NEXT RECORD ID", response)

    def test_add_trash_cat(self):
        response = self.recorder.add_trash_cat('test_trash_cat_1337', 17)
        self.assertTrue(response['status'] == 'success')
        self.recorder.delete_record(response['info'][0][0], 'trash_cats')

    def test_add_trash_type(self):
        response = self.recorder.add_trash_type('test_type_6', 1, 56)
        self.assertTrue(response['status'] == 'success')
        self.recorder.delete_record(response['info'][0][0], 'trash_types')

    def test_add_trash_type_unreal_cat(self):
        response = self.recorder.add_trash_type('test_type_6', 0, 56)
        print(response)
        self.assertTrue(response['status'] == 'success')
        self.recorder.delete_record(response['info'][0][0], 'trash_types')

    def test_add_new_auto(self):
        response = self.recorder.add_new_auto('В999ВВ999', 1488, 35, 'SOMERFID',
                                              'tails', 1337)
        self.assertTrue(response['status'] == 'success')
        self.recorder.delete_record(response['info'][0][0], 'auto')

    def test_add_new_user(self):
        response = self.recorder.add_new_user('test_user_1337', "AMA TEST USER",
                                              'TEST PASSWORD', '1337')
        self.assertTrue(response['status'] == 'success')
        self.recorder.delete_record(response['info'][0][0], 'users')

    def test_disable_record(self):
        response = self.recorder.add_new_user('test_user_1337', "AMA TEST USER",
                                              'TEST PASSWORD', '1337')
        response = self.recorder.change_record_activity('users', 1337, False)
        response = self.recorder.change_record_activity('users', 1337, True)
        self.recorder.delete_record(response['info'][0][0], 'users')

    def test_get_auto_info(self):
        response_car_num = self.recorder.get_auto_info(car_number='В060ХА702')
        self.assertTrue(type(response_car_num) == dict)
        response_car_id = self.recorder.get_auto_info(auto_id=response_car_num['id'])
        self.assertEqual(response_car_id, response_car_num)
        response_no_car_num = self.recorder.get_auto_info(car_number='AJLFSKFJ')
        self.assertTrue(not response_no_car_num)

    def test_get_records(self):
        self.recorder.close_opened_record(588)
        response = self.recorder.get_alerts(588)
        self.assertTrue(len(response) > 0)

    def test_if_alert_mentioned(self):
        """ Создаем заезд, правоцируем алерт, проверяем ее наличие,
         удаляем заезд"""
        auto_id = self.recorder.register_car('А845АТ702')
        record_id = self.recorder.create_empty_record(auto_id=auto_id)
        response = self.recorder.init_round(record_id, 1385, 'А845АТ702', trash_cat=1,
                                            trash_type=6, carrier=1,
                                            operator=5)
        self.recorder.close_opened_record(response['record_id'])
        alerts = self.recorder.get_alerts(record_id=response['record_id'])
        alert_description = alert_settings.get_alert_description('manual_close')
        self.assertTrue(alert_description in alerts)
        self.recorder.delete_record(response['record_id'], 'records')

    def test_add_carrier(self):
        response_only_name = self.recorder.add_carrier('ТИПА ФИЗИК')
        print(response_only_name)
        response_inn_add = self.recorder.add_carrier('ТИПА ФИЗИК', inn=123)
        print(response_inn_add)
        response_kpp_add = self.recorder.add_carrier('ТИПА ФИЗИК', inn=123, kpp=321)
        print(response_kpp_add)
        response_ex_id_add = self.recorder.add_carrier('ТИПА ФИЗИК', inn=123,
                                                       kpp=321, ex_id='034')
        print(response_ex_id_add)
        response_status_add = self.recorder.add_carrier('ТИПА ФИЗИК', inn=123,
                                                        kpp=321, ex_id='034',
                                                        status='Действующий')
        print(response_status_add)
        response_wserver_id_add = self.recorder.add_carrier('ТИПА ФИЗИК', inn=123,
                                                            kpp=321,
                                                            ex_id='034',
                                                            status='Действующий',
                                                            wserver_id=345)
        print(response_wserver_id_add)

    def test_insert_empty_record_and_fill(self):
        record_id = self.recorder.create_empty_record(886)
        self.assertTrue(type(record_id) == int)
        gross_response = self.recorder.fix_weight_gross(record_id, 1500, None,
                                                        None, None, None)
        self.assertTrue(gross_response['status'] == 'success' and
                        gross_response['record_id'] == record_id)
        tare_responce = self.recorder.fix_weight_tare(record_id, 886, 500)
        self.assertTrue(tare_responce['status'] == 'success' and
                        tare_responce['record_id'] == record_id)
        self.recorder.delete_record(record_id, 'records')

    def test_get_record_comments(self):
        test_com = 'TEST_COMM_GET_RECORD_COMM'
        record_id = self.recorder.create_empty_record(886)
        self.recorder.add_comment(record_id, test_com)
        response = self.recorder.get_operator_comments(record_id)
        self.assertTrue(not response['gross_notes']
                        and not response['tare_notes']
                        and not response['change_notes']
                        and not response['close_notes']
                        and test_com in response['additional_notes'])

    def test_check_car_registered(self):
        carnum = '2478af8a-5'
        resp1 = self.recorder.register_car(carnum)
        resp2 = self.recorder.register_car(carnum)
        self.assertEqual(resp1, resp2)

if __name__ == '__main__':
    unittest.main()
