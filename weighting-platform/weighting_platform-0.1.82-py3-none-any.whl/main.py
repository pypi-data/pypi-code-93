""" Модуль содержит основной класс, исполняющий все работу """
from weighting_platform import settings
from weighting_platform import cfg
from weighting_platform.functions import barrier_functions
from weighting_platform.functions import photocell_functions
from weighting_platform.functions import weigthing_functions
from weighting_platform.functions import mechanisms
from weighting_platform.functions import general_functions
from weighting_platform.functions import pic_make_functions
from weighting_platform.functions import logging_functions
from weighting_platform.tools import round_decorator
import logging
import threading
from qpi.main import QPI


class WeightingPlatform:
    """ Класс - модель реальной весовой площадки, производит взвешивания.
     Принимает параметры:
     qodex_skud_bus - шина для работы с контроллером СКУД,
     qodex_camera_operator - фреймворк для работы с камера (фотографирование весовой площадки),
     qodex_db_worker - фреймворк для проведения работ с базой данных,
     weight_splitter - модуль отправки данных с весового терминала. """
    def __init__(self, qodex_skud_bus, qodex_camera_operator, gravity_db_worker,
                 weight_splitter, qpi_port=4455, *args, **kwargs):
        self.qsb = qodex_skud_bus
        self.qco = qodex_camera_operator
        self.gdw = gravity_db_worker
        cfg.qodex_pi = QPI('0.0.0.0', qpi_port, mark_disconnect=False,
                       without_auth=True, name='WeightingPlatform QPI')
        self.weight_splitter = weight_splitter
        threading.Thread(target=self.weight_splitter.start, args=()).start()
        self.status_ready = True
        logging_functions.software_start_logging(self.gdw)

    @round_decorator
    def init_round(self, car_number, course: str, car_choose_mode,
                   spec_protocol_dlinnomer_bool=False,
                   spec_protocol_polomka_bool=False,
                   carrier=None, trash_cat=None, trash_type=None, notes=None,
                   operator=None, duo_polygon=None):
        """
        :param car_number: Гос. номер авто
        :param course: Направление, с какой стороны подъехало авто, дается
        в виде external, internal
        :param car_choose_mode: Способ выбора авто (manual|auto)
        :param spec_protocol_polomka_bool:  Вспомогательный протокол "Поломка" (True|False)
        :param spec_protocol_dlinnomer_bool: Вспомогательный протокол "Длинномер" (True|False)
        :param carrier: Идентификатор перевозчика из таблицы clients
        :param trash_cat: Идентификатор категории груза из trash_cats
        :param trash_type: Идентификатор вида груза из trash_types
        :param notes: Комментарий, отсавленный весовщиком
        :param operator: Идентификатор весовщика
        :param duo_polygon: Идентификатор полигона - приемщика груза (DUO)
        :return:
        """
        self.status_ready = False
        # Зарегистрировать авто
        auto_id = self.gdw.register_car(car_number)
        # Узнать, какой ID будет у записи
        record_id = self.gdw.get_record_id(auto_id)
        has_gross = self.gdw.check_car_has_gross(auto_id)
        if not has_gross:
            self.gdw.create_empty_record(auto_id)
        # Сохранить данные о заезде в общедоступный модуль
        general_functions.save_current_round_info(record_id=record_id,
                                                  auto_id=auto_id,
                                                  has_gross=has_gross)
        # Закрыть оба шлагбаума
        mechanisms.close_both_gates(self.qsb)
        log_id = mechanisms.start_log(self.gdw)
        # Извлечь порядок заезда для этого авто (протокол)
        auto_protocol_dict = self.gdw.get_auto_protocol_info(auto_id)
        first_gate = auto_protocol_dict['first_open_gate']        # (near|far)
        second_gate = auto_protocol_dict['second_open_gate']      # (near|far)
        second_gate_course = settings.protocol_gate_description_dict[course][second_gate]
        if spec_protocol_polomka_bool:
            mechanisms.open_both_gates(self.qsb)
        else:
            mechanisms.open_first_barrier(self.qsb, first_gate, course)
        # Извлечь нужное направление весовой, согласно протколу
        first_gate_course = settings.protocol_gate_description_dict[course][first_gate]
        # Засечь, что машина проехала
        photocell_functions.start_course_trace(self.qsb, first_gate_course)
        # Закрыть шлагбаум, если не длинномер
        if not spec_protocol_dlinnomer_bool:
            barrier_functions.close_barrier(self.qsb, course=first_gate_course)
        # Снять вес
        weight = weigthing_functions.get_stable_data(self.weight_splitter)
        print('Получен вес:', weight)
        if weight < 50:
            # Машина не проехала
            self.status_ready = True
            return {'status': False, 'info': 'Машина не проехала'}
        # Внести данные в БД
        if spec_protocol_dlinnomer_bool:
            barrier_functions.open_barrier(self.qsb, course=second_gate_course)
            weight = mechanisms.dlinnomer_scaling_mechanism(self.weight_splitter,
                                                            weight)
            barrier_functions.close_barrier(self.qsb, course=first_gate_course)
        response = self.gdw.init_round(record_id, weight, car_number, carrier,
                                       operator, trash_cat,
                                       trash_type, notes)
        # Фотка
        pic_make_functions.photo_record(self.qco,
                                        response['record_id'],
                                        response['weight_stage'])
        # Открыть шлагбаум
        barrier_functions.open_barrier(self.qsb, course=second_gate_course)
        # Закрыть шлагбаум (по выполнении условий)
        mechanisms.close_barrier_after_round(self.qsb, self.weight_splitter,
                                             second_gate_course)
        if spec_protocol_polomka_bool:
            mechanisms.close_both_gates(self.qsb)
        #logging_functions.fix_record_id(self.gdw, log_id)
        general_functions.clear_current_round()
        self.status_ready = True
        return {'status': True, 'auto_id': auto_id,
                'record_id': response['record_id']}


    def get_round_status(self):
        """ Возвращает статус заезда"""
        return cfg.current_round
