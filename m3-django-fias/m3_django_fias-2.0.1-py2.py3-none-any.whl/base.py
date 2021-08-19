# coding: utf-8
import re
from importlib import import_module
from os import listdir
from os.path import isfile, join, dirname, abspath

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from lxml import etree

from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.base.introspection import BaseDatabaseIntrospection


def get_by_xpath(element, xpath):
    """
    Возвращает все объекты по xpath
    """
    return element.xpath(
        xpath,
        namespaces={'xs': "http://www.w3.org/2001/XMLSchema"}
    )


def get_first_by_xpath(element, xpath):
    """
    Возвращает первый объект по xpath
    """
    return get_by_xpath(element, xpath)[0]


class XSDField(object):
    u"""
    Поле в стуктуре XSD
    """
    # соотвествие атрибутов XSD и атрибутов объекта с конверторами
    attr_map = {
        u'totalDigits': ('max_length', int),
        u'maxLength': ('max_length', int),
        u'length': ('max_length', int),
    }

    # индексы полей при обращении через порядковый номер
    indexes = {
        0: 'name',
        1: 'type_',
        3: 'max_length',
        6: 'null_ok',
    }

    def __init__(self, element):
        super(XSDField, self).__init__()
        self.name = element.get('name', '').lower()
        self.null_ok = element.get('use') != 'required'
        self.description = element[0][0].text.replace('\n', ' ')
        self.max_length = 1000

        try:
            attrs = get_first_by_xpath(
                element,
                'xs:simpleType/xs:restriction[1]'
            )
        except IndexError:
            self.type_ = element.get('type')
        else:
            self.type_ = attrs.get('base')
            for attr_element in attrs:
                local_name = etree.QName(attr_element).localname
                if local_name in self.attr_map:
                    attr_name, convertor = self.attr_map[local_name]
                    setattr(
                        self,
                        attr_name,
                        convertor(
                            attr_element.get('value')
                        ),
                    )
        finally:
            self.type_ = self.type_.replace(element.prefix + ':', '')

    def __getitem__(self, i):
        return getattr(self, self.indexes[i])


class XSDObject(object):
    """
    XSD объект
    """
    def __init__(self, folder_path, file_name):
        super(XSDObject, self).__init__()
        self.name = self.get_name(file_name)
        self.file_name = file_name
        # для совместимости с типом "Таблица" с точки зрения DataBaseEngine
        self.type = 't'

        root = etree.parse(join(folder_path, file_name)).getroot()

        element = get_first_by_xpath(
            root,
            'xs:element/xs:complexType/xs:sequence/xs:element[1]',
        )

        self.description = get_first_by_xpath(
            element,
            'xs:annotation/xs:documentation[1]/text()',
        )
        self.fields = [
            XSDField(el) for el in get_first_by_xpath(element, 'xs:complexType')
        ]

    def get_name(self, file_name):
        """
        Возвращает имя по имени файла
        """
        p = re.compile("_[a-zA-Z_]+")
        name = p.search(file_name).group(0)[1:-1]

        return name


class XSDFolder(object):
    """
    Директория с XSD
    """
    def __init__(self, folder_path):
        super(XSDFolder, self).__init__()
        self.files = {}

        files = [
            f for f in listdir(folder_path) if isfile(join(folder_path, f))
        ]

        for file_ in files:
            xsd_obj = XSDObject(folder_path, file_)
            self.files[xsd_obj.name] = xsd_obj

    def get_files_list(self):
        return self.files.values()

    def get_file(self, name):
        return self.files[name]


class XSDFolderCursor(object):
    """
    "Указатель" для взаимодействия 
    """
    def __init__(self, xsd_path):
        super(XSDFolderCursor, self).__init__()
        self.xsd_path = xsd_path
        self.folder = None

    def __enter__(self):
        self.folder = XSDFolder(self.xsd_path)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def get_files_list(self):
        """
        Возвращает перечень файлов
        """
        return self.folder.get_files_list()

    def get_file(self, name):
        """
        Возвращает файл по имени
        """
        return self.folder.get_file(name)


class XSDFolderIntrospection(BaseDatabaseIntrospection):
    """
    Анализатор директории с xsd
    """
    data_types_reverse = {
        # немного странное описание булевых значений в схемах как тип byte, но используется именно так
        'byte': 'BooleanField',
        'int': 'PositiveSmallIntegerField',
        'integer': 'IntegerField',
        'string': 'CharField',
        'date': 'DateField',
    }

    def get_table_list(self, cursor):
        """
        Возвращает перечень файлов
        """
        return cursor.get_files_list()

    def get_relations(self, cursor, table_name):
        """
        Возвращает перечнь связей между файлами (пока считаем, что их нет)
        """
        return {}

    def get_table_description(self, cursor, table_name):
        """
        Возвращает перечень полей определенного файла
        """
        return cursor.get_file(table_name).fields


class DatabaseWrapper(BaseDatabaseWrapper):
    """
    Обертка на "базой данных", которая представляет из себя директорию с XSD
    """
    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.introspection = XSDFolderIntrospection(self)

    def cursor(self):
        return XSDFolderCursor(join(dirname(abspath(__file__)), 'schemas'))


def get_table_names_from_db():
    """
    Возвращает названия таблиц
    """
    table_names = []

    for model in apps.get_models():
        if model._meta.db_table.startswith('fias_'):
            table_names.append(model._meta.db_table[5:])

    return tuple(table_names)


def get_table_row_filters():
    """
    Перенос функционала из config в функцию
    Достает фильтры для таблиц

    Оригинальное описание:
    см. fias.importer.filters
    указывается список путей к функциям-фильтрам
    фильтры применяются к *каждому* объекту
    один за другим, пока не закончатся,
    либо пока какой-нибудь из них не вернёт None
    если фильтр вернул None, объект не импортируется в БД

    пример:

    FIAS_TABLE_ROW_FILTERS = {
        'addrobj': (
            'fias.importer.filters.example_filter_yaroslavl_region',
        ),
        'house': (
            'fias.importer.filters.example_filter_yaroslavl_region',
        ),
    }
    """
    row_filters = getattr(settings, 'FIAS_TABLE_ROW_FILTERS', {})
    table_row_filters = {}

    for flt_table, flt_list in row_filters.items():
        if flt_table in get_table_names_from_db():
            for flt_path in flt_list:
                try:
                    module_name, _, func_name = flt_path.rpartition('.')
                    flt_module = import_module(module_name)
                    flt_func = getattr(flt_module, func_name)
                except (ImportError, AttributeError):
                    raise ImproperlyConfigured(
                        'Table row filter module `{0}` does not exists'.format(
                            flt_path))
                else:
                    table_row_filters.setdefault(flt_table, []).append(flt_func)

    return table_row_filters
