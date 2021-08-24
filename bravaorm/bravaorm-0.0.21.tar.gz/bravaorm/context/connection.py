
from bravaorm.utils.inflector import Inflector
from bravaorm.context.database import DataBase
import bravaorm.entity.datatype as datatype
from bravaorm.utils.log import *

import re

class Connection():

    def __init__(self, db_user=None, db_password=None, db_host=None, db_port=None, db_database=None, db_ssl=False, db_ssl_ca=None, db_ssl_cert=None, db_ssl_key=None, db_charset='utf8', log_level='error'):
        try:

            Logging(log_level=log_level)

            self._inflector = Inflector()
            self._conn = DataBase(db_user, db_password, db_host, db_port,db_database, db_ssl, db_ssl_ca, db_ssl_cert, db_ssl_key, db_charset)

            self.__queue__ = {
                'add':[],
                'delete':[]
            }
        except Exception as e:
            raise e

    def __reset__(self):
        self._distinct = None
        self._select = None
        self._alias = None
        self._where = None
        self._orwhere = {}
        self._having = None
        self._orhaving = {}
        self._orderby = None
        self._groupby = None
        self._limit = None
        self._join = None
        self._inner = None
        self._include = None

    def __getattr__(self, name):
        try:
            if not name in self.__dir__():
                self._table = name
                self._class_name = self._inflector.classify(name)
                self._class = getattr(__import__(f'model.{self._class_name.lower()}', fromlist=[self._class_name]), self._class_name)
                self._klass = self._class()
                self.__reset__()
        except Exception as e:
            raise e
        return self

    def __format_clause__(self, *clause):
        arr = []

        def FormatCondition(_field_condition):
            if not "(" in _field_condition and ")" in _field_condition:
                _field_condition = f'{self._table}.{_field_condition.strip()}'
            return  _field_condition

        def FormatField(_condition):
            return _condition.strip() if '.' in _condition else FormatCondition(_condition)

        for c in clause:
            if not ',' in c:
                arr.append(FormatField(c))
            else:
                arr = arr + [FormatField(s) for s in c.split(',')]

        return arr

    def __format_fields__(self, *fields):
        arr = []
        for f in fields:
            if not ',' in f:
                arr.append(f.strip())
            else:
                arr = arr + [s.strip() for s in f.split(',')]
        return arr

    def __valid_relationship__(self, table):
        if table in self._klass.__dict__ and self._klass[table].__class__.__name__.startswith("Obj"):
            return True
        else:
            raise Exception(f"{table} does not exist in relational list of {self._class_name}")

    def __format_relationship__(self, *tables):
        list_tables = []
        for table in tables:
            if len(re.findall(r"(([a-z]|[A-Z]|[0-9]|\'|\*){1},{1}\ )", table)) > 0:
                for table_name in table.split(","):
                    if self.__valid_relationship__(table_name.strip()):
                        list_tables.append(table_name.strip())
            elif self.__valid_relationship__(table.strip()):
                list_tables.append(table.strip())
        return list_tables


    def __format_join_query__(self, joined, type):
        if self._select:
            _selects_stetaments = ', '.join([f"{c} AS '{c}'" for c in self._select if self.__is__join_select__(c)])
        else:
            _selects_stetaments = ''

        _joins_stetaments = []

        if joined:
            count = 0
            for join in joined:
                count += 1
                join_class = self._klass[join]()
                join_key = self._klass[join]

                if self._select:
                    if not all([f'{join}.{pk}' in _selects_stetaments for pk in join_class.__metadata__['pk']]):
                        _select_join_pks = ", ".join([f"{join}.{pk} AS '{join}.{pk}'" for pk in join_class.__metadata__['pk']])
                        _selects_stetaments = f"{_selects_stetaments}, {_select_join_pks}"
                else:
                    _select_join = ", ".join([f"{join}.{field} AS '{join}.{field}'" for field in join_class.__dict__ if not field.startswith("_") and not join_class[field].__class__.__name__.startswith("Obj")])
                    _selects_stetaments = f"{_selects_stetaments}, {_select_join}" if _selects_stetaments != '' else _select_join


                # CODITIONS OF JOIN
                _coditions = []

                __conditions_join = [w for w in self._where if self.__is__join_or_include_codition__(join, w)] if self._where else []


                if self._klass[join].__class__.__name__ != "ObjListOfMany":
                    _base_join = f"({join}.{join_key.key} = {self._table}.{join_key.reference})"

                    if len(__conditions_join)>0:

                        # WHERE
                        _coditions.append(f"{_base_join.replace('()','').replace(')','')} AND {' AND '.join(__conditions_join)})")

                        # ORWHERE
                        _coditions.extend([c for c in [f" OR ( {_base_join.replace('(','').replace(')','')} AND {' AND '.join([w for w in conditions if self.__is__join_or_include_codition__(join, w)])})" for block, conditions in self._orwhere.items()] if c.strip() != 'OR ()'] if self._orwhere else [])

                    else:
                        _coditions.append(_base_join)


                    _joins_stetaments.append(f"{type} JOIN {join_key.table} AS {join} ON ({' '.join(_coditions)})")

                else:
                    # N TO N
                    _base_join = f"{join_key.keyname}.{join_key.key} = inter_{count}_{join_key.intermediate}.{join_key.rel_key}"

                    if len(__conditions_join)>0:
                        # WHERE
                        _coditions.append(f"{_base_join} AND {' AND '.join(__conditions_join)}")

                        # ORWHERE
                        _coditions.extend([c for c in [f" OR {_base_join} AND {' AND '.join([w for w in conditions if self.__is__join_or_include_codition__(join, w)])}" for block, conditions in self._orwhere.items()] if c.strip() != 'OR'] if self._orwhere else [])

                    else:

                        _coditions.append(_base_join)


                    _joins_stetaments.append(f"{type} JOIN {join_key.intermediate} AS inter_{count}_{join_key.intermediate} ON  inter_{count}_{join_key.intermediate}.{join_key.ref_key} = {self._table}.{join_key.reference} {type} JOIN {join_key.table} AS {join_key.keyname} ON {' '.join(_coditions)}")


        return _selects_stetaments, " ".join(_joins_stetaments)

    def __format_include_query__(self, obj, include):
        _include_key = self._klass[include]
        _include_class = self._klass[include]()
        if obj[_include_key.reference].value:
            if self._select:
                _include_select = ", ".join([f"{c.replace(f'{include}.', '')} AS '{c.replace(f'{include}.', '')}'" for c in self._select if self.__is__include_select__(include, c)])
                if not all([f"'{pk}'" in _include_select for pk in _include_class.__metadata__['pk']]):
                    _pk_select = ", ".join([f"{pk} AS '{pk}'" for pk in _include_class.__metadata__['pk']])
                    _include_select = f"{_include_select}, {_pk_select}"
            else:
                _include_select = ", ".join([f"{field} AS '{field}'" for field in _include_class.__dict__ if not field.startswith("_") and not _include_class[field].__class__.__name__.startswith("Obj")])

            if isinstance(obj[_include_key.reference], datatype.Int):
                _default_condition = f'{include}.{_include_key.key} = {obj[_include_key.reference].value}'
            else:
                _default_condition = f"{include}.{_include_key.key} = '{obj[_include_key.reference].value}'"

            __conditions_include = " AND ".join([w for w in self._where if self.__is__join_or_include_codition__(include, w)]) if self._where else ""

            _where = []
            if len(__conditions_include)>0:
                _where.append(f"( {_default_condition} AND {__conditions_include} )")
                _orwhere = '' if len(self._orwhere) == 0 else ' OR '.join([f"( {_default_condition} AND {' AND '.join([w for w in conditions if self.__is__join_or_include_codition__(include, w)])} )" for block, conditions in self._orwhere.items()])
                if _orwhere != '':
                    _where.append(_orwhere)
            else:
                _where.append(_default_condition)

            def ReplaceData(stetament):
                rule = f"\S[a-zA-Z]+_{self._table}.[a-zA-Z]+_?[a-zA-Z]+ | {self._table}.[a-zA-Z]+_?[a-zA-Z]+"
                match = re.findall(rule, stetament)
                for value in match:
                    if value.strip().startswith(self._table):
                        key = value.strip().split(".")[1]
                        stetament = stetament.replace(value, str(obj[key].value))
                return stetament

            if _include_key.__class__.__name__ != "ObjListOfMany":
                stetament = ReplaceData(f"SELECT {_include_select} FROM {include} WHERE {' OR '.join(_where)}")
            else:
                _where = ""
                __conditions_include = " AND ".join([w for w in self._where if self.__is__join_or_include_codition__(include, w)]) if self._where else ""
                if len(__conditions_include)>0:
                    _where = f"WHERE ({__conditions_include})"
                    _orwhere = '' if len(self._orwhere) == 0 else ' OR '.join([f"({' AND '.join([w for w in conditions if self.__is__join_or_include_codition__(include, w)])} )" for block, conditions in self._orwhere.items()])
                    if len(_orwhere)>0:
                        _where = f"t{_where} OR {_orwhere}"
                stetament = f"SELECT {_include_select} FROM {_include_key.table} {include} INNER JOIN {_include_key.intermediate} inter_{_include_key.intermediate} ON (inter_{_include_key.intermediate}.{_include_key.rel_key} = {include}.{_include_key.key} AND inter_{_include_key.intermediate}.{_include_key.ref_key} = {obj[ _include_key.reference].value}) {_where}"
            return stetament
        return None


    def __is_join__(self, table_name):
        return (not self._join is None and table_name in self._join) or (not self._inner is None and table_name in self._inner)

    def __is_include__(self, table_name):
        return not self._include is None and table_name in self._include

    def __is__main_select__(self, field):
        if not '.' in field:
            return True
        else:
            table_name = field.split('.')[0].strip()
            return not self.__is_join__(table_name) and not self.__is_include__(table_name)

    def __is__join_select__(self, field):
        if '.' in field:
            table_name = field.split('.')[0].strip()
            return self.__is_join__(table_name)
        else:
            return False

    def __is__include_select__(self, include, field):
        if '.' in field:
            table_name = field.split('.')[0].strip()
            return table_name == include
        else:
            return False


    def __is__main_codition__(self, condition):
        if not self._join and not self._inner and not self._include:
            return True
        else:
            if not '.' in condition:
                return True
            else:
                is_join = any([self.__is__join_or_include_codition__(join, condition) for join in self._join]) if self._join else False
                is_inner = any([self.__is__join_or_include_codition__(inner, condition) for inner in self._inner]) if self._inner else False
                is_include = any([self.__is__join_or_include_codition__(include, condition) for include in self._include]) if self._include else False
                return not is_join and not is_inner and not is_include

    def __is__join_or_include_codition__(self, table, condition):
        if not '.' in condition:
            return False
        else:
            return f'{table}.' in condition and not re.match("\w+"+ table + "\.", condition)

    def __format_select_query__(self):

        # SELECT BLOCK
        if self._select:
            _select = ', '.join([f"{self._table}.{c} AS '{c}'" for c in self._select if self.__is__main_select__(c)])
            # IF NOT PRIMARY KEY ON SELECT, APPEND IT
            if not all([f'{self._table}.{pk}' in _select for pk in self._klass.__metadata__['pk']]):
                _select_pk = ', '.join([f"{self._table}.{pk} AS '{pk}'" for pk in self._klass.__metadata__['pk']])
                _select = f"{_select}, {_select_pk}"
        else:
            _select = ", ".join([f"{self._table}.{field} AS '{field}'" for field in self._klass.__dict__ if not field.startswith("_") and not self._klass[field].__class__.__name__.startswith("Obj")])


        _distinct = f'DISTINCT({",".join(self._distinct)})' if self._distinct else None

        _select = f"{_select}, {_distinct}" if _distinct else f"{_select}"

        _alias = ",".join([f'{alias[0]} AS {alias[1]}' for alias in self._alias]) if self._alias else None

        _select = f"{_select}, {_alias}" if _alias else f"{_select}"

        _select_join, _join = self.__format_join_query__(self._join, 'LEFT')
        _select_join = f', {_select_join}' if _select_join != '' else ''

        _select_inner, _inner = self.__format_join_query__(self._inner, 'INNER')
        _select_inner = f', {_select_inner}' if _select_inner != '' else ''

        # CONDITION BLOCK
        _where = [w for w in self._where if self.__is__main_codition__(w)] if self._where else []
        _where = f" WHERE ({' AND '.join(_where)})" if len(_where) > 0 else ''
        _orwhere = ''.join([c for c in [f" OR ({' AND '.join([w for w in conditions if self.__is__main_codition__(w)])})" for block, conditions in self._orwhere.items()] if c.strip() != 'OR ()']) if self._orwhere else ''

        # GROUP BLOCK
        _groupby =  '' if not self._groupby else f" GROUP BY ({self._groupby})"

        # HAVING BLOCK
        _having = '' if not self._having else f" HAVING ({' AND '.join(self._having)})"
        _orhaving = '' if len(self._orhaving) == 0 else  ''.join([f" OR ({' AND '.join([w for w in conditions])})" for block, conditions in self._orhaving.items()])

        # ORDER BLOCK
        _orderby = '' if not self._orderby else f" ORDER BY {','.join(self._orderby)}"

        # LIMIT BLOCK
        _limit = '' if not self._limit else f" LIMIT {self._limit[0]},{self._limit[1]}"

        _stetament =  f"SELECT {_select} {_select_join} {_select_inner} FROM {self._table} {_join} {_inner} {_where}{_orwhere}{_groupby}{_having}{_orhaving}{_orderby}{_limit}"

        return  _stetament


    def __format_count_query__(self):

        # SELECT BLOCK
        _select = 'COUNT(*)' if not self._select else f"COUNT({', '.join(self._select)})"

        _distinct = f'DISTINCT({",".join(self._distinct)})' if self._distinct else None

        _select = f"{_select}, {_distinct}" if _distinct else f"{_select}"

        _alias = ",".join([f'{alias[0]} AS {alias[1]}' for alias in self._alias]) if self._alias else None

        _select = f"{_select}, {_alias}" if _alias else f"{_select}"

        _select_join, _join = self.__format_join_query__(self._join, 'LEFT')
        _select_join = f', {_select_join}' if _select_join != '' else ''

        _select_inner, _inner = self.__format_join_query__(self._inner, 'INNER')
        _select_inner = f', {_select_inner}' if _select_inner != '' else ''

        # CONDITION BLOCK
        _where = [w for w in self._where if self.__is__main_codition__(w)] if self._where else []
        _where = f" WHERE ({' AND '.join(_where)})" if len(_where) > 0 else ''
        _orwhere = ''.join([c for c in [f" OR ({' AND '.join([w for w in conditions if self.__is__main_codition__(w)])})" for block, conditions in self._orwhere.items()] if c.strip() != 'OR ()']) if self._orwhere else ''

        # GROUP BLOCK
        _groupby =  '' if not self._groupby else f" GROUP BY ({self._groupby})"

        # HAVING BLOCK
        _having = '' if not self._having else f" AND ({' AND '.join(self._having)})"
        _orhaving = '' if len(self._orhaving) == 0 else  ''.join([f" OR ({' AND '.join([w for w in conditions])})" for block, conditions in self._orhaving.items()])

        # ORDER BLOCK
        _orderby = '' if not self._orderby else f" ORDER BY {','.join(self._orderby)}"

        # LIMIT BLOCK
        _limit = '' if not self._limit else f" LIMIT {self._limit[0]},{self._limit[1]}"

        _stetament =  f"SELECT {_select} FROM {self._table} {_join} {_inner} {_where}{_orwhere}{_groupby}{_having}{_orhaving}{_orderby}{_limit}"

        return  _stetament

    def __format_object_delete_query__(self, obj):
        if all([ key in obj.__metadata__['data'] for key in obj.__metadata__['pk']]):
            keys = [f"{key}={obj.__metadata__['data'][key]}" for key in obj.__metadata__['pk']]
            table =  self._inflector.tableize(obj.__class__.__name__)
            return f"DELETE FROM {table} WHERE { ' AND '.join(keys) }"
        else:
            raise Exception(f"Can't delete object {obj.__class__.__name__} whitout primary key defined")

    def __format_delete_query__(self):
        _where = [w for w in self._where if self.__is__main_codition__(w)]
        return f"DELETE FROM {self._table} WHERE ({' AND '.join(_where)})"

    def __format_object_insert_query__(self, obj):
        table =  self._inflector.tableize(obj.__class__.__name__)
        keys = ', '.join([key for key, value in obj.__metadata__['data'].items() if value is not None])
        values = ', '.join([f'%({key})s' for key, value in obj.__metadata__['data'].items() if value is not None])
        on_keys = ', '.join([f"{key}=%({key})s" for key, value in obj.__metadata__['data'].items() if value is not None])
        return f"INSERT INTO {table} ({keys}) VALUES ({values}) ON DUPLICATE KEY UPDATE {on_keys}"

    def select(self, *fields):
        self._select = self.__format_fields__(*fields)
        return self

    def distinct(self, *fields):
        self._distinct = self.__format_fields__(*fields)
        return self

    def alias(self, condition, name):
        if not self._alias:
            self._alias = [(condition, name)]
        else:
            self._alias.append((condition ,name))
        return self

    def where(self, *clause):
        self._where = self.__format_clause__(*clause)
        return self

    def orwhere(self, *clause):
        if not self._where:
            raise Exception("where('condition') must be used befere orwhere('condition')")
        self._orwhere[len(self._orwhere)] = self.__format_clause__(*clause)
        return self

    def groupby(self, field):
        self._groupby = field
        return self

    def having(self, *clause):
        self._having = self.__format_clause__(*clause)
        return self

    def orhaving(self, *clause):
        if not self._having:
            raise Exception("having('condition') must be used befere orhaving('condition')")
        self._orhaving[len(self._orhaving)] = self.__format_clause__(*clause)
        return self

    def orderby(self, *fields):
        self._orderby = self.__format_clause__(*fields)
        return self

    def limit(self, start, end):
        self._limit = (start, end)
        return self

    def join(self, *tables):
        self._join = self.__format_relationship__(*tables)
        return self

    def inner(self, *tables):
        self._inner = self.__format_relationship__(*tables)
        return self

    def include(self, *tables):
        self._include = self.__format_relationship__(*tables)
        return self

    def execute(self, query, class_name=None):
        result = self._conn.fetchall(query)
        if class_name:
            _class = getattr(__import__(f'model.{class_name.lower()}', fromlist=[class_name]), class_name)
            _klass = _class()
            result = datatype.ListType(_class).add([_class(**item) for item in result])
        return result

    @property
    def fetch(self):
        query = self.__format_select_query__()
        return self._conn.fetchall(query)

    @property
    def all(self):
        Debug("Formating Query")
        query = self.__format_select_query__()
        result = self._conn.fetchall(query)
        result = datatype.ListType(self._class).add([self._class(aliases=self._alias, **item) for item in result])
        if self._include:
            for item in result:
                for _include in self._include:
                    item[_include].__reset__()
                    print()
                    print()
                    print()
                    print()
                    print(item[_include].__class__)
                    print()
                    print()
                    print()
                    print()
                    item.__metadata__['relasionships'][_include] = None if not 'List' in item[_include].__class__.__name__ else []
                    _stetament_include = self.__format_include_query__(item, _include)
                    if _stetament_include:
                        _include_result = self._conn.fetchall(_stetament_include)
                        if len(_include_result)>0:
                            item.add(_include, _include_result)
        return result

    @property
    def first(self):
        Debug("Formating Query")
        self.limit(0,1)
        query = self.__format_select_query__()
        result = self._conn.fetchall(query)

        item = self._class(aliases=self._alias, **result[0]) if result else None
        if item and self._include:
            for _include in self._include:
                item[_include].__reset__()
                item.__metadata__['relasionships'][_include] = None if not 'List' in item[_include].__class__.__name__ else []
                _stetament_include = self.__format_include_query__(item, _include)
                if _stetament_include:
                    _include_result = self._conn.fetchall(_stetament_include)
                    item.add(_include, _include_result)
        return item


    @property
    def count(self):
        Debug("Formating Query")
        query = self.__format_count_query__()
        result = self._conn.fetchall(query)
        return result[0]["COUNT(*)"] if len(result) > 0  else 0

    def __commit__(self, obj, action):
        [ v.remove(obj) for k, v in self.__queue__.items() if k != action and obj in v]
        if obj and  obj.__class__.__module__.startswith("model."):
            if not obj in self.__queue__[action]:
                self.__queue__[action].append(obj)
        return self

    def add(self, obj):
        return self.__commit__(obj, 'add')

    def delete(self, obj=None):
        if obj:
            return self.__commit__(obj, 'delete')
        else:
            if self._where:
                self._conn.save(self.__format_delete_query__(), {})
                self._conn.commit()
                return None
            else:
                raise Exception("delete method requires where condition or object")

    def __save__object__(self, obj):
        Debug("Saving Object")
        def do_object(_obj):
            _add_query = self.__format_object_insert_query__(_obj)
            _last_row_id = self._conn.save(_add_query, {key:value for key, value in _obj.__metadata__['data'].items() if value is not None})
            if _last_row_id:
                _pk_key = obj.__metadata__['pk'][0]
                _obj.__setattr__(_pk_key, _last_row_id)

        do_object(obj)

        def do_relacional(_rel, _obj, _sub_item):
            Debug("Making Relasionship")
            _reference = _obj[rel].reference
            _ref_key = _obj[rel].ref_key
            _rel_key = _obj[rel].rel_key
            _key = _obj[rel].key
            _relacional_query = f"INSERT INTO {_obj[rel].intermediate} ({_ref_key}, {_rel_key}) VALUES (%({_ref_key})s, %({_rel_key})s) ON DUPLICATE KEY UPDATE {_ref_key}=%({_ref_key})s, {_rel_key}=%({_rel_key})s"
            _relacional_data = {
                _ref_key : _obj[_reference].value,
                _rel_key : _sub_item[_key].value
            }
            self._conn.save(_relacional_query, _relacional_data)

        if len(obj.__metadata__['relasionships'] )> 0:
            for rel in obj.__metadata__['relasionships']:
                if obj[rel].__class__.__name__ == 'ObjList':
                    for sub_item in obj[rel].value:
                        sub_item.__setattr__(obj[rel].key, obj[obj[rel].reference].value)
                        do_object(sub_item)
                if obj[rel].__class__.__name__ == 'ObjListOfMany':
                    for sub_item in obj[rel].value:
                        do_object(sub_item)
                        do_relacional(rel, obj, sub_item)


    def set(self, field, value):
        _where = [w for w in self._where if self.__is__main_codition__(w)] if self._where else []
        _where = f" WHERE ({' AND '.join(_where)})" if len(_where) > 0 else ''
        _orwhere = ''.join([c for c in [f" OR ({' AND '.join([w for w in conditions if self.__is__main_codition__(w)])})" for block, conditions in self._orwhere.items()] if c.strip() != 'OR ()']) if self._orwhere else ''
        query = f"UPDATE {self._table} SET {field}='{value}' {_where}{_orwhere}"
        self._conn.save(query, {})
        self._conn.commit()

    def save(self):

        # DELETE OBJECTS
        Debug("Process Delete Queue")
        for obj_delete in self.__queue__['delete']:
            _delete_query = self.__format_object_delete_query__(obj_delete)
            self._conn.save(_delete_query, {})
            obj_delete.__init__()
        self.__queue__['delete'] = []

        # ADD/UPDATE OBJECTS
        Debug("Process Insert/Update Queue")
        for obj_add in self.__queue__['add']:
            self.__save__object__(obj_add)
        self.__queue__['add'] = []

        self._conn.commit()

    def close(self):
        self._conn.close()
