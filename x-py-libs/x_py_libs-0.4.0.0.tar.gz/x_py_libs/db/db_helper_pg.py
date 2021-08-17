# -*- coding=utf-8 -*-

from enum import Enum
import sys
import psycopg2
from psycopg2.extras import DictCursor, RealDictCursor

from x_py_libs.db import BaseDBHelper


class DBOperatorEnum(Enum):
    EQUAL_TO = '='
    NOT_EQUAL_TO = '!='
    LIKE = 'LIKE'
    NOT_LIKE = 'NOT LIKE'
    IN = 'IN'
    GREATER_THAN = '>'
    LESS_THAN = '>'
    GREATER_THAN_OR_EQUAL_TO = '>='
    LESS_THAN_OR_EQUAL_TO = '>='
    POSIX = '~'


class DBAndOrEnum(Enum):
    AND = 'AND'
    OR = 'OR'


class DBConditionParamsTypeEnum(Enum):
    P = 0
    C = 1


__db_expression = {
    'field': {
        'concat': {
            'comma_lr': """CONCAT(',', %s, ',')"""
        },
        'cast': {
            'varchar': """CAST(%s AS VARCHAR)"""
        }
    },
    'params': {
        'like': {
            'lr': '%%%s%%',
            'comma_lr': '%%,%s,%%'
        },
        'in': ' (%s) '
    }
}

DBExpression = __db_expression


class DBConditionModel(object):

    field = ''
    field_expression = ''
    operator = DBOperatorEnum.EQUAL_TO
    params = None
    params_expression = ''
    params_type = DBConditionParamsTypeEnum.P
    params_brackets = False
    and_or = DBAndOrEnum.AND
    use_and_or = True
    inner_and_or = DBAndOrEnum.AND

    def __init__(self):
        pass

    def __init__(self, field='', field_expression='', operator=DBOperatorEnum.EQUAL_TO, params=None, params_expression='', params_type=DBConditionParamsTypeEnum.P, params_brackets=False, and_or=DBAndOrEnum.AND, use_and_or=True, inner_and_or=DBAndOrEnum.AND, use_inner_and_or=False):

        self.field = field
        self.field_expression = field_expression
        self.operator = operator
        # print('operator:', operator, type(operator), operator.value, type(operator.value))
        # print('self.operator:', self.operator, type(self.operator), self.operator.value, type(self.operator.value))
        self.params = params
        self.params_expression = params_expression
        self.params_type = params_type
        self.params_brackets = params_brackets
        self.and_or = and_or
        self.use_and_or = use_and_or
        self.use_inner_and_or = use_inner_and_or
        self.inner_and_or = inner_and_or


class DBConditionHelper(object):

    @staticmethod
    def get_in_condition(field, params, **kwargs):
        return DBConditionModel(
            field=field,
            params=params,
            params_brackets=True,
            operator=DBOperatorEnum.IN,
            **kwargs
        )

    @staticmethod
    def get_equal_condition(field, params):
        return DBConditionModel(
            field=field,
            params=params,
        )

    @staticmethod
    def get_like_lr_condition(field, params, has_comma=True, **kwargs):
        field_expression = ''
        params_expression = DBExpression['params']['like']['lr']
        if has_comma:
            field_expression = DBExpression['field']['concat']['comma_lr']
            params_expression = DBExpression['params']['like']['comma_lr']

        return DBConditionModel(
            field=field,
            field_expression=field_expression,
            operator=DBOperatorEnum.LIKE,
            params=params,
            params_expression=params_expression,
            **kwargs
        )

    @staticmethod
    def get_posix_condition(field, params, has_field_cast_varchar_exp=True, **kwargs):
        field_expression = ''
        if has_field_cast_varchar_exp:
            field_expression = DBExpression['field']['cast']['varchar']
        return DBConditionModel(
            field=field,
            field_expression=field_expression,
            operator=DBOperatorEnum.POSIX,
            params=params,
            **kwargs
        )


class PgDBHelper(BaseDBHelper):

    def connect(self):
        try:
            conn = psycopg2.connect(self.connect_string, cursor_factory=DictCursor)
            conn.set_client_encoding('UTF8')
            # print(conn)
            return conn
        except psycopg2.Error as e:
            print('psycopg2 error:', e.pgerror)
            return None

    def __analyze_condition(self, condition):
        __params = []
        __condition = ''
        __conditions = []

        operator = condition.operator.value
        params_type = condition.params_type

        use_and_or = condition.use_and_or
        and_or = condition.and_or.value
        if not use_and_or:
            and_or = ''

        use_inner_and_or = condition.use_inner_and_or
        inner_and_or = condition.inner_and_or.value

        # use_and_or = condition.use_and_or
        # and_or = condition.and_or.value
        # if not use_and_or:
        #     and_or = ''

        field = condition.field
        field_expression = condition.field_expression
        if field_expression != '':
            field = field_expression % field

        __c = ' ' + field + ' ' + operator + ' '
        # __c = (inner_and_or if use_inner_and_or else and_or) + ' ' + field + ' ' + operator + ' '
        # print('o:', o, type(o))
        # print('and_or:', and_or, type(and_or))
        # print('f:', f, type(f))
        # print('fe:', fe, type(fe))
        # print('__c:', __c)

        params = condition.params
        params_expression = condition.params_expression
        new_params = []

        if type(params) is not list:
            params = [params]

        # if pe != '':
            # p = pe % p
        new_params = [param if params_expression == '' else (params_expression % param) for param in params]

        # print('pe:', pe)
        # print('new_params:', new_params)

        for param in new_params:
            nc = __c
            if params_type == DBConditionParamsTypeEnum.P:
  
                if operator == 'IN':
                    param = tuple(param.split(','))
                    
                nc += ' %s ' # if not condition.params_brackets else ' (%s) '
                __params.append(param)
            else:
                nc += param

            # __condition += nc + ' '
            __conditions.append(nc)

        __condition = (inner_and_or if use_inner_and_or else and_or).join(__conditions)

        if use_inner_and_or:
            __condition = ' (' + __condition + ') '

        __condition = and_or + __condition

        # print('__params:', __params)
        # print('__condition:', __condition)

        return __params, __condition

    # def get_one(self, table_name, fields, sc=None, conditions=None):
    #     rst, cnt = self.get_list(table_name, fields, sc=sc, conditions=conditions, order_field=None, order_type=None, count=False, pagination=False)
    #     return rst[0] if len(rst) > 0 else None

    def get_list(self, table_name, fields, sc=None, conditions=None, rawConditions='', order_field='id', order_type='DESC', page_index=0, page_size=10, count=True, pagination=True):
        params = []
        condition = ''
        rst = None
        cnt = 0

        if conditions is not None:

            for c in conditions:
                __cc = ''
                template = ''
                t = type(c)

                if t is not list:
                    c = [c]
                    template = '%s'
                else:
                    template = ' AND (%s) '

                for c2 in c:
                    __params, __condition = self.__analyze_condition(c2)
                    params.extend(__params)
                    __cc += __condition
                # print('__cc:', __cc)

                condition += template % __cc
        
        if rawConditions != '':
            condition += rawConditions

        rst, cnt = self.get_list_base(table_name, fields, condition, params, order_field=order_field, order_type=order_type, sc=sc, page_index=page_index, page_size=page_size, count=count, pagination=pagination)
        return rst, cnt

    def get_list_base(self, table_name, fields, condition='', params=None, order_field='id', order_type='DESC', sc=None, page_index=0, page_size=10, count=True, pagination=True):
        cnt = 0
        if pagination:
            cnt_sql = """SELECT COUNT(1) AS cnt FROM """ + table_name + ' WHERE 1 = 1 ' + condition + """;"""
            rst = self.fetch_one(cnt_sql, params)
            cnt = rst['cnt']

        sql = """SELECT """ + fields + """ FROM """ + table_name
        sql += """ WHERE 1 = 1 """
        sql += condition

        if order_field is not None and order_type is not None:
            order_field = [order_field] if type(order_field) is str else order_field
            order_type = [order_type] if type(order_type) is str else order_type

            if len(order_type) != len(order_field):
                order_type = list(map(lambda x: order_type[0], range(len(order_field))))

            sort_list = list(map(lambda f, t: """ %s %s """ % (f, t), order_field, order_type))

            sql += """ ORDER BY """ + ','.join(sort_list)

        if pagination:
            if page_size > 0:
                sql += """ LIMIT %s OFFSET %s """
                params.append(page_size)
                params.append(page_size*page_index)

            # __page_size = 10
            # __page_index = 0

            # if sc is not None:
            #     __page_size = int(sc['pageSize'] if sc['pageSize'] is not None else 10)
            #     __page_index = int(sc['pageIndex'] if sc['pageIndex'] is not None else 1)-1
            # else:
            #     __page_size = page_size
            #     __page_index = page_index

            # if __page_size > 0:
            #     sql += """ LIMIT %s OFFSET %s """
            #     params.append(__page_size)
            #     params.append(__page_size*__page_index)

        sql += """;"""

        # print(sql, params)

        rst = self.fetch_all(sql, params)
        return rst, cnt

    def fetch_returning_id(self, sql, *params, **kw):
        sql = sql + """ RETURNING id;"""

        def callback(cur):
            rst = cur.fetchone()
            id = rst.get('id')
            return 0 if id is None else id

        return self.execute_sql(sql, callback, *params, **kw)

    def fetch_rowcount(self, sql, *params, **kw):
        def callback(cur):
            # print('cur:',cur)
            return cur.rowcount

        return self.execute_sql(sql, callback, *params, **kw)

    def fetch_one(self, sql, *params, **kw):
        def callback(cur):
            return cur.fetchone()

        return self.execute_sql(sql, callback, *params, **kw)

    def fetch_all(self, sql, *params, **kw):
        def callback(cur):
            return cur.fetchall()

        return self.execute_sql(sql, callback, *params, **kw)

    def execute_sql(self, sql, callback, *params, **kw):
        conn = self.connect()

        if conn == None:
            return None

        # print(sql, *params, type(params), len(params), **kw)
        is_multiple = False if kw.get('is_multiple') == None else kw['is_multiple']
        # print('--kw--:', kw, kw.get('is_multiple'), is_multiple)

        cur = conn.cursor(cursor_factory=RealDictCursor)
        # cur = conn.cursor()
        rst = None

        if is_multiple:
            psycopg2.extras.execute_values(cur, sql, params, page_size=9999)
        else:
            if params is not None:
                # print('sql:', cur.mogrify(sql, *params))
                cur.execute(sql, *params)
            else:
                cur.execute(sql)

        # rst = cur.fetchone()

        rst = callback(cur)
        conn.commit()
        conn.close()
        # print('rst:',rst)
        return rst

    def callproc(self, proc_name, *params):
        conn = self.connect()

        if conn == None:
            return None

        cur = conn.cursor()
        cur.callproc(proc_name, *params)
        rst = cur.fetchall()

        conn.commit()
        conn.close()
        return rst


"""
    # def execute_values(self, sql, *params):
    #     conn = db_helper.connect()

    #     if conn == None:
    #         return None

    #     print(params, type(params), list(params))

    #     cur = conn.cursor()
    #     psycopg2.extras.execute_values(cur, sql, params)
    #     rst = cur.rowcount
    #     conn.commit()
    #     conn.close()
    #     return rst
"""
