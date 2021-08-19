# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from abc import ABCMeta
from abc import abstractmethod
from itertools import chain
from itertools import count

from six import iteritems
from six import text_type
from six import with_metaclass
from six.moves import http_client
from six.moves import map
from six.moves import range

from m3_gar_client.constants import GAR_LEVELS_PLACE
from m3_gar_client.constants import GAR_LEVELS_STREET
from m3_gar_client.data import AddressObject
from m3_gar_client.data import House
from m3_gar_client.data import ObjectMapper
from m3_gar_client.utils import cached_property

from .server import server


# -----------------------------------------------------------------------------
# Обёртки над данными, поступающими с сервера m3-rest-gar.

class AddressObjectMapper(ObjectMapper):
    """
    Обертка над данными сервера m3-rest-gar об адресных объектах.

    Предназначена для использования при создании экземпляров
    :class:`m3_gar_client.data.AddressObject`.
    """

    fields_map = {
        'id': 'id',
        'guid': 'objectguid',
        'obj_id': 'objectid',
        'previous_id': 'previd',
        'next_id': 'nextid',
        'ifns_fl_code': 'params__IFNSFL__value',
        'ifns_fl_territorial_district_code': 'params__territorialifnsflcode__value',
        'ifns_ul_code': 'params__IFNSUL__value',
        'ifns_ul_territorial_district_code': 'params__territorialifnsulcode__value',
        'okato': 'params__OKATO__value',
        'oktmo': 'params__OKTMO__value',
        'postal_code': 'params__PostIndex__value',
        'formal_name': 'name',
        'official_name': 'name',
        'short_name': 'typename',
        'level': 'level',
        'kladr_code': 'params__CODE__value',
        'kladr_plain_code': 'params__PLAINCODE__value',
        'date_of_update': 'updatedate',
        'date_of_creation': 'startdate',
        'date_of_expiration': 'enddate',
        'full_name': lambda data: '{} {}'.format(data['name'], data['typename']),
    }

    assert set(fields_map) == set(AddressObject.fields)


class HouseMapper(ObjectMapper):
    """Обертка над данными сервера m3-rest-gar об адресных объектах.

    Предназначена для использования при создании экземпляров
    :class:`m3_gar_client.data.House`.
    """

    fields_map = {
        'id': 'id',
        'guid': 'objectguid',
        'obj_id': 'objectid',
        'ifns_fl_code': 'params__IFNSFL__value',
        'ifns_fl_territorial_district_code': 'params__territorialifnsflcode__value',
        'ifns_ul_code': 'params__IFNSUL__value',
        'ifns_ul_territorial_district_code': 'params__territorialifnsulcode__value',
        'okato': 'params__OKATO__value',
        'oktmo': 'params__OKTMO__value',
        'postal_code': 'params__PostIndex__value',
        'house_number': 'housenum',
        'building_number': 'addnum1',
        'structure_number': 'addnum2',
        'date_of_update': 'updatedate',
        'date_of_creation': 'startdate',
        'date_of_end': 'enddate',
    }

    assert set(fields_map) == set(House.fields)


class UIAddressObjectMapper(ObjectMapper):
    """
    Обертка над данными сервера m3-rest-gar об адресных объектах.
    Предназначена для использования в UI.
    """

    fields_map = {
        # TODO: заменить 'objectid' на 'objectguid'
        'objectId': 'objectid',
        'level': 'level',
        'shortName': 'typename',
        'formalName': 'name',
        'postalCode': 'params__PostIndex__value',
        'fullName': lambda data: '{} {}'.format(data['name'], data['typename']),
    }


class UIHouseMapper(ObjectMapper):
    """
    Обертка над данными сервера m3-rest-gar о зданиях.
    Предназначена для использования в UI.
    """

    fields_map = {
        # TODO: заменить 'objectid' на 'objectguid'
        'objectId': 'objectid',
        'houseNumber': 'housenum',
        'buildingNumber': 'addnum1',
        'structureNumber': 'addnum2',
        'postalCode': 'params__PostIndex__value',
    }

# -----------------------------------------------------------------------------
# Загрузчики данных с сервера m3-rest-gar.


class LoaderBase(with_metaclass(ABCMeta, object)):
    """
    Базовый класс для загрузчиков объектов ГАР.
    """

    def __init__(self, filter_string, **kwargs):
        """Инициализация экземпляра класса.

        :param unicode filter_string: Строка для фильтрации объектов.
        :param float timeout: Timeout запросов к серверу ГАР в секундах.
        """
        self.filter_string = filter_string
        self.timeout = kwargs.get('timeout')

    @property
    @abstractmethod
    def _path(self):
        """Путь к ресурсу API сервера ГАР.

        :rtype: str
        """

    @property
    @abstractmethod
    def _fields(self):
        """Имена полей, подлежащих загрузке.

        :rtype: tuple
        """

    @property
    @abstractmethod
    def _mapper_class(self):
        """Класс, преобразующий имена полей.

        ::rtype: m3_gar_client.data.ObjectMapper
        """

    def _load_page(self, params, page):
        params = params.copy()
        params['page'] = page

        drf_response = server.get(self._path, params, timeout=self.timeout)
        if drf_response.status_code == http_client.OK:
            result = drf_response.json()
        else:
            result = None

        return result

    def _process_object_data(self, drf_object_data):
        """Выполняет дополнительную обработку данных объекта ГАР.

        :param dict drf_object_data: Данные объекта ГАР, полученные с сервера m3-rest-gar.
        """
        return map_object_data(self._mapper_class, drf_object_data)

    def _build_result(self, object_data):
        """Формирует данные результирующего объекта ГАР.

        Полученные данные включаются в результат загрузки.

        :param dict object_data: Данные объекта, полученные с сервера ГАР и
            прошедшие обработку в методе ``_process_object_data``.

        :rtype: dict
        """
        return {
            field: object_data[field]
            for field in self._fields
        }

    @abstractmethod
    def _filter(self, object_data):
        """Возвращает True, если объект ГАР должен попасть в загрузку.

        :rtype: bool
        """

    def _get_params(self):  # pylint: disable=no-self-use
        """Возвращает параметры запроса к серверу ГАР.

        :rtype: dict
        """
        result = {
            'name': ','.join(word.replace('.', '') for word in self.filter_string.split()),
        }

        return result

    def load_raw(self, page=None):
        """Возвращает данные адресных объектов в исходном виде.

        :param int page: Номера страницы для загрузки данных. Значение ``None``
            указывает на необходимость загрузки всех страниц.

        :rtype: generator
        """
        if page is None:
            pages = count(start=1)
        else:
            pages = range(page, page + 1)

        params = self._get_params()

        for page_number in pages:
            drf_data = self._load_page(params, page_number)
            if drf_data:
                for drf_object_data in drf_data['results']:
                    object_data = self._process_object_data(drf_object_data)
                    if self._filter(object_data):
                        yield object_data

                if not drf_data['next']:
                    break
            else:
                break

    def load_results(self, page=None):
        """Возвращает данные в соответствии с параметрами загрузчика.

        :param int page: Номера страницы для загрузки данных. Значение ``None``
            указывает на необходимость загрузки всех страниц.

        :rtype: itertools.imap
        """
        return map(self._build_result, self.load_raw(page))

    @abstractmethod
    def _sort_key(self, object_data):
        """Возвращает значение ключа для сортировки результатов загрузки.

        :param dict object_data: Данные загруженного объекта ГАР.
        """

    def _process_result(self, data):
        """Обработка полученных после загрузки данных.

        :param tuple data: Кортеж словарей с данными загруженных объектов ГАР.
        """
        return sorted(data, key=self._sort_key)

    def load(self, page=None):
        """Загружает данные с сервера ГАР.

        :param int page: Номера страницы для загрузки данных. Значение ``None``
            указывает на необходимость загрузки всех страниц.

        :rtype: collections.Iterable
        """
        data = tuple(self.load_results(page))
        result = self._process_result(data)

        return result


class ParentFilterMixin(object):
    """
    Миксин для загрузчиков, которые используют id родительского объекта в запросах к серверу ГАР
    """

    @property
    @abstractmethod
    def _default_hierarchy(self):
        """Вид иерархии, используемый по умолчанию"""

    def __init__(self, *args, **kwargs):
        super(ParentFilterMixin, self).__init__(*args, **kwargs)

        self._hierarchy = kwargs.get('hierarchy') or self._default_hierarchy
        self._parent_id = kwargs.get('parent_id')

    def _get_params(self):
        result = super(ParentFilterMixin, self)._get_params()

        if self._parent_id:
            result['parent'] = text_type('{}:{}'.format(self._hierarchy, self._parent_id))

        return result


class AddressObjectLoaderBase(ParentFilterMixin, LoaderBase):
    """Базовый класс для загрузчиков адресных объектов ГАР.

    В терминологии ГАР адресными объектами называются:

        * субъекты РФ;
        * административные и муниципальные районы субъектов РФ;
        * города;
        * сельские/городские поселения;
        * населенные пункты;
        * элементы планировочной структуры;
        * улицы.
    """

    _default_hierarchy = 'mun'

    @property
    def _path(self):
        return '/addrobj/'

    @cached_property
    def _fields(self):
        return list(self._mapper_class.fields_map.keys())

    @property
    @abstractmethod
    def _levels(self):
        """Уровни адресных объектов, для которых нужно искать данные в ГАР.

        :rtype: tuple
        """

    def _get_params(self):
        """Возвращает параметры запроса к серверу ГАР.

        :rtype: dict
        """
        result = super(AddressObjectLoaderBase, self)._get_params()

        if self._levels:
            result['level'] = ','.join(map(str, self._levels))

        return result

    def _filter(self, object_data):
        return True

    def _sort_key(self, object_data):
        return object_data['fullName'] or ''


class AddressObjectLoader(AddressObjectLoaderBase):
    """Загрузчик адресных объектов ГАР.

    Загружает информацию об адресных объектах, соответствующих строке
    фильтрации и находящихся на одном из указанных в параметрах экземпляра
    уровней иерархии адресных объектов.
    """

    _levels = None

    _mapper_class = AddressObjectMapper

    def __init__(self, filter_string, levels=None, **kwargs):
        """Инициализация экземпляра класса.

        :param unicode filter_string: Строка для фильтрации объектов.
        :param levels: Уровни адресных объектов.
        """
        super(AddressObjectLoader, self).__init__(filter_string, **kwargs)

        self._levels = levels


class PlaceLoader(AddressObjectLoaderBase):
    """
    Загрузчик сведений о населенных пунктах
    """

    _levels = GAR_LEVELS_PLACE

    _mapper_class = UIAddressObjectMapper


class StreetLoader(AddressObjectLoaderBase):
    """
    Загрузчик сведений об улицах.
    """

    _levels = GAR_LEVELS_STREET

    _mapper_class = UIAddressObjectMapper


class HouseLoader(ParentFilterMixin, LoaderBase):
    """
    Загрузчик сведений о зданиях.
    """

    _default_hierarchy = 'mun'

    _mapper_class = UIHouseMapper

    _fields = (
        'objectId',
        'houseNumber',
        'buildingNumber',
        'structureNumber',
        'postalCode',
    )

    @property
    def _path(self):
        return '/houses/'

    @staticmethod
    def _split_number(number):
        """Разделяет номер на целочисленную и буквенную части.

        :param unicode number: Номер дома/корпуса/строения.

        :rtype: tuple
        """
        int_part = ''.join(ch for ch in number if ch.isdigit())
        str_part = number[len(int_part):]

        return int(int_part) if int_part else -1, str_part

    def _sort_key(self, object_data):
        return tuple(chain(*(
            self._split_number(object_data[number_type + 'Number'])
            for number_type in ('house', 'building', 'structure')
        )))

    def _filter(self, object_data):
        """Возвращает True для записей, соответствующих параметрам поиска.

        Запись считается соответствующей указанным при инициализации загрузчика
        параметрам поиска, если:

            * номер дома (если есть) в записи **начинается со строки**,
              указанной в аргументе ``filter_string``;
            * номер корпуса или строения (если номер дома отсутствует) в записи
              **начинается со строки**, указанной в аргументе
              ``filter_string``;
            * в аргументе ``filter_string`` конструктора класса было передано
              значение ``None``.

        :rtype: bool
        """
        if self.filter_string is None:
            result = True
        else:
            house = (object_data.get('houseNumber') or '').lower()

            if house:
                result = house.startswith(self.filter_string)
            else:
                building = (object_data.get('buildingNumber') or '').lower()
                structure = (object_data.get('structureNumber') or '').lower()
                result = (
                    building and building.startswith(self.filter_string) or
                    structure and structure.startswith(self.filter_string)
                )
        return result

    def _process_object_data(self, drf_object_data):
        house_data = super(HouseLoader, self)._process_object_data(drf_object_data)

        house_data['houseNumber'] = house_data['houseNumber'] or ''
        house_data['buildingNumber'] = house_data['buildingNumber'] or ''
        house_data['structureNumber'] = house_data['structureNumber'] or ''

        return house_data


# -----------------------------------------------------------------------------
# Функции для создания объектов m3-gar-client на основе данных m3-rest-gar.

def get_address_object(obj_id, timeout=None):
    """Возвращает адресный объект, загруженный с сервера ГАР.

    Если адресный объект не найден, возвращает ``None``.

    :param obj_id: ID адресного объекта ГАР.
    :param float timeout: timeout запроса к серверу ГАР в секундах.

    :rtype: m3_gar_client.data.AddressObject or NoneType

    :raises requests.ConnectionError: если не удалось соединиться с сервером ГАР
    """
    assert obj_id is not None

    # TODO: Сервер ГАР пока не поддерживает поиск адресного объекта по objectguid.
    # В идеале нужно смотреть на вид obj_id и вызывать разные методы поиска в зависимости от него
    # Пока предполагаем, что obj_id - число (int).

    response = server.get('/addrobj/{}/'.format(obj_id), timeout=timeout)

    if response.status_code == http_client.OK:
        response_data = response.json()
        mapped_data = map_object_data(AddressObjectMapper, response_data)
        result = AddressObject(**mapped_data)
    else:
        result = None

    return result


def find_address_objects(filter_string, levels=None, parent_id=None, timeout=None):
    """Возвращает адресные объекты, соответствующие параметрам поиска.

    :param unicode filter_string: Строка поиска.
    :param levels: Уровни адресных объектов, среди которых нужно осуществлять поиск.
    :param parent_id: ID родительского объекта.
    :param float timeout: Timeout запросов к серверу ГАР в секундах.

    :rtype: generator
    """
    return AddressObjectLoader(filter_string, levels=levels, parent_id=parent_id, timeout=timeout).load_results()


def get_house(house_id, timeout=None):
    """Возвращает информацию о здании по его ID в ГАР.

    :param house_id: ID здания.
    :param float timeout: Timeout запросов к серверу ГАР в секундах.

    :rtype: m3_gar_client.data.House
    """
    assert house_id is not None

    response = server.get('/houses/{}/'.format(house_id), timeout=timeout)

    if response.status_code == http_client.OK:
        response_data = response.json()
        mapped_data = map_object_data(HouseMapper, response_data)
        result = House(**mapped_data)
    else:
        result = None

    return result


def find_house(obj_id, house_number='', building_number='', structure_number='', timeout=None):
    """Возвращает информацию о здании по его номеру.

    :param obj_id: ID адресного объекта.
    :param unicode house_number: Номер дома.
    :param unicode building_number: Номер корпуса.
    :param unicode structure_number: Номер строения.
    :param float timeout: Timeout запросов к серверу ГАР в секундах.

    :rtype: m3_gar_client.data.House or NoneType
    """
    assert house_number or building_number or structure_number, (
        house_number, building_number, structure_number
    )

    houses = tuple(
        house_info['objectId']
        for house_info in HouseLoader(
            obj_id,
            house_number or building_number or structure_number,
            timeout=timeout,
        ).load()
        if (
            house_info['objectId'] and
            house_info['houseNumber'] == (house_number or '') and
            house_info['buildingNumber'] == (building_number or '') and
            house_info['structureNumber'] == (structure_number or '')
        )
    )

    if len(houses) == 1:
        result = get_house(houses[0], timeout)
    else:
        result = None

    return result


def flatten_object_data(raw_object_data):
    """Преобразует данные объекта ГАР к "плоскому" виду

    :param dict raw_object_data: Необработанные данные объекта ГАР, полученные с сервера m3-rest-gar.
    """
    flat_data = {}

    for key, value in iteritems(raw_object_data):
        if type(value) is dict:
            for inner_key, inner_value in iteritems(flatten_object_data(value)):
                flat_data['{}__{}'.format(key, inner_key)] = inner_value

        elif type(value) is list and key == 'params':
            for param_dict in value:
                if type(param_dict) is not dict:
                    continue

                code = param_dict.get('typeid', {}).get('code')
                if code is None:
                    continue

                for inner_key, inner_value in iteritems(flatten_object_data(param_dict)):
                    flat_data['params__{}__{}'.format(code, inner_key)] = inner_value

        else:
            flat_data[key] = value

    return flat_data


def map_object_data(mapper_class, raw_object_data):
    """Выполняет маппинг сырых данных, полученных с сервера m3-rest-gar

    :param dict raw_object_data: Необработанные данные объекта ГАР, полученные с сервера m3-rest-gar.
    :param class ObjectMapper mapper_class: класс-маппер.
    """
    flat_data = flatten_object_data(raw_object_data)
    mapped_data = mapper_class(flat_data)

    return mapped_data
