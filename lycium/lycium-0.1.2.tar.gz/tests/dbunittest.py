#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
import sys
import tornado.gen
from tornado.ioloop import IOLoop
from lycium.asynchttphandler import async_route, args_as_dict, request_body_as_json
from lycium.dbproxy import DbProxy
from lycium.webapplication import WebApplication

from lycium.modelutils import ModelBase, MongoBase, MODEL_DB_MAPPING
from lycium.behaviors import AppBehevior, ModifyingBehevior
from sqlalchemy import Column, Integer, SmallInteger, String
from mongoengine import StringField, IntField, DateTimeField, ObjectIdField

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

rdbms = {
    'debug_mssql': {
        'connector': "mssql",
        'driver': "pymssql",
        'host': "10.10.61.22",
        'port': 1433,
        'user': "sa",
        'pwd': "server@1",
        'db': "rris"
    },
    'debug_pg': {
        'connector': "postgresql",
        'driver': "",
        'host': "10.10.61.37",
        'port': 5432,
        'user': "opsmart",
        'pwd': "q1w2e3r4",
        'db': "bennx_app",
        # 'ext_args': {'sslmode': 'require'}
    }
}

mongodbs = {
    'debug_mongo': {
        'connector': 'mongodb',
        'host':  '10.10.2.149',
        'port': 27017,
        'user': 'starviews',
        'pwd': 'HK.bianque.27017',
        'db': 'starviews_medical'
    }
}

class AppMedicineRoutineDose(ModelBase, AppBehevior, ModifyingBehevior):
    __tablename__ = 'app_medicine_routine_dose'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    med_code = Column('med_code', String(50), index=True)
    condition_value = Column('condition_value', Integer, index=True)
    result_content = Column('result_content', String(1000))
    opip_flag = Column('opip_flag', SmallInteger)

class Application(MongoBase):
    type = StringField()
    name = StringField()
    code = StringField()
    level = StringField()
    cooperation_mode = IntField(default=1)
    sign = StringField()
    lng = StringField()
    lat = StringField()
    admin_user_id = ObjectIdField()
    appKey = StringField()
    meta = {
        'collection': 'XHHK_Application',
        'indexes': [
            ('code'),
        ]
    }

MODEL_DB_MAPPING[AppMedicineRoutineDose.__name__] = "debug_pg"

@async_route('/debug', methods=['GET'])
@tornado.gen.coroutine
def test_query_sql(handler, request):
    sql1 = 'SELECT * FROM RRIS.dbo.SmartPrint_GetReportData where 1=0'
    result1 = yield DbProxy().exec_query('debug_mssql', sql1)
    total2 = yield DbProxy().get_count(AppMedicineRoutineDose, {})
    print('total count before inserting', total2)
    one = AppMedicineRoutineDose()
    one.app_id = '766'
    one.med_code = '10024'
    one.opip_flag = 3
    one.condition_value = 14
    one.result_content = ''
    result5 = yield DbProxy().insert_item(one)
    total2 = yield DbProxy().get_count(AppMedicineRoutineDose, {})
    print('total count after inserted', total2)
    result6 = yield DbProxy().del_item(result5)
    total2 = yield DbProxy().get_count(AppMedicineRoutineDose, {})
    print('total count after delete inserted', total2)
    print('del inserted item result', result6)
    result0 = yield DbProxy().update_values(AppMedicineRoutineDose, {AppMedicineRoutineDose.id==1}, {'condition_value': 3})
    print('update row count', result0)
    result3 = yield DbProxy().query_all(AppMedicineRoutineDose, {})
    result4 = yield DbProxy().find_item(AppMedicineRoutineDose, {AppMedicineRoutineDose.id==1})
    if result4:
        result4.condition_value = 1
        result41 = yield DbProxy().update_item(result4)
        print('updated item', result41)
    result2, total = yield DbProxy().query_list(AppMedicineRoutineDose, {}, 10, 0, '', '')
    total2 = yield DbProxy().get_count(AppMedicineRoutineDose, {})
    print('result1', result1)
    print('result3', result3)
    print('result4', result4)
    print('result2 total', total, result2)
    print('total2', total2)
    
    return json.dumps({
        'total': total,
        'data': result2
    })

@async_route('/mongo', methods=['GET'])
@tornado.gen.coroutine
def test_query_mongo(handler, request):
    item = Application()
    item.name = 'TESTING'
    item.code = 'TESTING-01'
    result4 = yield DbProxy().insert_mongo(Application, item)
    print('result4', result4)
    result4.level = '33'
    result6 = yield DbProxy().save_mongo(result4)
    print('result6', result6)
    result5 = yield DbProxy().del_item_mongo(result4, {'code': 'TESTING-01'})
    print('result5', result5)
    result7 = yield DbProxy().update_mongo(Application, {'level': '22'}, {'code': 'TESTING-01'})
    print('result7', result7)
    result0 = yield DbProxy().find_one_mongo(Application, code='TESTING-01')
    print('result0', result0)
    result1 = yield DbProxy().query_all_mongo(Application, {})
    result2, total = yield DbProxy().query_list_mongo(Application, {}, 10, 0, None, None)
    result3 = yield DbProxy().mongo_aggregate(Application, [{'$group': {'_id': {'type': '$type', 'level': '$level'}, 'occurrence': { '$sum': 1 }}}, { '$sort': { "occurrence": -1 } }])
    print('result1', result1)
    print('result2', result2)
    print('result3', result3)
    return json.dumps({
        'total': total,
        'data': result2
    })

def main():
    DbProxy().setup_rdbms(rdbms)
    DbProxy().setup_mongodbs(mongodbs)

    web_app = WebApplication()
    web_app.listen(port=8081, address='0.0.0.0')
    print('starting...')
    IOLoop.instance().start()

if __name__ == "__main__":
    main()
