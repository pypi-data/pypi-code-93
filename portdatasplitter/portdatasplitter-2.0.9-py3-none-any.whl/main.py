import socket
import threading
from serial import Serial
import serial.tools.list_ports
from time import sleep
from portdatasplitter import settings as s
from traceback import format_exc
from portdatasplitter import functions
from qpi.main import QPI
import datetime


class PortDataSplitter:
    """ Сервер для прослушивания порта port_name (USB, COM),
     и переотправки данных подключенным к нему клиентам (Clients)."""
    def __init__(self, ip: str, port: int, port_names_list=['/dev/ttyUSB0',],
                 debug=False, device_name='unknown',
                 test_mode=False, api_debug=False, handicap_time=5,
                 *args, **kwargs):
        """ Принимает:
        IP :str - IP адрес, на котором будет размещаться сервер рассылки
            входных данных,
        port :int - порт данного сервера,
        port_name :str - имя порта, откуда будут приходить входные данные
        debug :bool - режим дебага, выводит в поток вывода дополнительную
            информацию
        device_name :str - имя устройства, с которого приходят данные
            (это имя можно использовать для парсинга данных,
            характерных именно для этого устройства)
        test_mode :bool - Тестовый режим, PDS не подключается к port_name,
            а отправляет через сервер рассылки данные,
            из атрибута manual_value
        manual_value :str - данные, которые рассылает сервер рассылки.
        handicap_time: время перед запуском основного модуля
            Его можно установить через метод set_test_value
        """
        self.start_api(ip, port, api_debug)
        self.device_name = device_name
        self.debug = debug
        self.port_names_list = port_names_list
        self.test_mode = test_mode
        self.data_list = [functions.get_format_send_message(
            weight_data=s.no_data_code,
            test_mode=self.test_mode,
            creation_date=datetime.datetime.now())]
        self.ports_dict = {}
        self.server_ip = ip
        self.server_port = port
        self.handicap_time = handicap_time

    def start_api(self, ip, port, api_debug):
        """ Запустить API PDS"""
        self.api_server = QPI(ip, port, self, debug=api_debug,
                              without_auth=True, auto_start=False,
                              name='PortDataSplitter QPI')
        thr = threading.Thread(target=self.api_server.launch_mainloop, args=())
        thr.start()

    def get_api_support_methods(self, *args, **kwargs):
        """ Открыть метод для API """
        api_methods = {'set_manual_value': {'method': self.set_manual_value},
                       'get_value': {'method': self.get_value},
                       }
        return api_methods

    def set_manual_value(self, manual_value, port_name=None, *args, **kwargs):
        """ Вручную установить значение manual_value, которое будет отправляться
        подписчикам от якобы port_name, если port_name не указан,
        то это значение будет отправляться от всех портов из словаря
        self.ports_dict.
        """
        return functions.set_manual_value(self.ports_dict, manual_value,
                                          port_name)

    def get_value(self, port_name=None, *args, **kwargs):
        """ Возвращает последний массив данных, у которого port_name=port_name,
        если же port_name=None, этот фильтр
        игнорируется и возвращается любой массив."""
        return functions.get_last_data_dict(self.data_list, port_name, *args,
                                            **kwargs)

    def unset_manual_value(self):
        """ Убрать отправку данных, заданных вручную операцией set_manual_value.
        Отныне данные будут отправлять из object_port, если PDS не запущен в
        режиме тестов. Если же он запущен в режиме тестов, он попытается
        отправить manual_set=None, но после форматирования функцией
        get_manual_set_value отправит 101010 (потому что None не отправляется
        """
        self.manual_value = None

    def get_all_connected_devices(self):
        # Показать все подключенные к этому компьютеру устройства
        ports = serial.tools.list_ports.comports()
        self.show_print('\nAll connected devices:')
        for port in ports:
            self.show_print('\t', port)
        return ports

    def get_device_name(self):
        # Вернуть заданный этому устройству имя
        return self.device_name

    def start(self):
        """ Запустить работу PortDataSplitter"""
        # Запустить параллельный поток, который отправляет данные из
        # self.data_list
        threading.Thread(target=self.sending_thread, args=(1,)).start()
        # Запустить основной поток, слушаюший заданный порт и
        # отправляющий эти данные клиентам
        try:
            self._mainloop()
        except:
            print(format_exc())

    def sending_thread(self, timing=1):
        # Поток отправки показаний весов
        while True:
            sleep(timing)
            self.send_data(self.data_list[-1])

    def send_data(self, data, *args, **kwargs):
        # Отправить данные по клиентам
        try:
            self.show_print('sending:', data, debug=True)
            self.api_server.broadcast_sending(data)
        except:
            # Если данные отправить клиенту не удалось,
            # удалить клиента из списка подписчиков
            self.show_print('\tFailed to send data to client')
            self.show_print(format_exc())

    def make_str_tuple(self, msg):
        # Перед отправкой данных в стандартный поток вывывода форматировать
        return ' '.join(map(str, msg))

    def show_print(self, *msg, debug=False):
        # Отправка данных в стандартный поток выводы
        msg = self.make_str_tuple(msg)
        if debug and self.debug:
            print(msg)
        elif not debug:
            print(msg)

    def _mainloop(self):
        # Основной цикл работы, слушает порт и передает данные клиентам
        self.show_print('\nЗапущен основной цикл отправки весов')
        # Нужно подождать около 5 секунд после запуска всего компа
        sleep(self.handicap_time)
        for port_name in self.port_names_list:
            thr = threading.Thread(target=self.serve_port_name,
                                   args=(port_name,))
            thr.start()

    def serve_port_name(self, port_name):
        """ Обслуживать порт port_name"""
        self.show_print('\nStart serving thread for port: {}'.format(
            port_name))
        port = self.create_port(port_name)
        while True:
            if not self.test_mode:
                data = functions.get_data_from_port(port)
            elif self.test_mode or self.ports_dict[port_name]['manual_value_set']:
                data = functions.get_manual_set_value(
                    self.ports_dict[port_name]['manual_value'])
                sleep(1)
            self.show_print('Data from port:', data, debug=True)
            if data:
                # Если есть данные проверить их и добавить в список отправки data_list
                data = self.check_data(data)
                self.prepare_data_to_send(port_name, data)
            else:
                pass

    def create_port(self, port_name):
        self.ports_dict[port_name] = {'manual_value': None,
                                      'manual_value_set': False,
                                      'test_mode': self.test_mode}
        if not self.test_mode:
            port = Serial(port_name, bytesize=8, parity='N', stopbits=1,
                          timeout=1, baudrate=9600)
            self.ports_dict[port_name]['port_object'] = port
        return self.ports_dict

    def check_data(self, data):
        self.show_print('Checking data in {}'.format(self.device_name), debug=True)
        return data

    def prepare_data_to_send(self, port_name, data, *args, **kwargs):
        # Подготовить данные перед отправкой
        self.data_list = self.data_list[-15:]
        data_to_send = functions.get_format_send_message(weight_data=data,
                                                         port_name=port_name,
                                                         manual_value_set=self.ports_dict[port_name]['manual_value_set'],
                                                         test_mode=self.test_mode,
                                                         creation_date=datetime.datetime.now())
        self.data_list.append(data_to_send)
        return data_to_send

    def reconnect_logic(self, port=None, *args, **kwargs):
        # Логика, реализуемая при выключении терминала
        self.show_print('Терминал выключен!')
        for port_name in self.ports_dict:
            port_name['port_object'].close()
        self._mainloop()

    def _shutdown(self):
        """ Выключить передачу данных и закрыть порты """
        for port in self.ports_dict:
            self.ports_dict[port]['port_object'].close()
        self.api_server.server.close()

