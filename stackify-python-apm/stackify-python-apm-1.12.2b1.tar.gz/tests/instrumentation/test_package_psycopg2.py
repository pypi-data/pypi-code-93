import json
from datetime import datetime
from unittest import TestCase
from unittest import SkipTest

try:
    import psycopg2
except Exception:
    raise SkipTest('Skipping due to version incompatibility')

from stackifyapm.base import Client
from stackifyapm.conf import constants
from stackifyapm.traces import execution_context
from stackifyapm.traces import Transaction
from stackifyapm.instrumentation import register
from stackifyapm.instrumentation import control
from stackifyapm.instrumentation.packages.psycopg2 import Psycopg2RegisterTypeInstrumentation

CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
    "PREFIX_ENABLED": True,
}


class Psycopg2InstrumentationTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        register._cls_registers = {
            "stackifyapm.instrumentation.packages.psycopg2.Psycopg2Instrumentation",
            "stackifyapm.instrumentation.packages.psycopg2.Psycopg2RegisterTypeInstrumentation",
        }

        self.params = {
            'database': 'test',
            'password': 'password',
            'user': 'postgres',
            'host': '127.0.0.1',
            'port': 1114,
        }

        self.conn = psycopg2.connect(**self.params)
        self.cursor = self.conn.cursor()

        self.cursor.execute("CREATE TABLE testdb(id INT, name VARCHAR(30));")
        self.conn.commit()

        control.instrument()
        self.client.begin_transaction("transaction_test")

    def tearDown(self):
        control.uninstrument()
        self.cursor.execute("DROP TABLE testdb;")
        self.conn.commit()

    def test_connect(self):
        psycopg2.connect(**self.params)

        self.assert_span(
            call='db.postgresql.connect',
            subcategory='Connect',
            component_category='Database',
            component_detail='Open Connection',
            provider='psycopg2',
        )

    def test_execute(self):
        self.conn = psycopg2.connect(**self.params)
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT * FROM testdb WHERE name LIKE 'JayR'")
        self.conn.commit()

        self.assert_span(
            call='db.postgresql.sql',
            subcategory='Execute',
            component_category='DB Query',
            component_detail='Execute SQL Query',
            provider='postgresql',
            sql='SELECT * FROM testdb WHERE name LIKE \'JayR\'',
        )

    def test_truncated_statement(self):
        statement = "SELECT * FROM testdb WHERE name LIKE '{}'".format('X' * 100000)
        self.conn = psycopg2.connect(**self.params)
        self.cursor = self.conn.cursor()
        self.cursor.execute(statement)
        self.conn.commit()

        transaction = execution_context.get_transaction()
        assert transaction
        assert transaction.get_spans()
        assert len(transaction.get_spans()) == 2
        span = transaction.get_spans()[1]

        span_data = span.to_dict()

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'db.postgresql.sql'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Database'
        assert span_data['props']['SUBCATEGORY'] == 'Execute'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'DB Query'
        assert span_data['props']['COMPONENT_DETAIL'] == 'Execute SQL Query'
        assert span_data['props']['PROVIDER'] == 'postgresql'
        assert span_data['props']['URL'] == '127.0.0.1:1114'
        assert len(span_data['props']['SQL']) == constants.SQL_STATEMENT_MAX_LENGTH
        assert span_data['props']['SQL_TRUNCATED']

    def test_prepared_statement(self):
        statement = "SELECT * FROM testdb WHERE name LIKE %s"
        argument = ('JayR',)

        self.conn = psycopg2.connect(**self.params)
        self.cursor = self.conn.cursor()
        self.cursor.execute(statement, argument)
        self.conn.commit()

        transaction = execution_context.get_transaction()
        assert transaction
        assert transaction.get_spans()
        assert len(transaction.get_spans()) == 2
        span = transaction.get_spans()[1]

        span_data = span.to_dict(config=self.client.config)

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'db.postgresql.sql'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Database'
        assert span_data['props']['SUBCATEGORY'] == 'Execute'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'DB Query'
        assert span_data['props']['COMPONENT_DETAIL'] == 'Execute SQL Query'
        assert span_data['props']['PROVIDER'] == 'postgresql'
        assert span_data['props']['URL'] == '127.0.0.1:1114'
        assert span_data['props']['SQL'] == 'SELECT * FROM testdb WHERE name LIKE %s'
        assert span_data['props']['PREFIX_SQL_PARAMETERS'] == json.dumps([{1: 'JayR'}])
        assert span_data['props']['PREFIX_SQL_PARAMETER_COUNT'] == '1'

    def test_prepared_statement_with_datetime_param(self):
        statement = "SELECT * FROM testdb WHERE name::date = %s"
        argument = (datetime.now(),)

        self.conn = psycopg2.connect(**self.params)
        self.cursor = self.conn.cursor()
        self.cursor.execute(statement, argument)
        self.conn.commit()

        transaction = execution_context.get_transaction()
        assert transaction
        assert transaction.get_spans()
        assert len(transaction.get_spans()) == 2
        span = transaction.get_spans()[1]

        span_data = span.to_dict(config=self.client.config)

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'db.postgresql.sql'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Database'
        assert span_data['props']['SUBCATEGORY'] == 'Execute'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'DB Query'
        assert span_data['props']['COMPONENT_DETAIL'] == 'Execute SQL Query'
        assert span_data['props']['PROVIDER'] == 'postgresql'
        assert span_data['props']['URL'] == '127.0.0.1:1114'
        assert span_data['props']['SQL'] == 'SELECT * FROM testdb WHERE name::date = %s'
        assert span_data['props']['PREFIX_SQL_PARAMETERS'] == json.dumps([{1: str(argument[0])}])
        assert span_data['props']['PREFIX_SQL_PARAMETER_COUNT'] == '1'
        print(span_data)

    def test_prepared_statement_with_int_param(self):
        statement = "SELECT * FROM testdb WHERE id = %s"
        argument = (1,)

        self.conn = psycopg2.connect(**self.params)
        self.cursor = self.conn.cursor()
        self.cursor.execute(statement, argument)
        self.conn.commit()

        transaction = execution_context.get_transaction()
        assert transaction
        assert transaction.get_spans()
        assert len(transaction.get_spans()) == 2
        span = transaction.get_spans()[1]

        span_data = span.to_dict(config=self.client.config)

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'db.postgresql.sql'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Database'
        assert span_data['props']['SUBCATEGORY'] == 'Execute'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'DB Query'
        assert span_data['props']['COMPONENT_DETAIL'] == 'Execute SQL Query'
        assert span_data['props']['PROVIDER'] == 'postgresql'
        assert span_data['props']['URL'] == '127.0.0.1:1114'
        assert span_data['props']['SQL'] == 'SELECT * FROM testdb WHERE id = %s'
        assert span_data['props']['PREFIX_SQL_PARAMETERS'] == json.dumps([{1: '1'}])
        assert span_data['props']['PREFIX_SQL_PARAMETER_COUNT'] == '1'

    def test_prepared_statement_with_multiple_params(self):
        statement = "SELECT * FROM testdb WHERE name LIKE %s OR name LIKE %s"
        argument = ('JayR', 'Python')

        self.conn = psycopg2.connect(**self.params)
        self.cursor = self.conn.cursor()
        self.cursor.execute(statement, argument)
        self.conn.commit()

        transaction = execution_context.get_transaction()
        assert transaction
        assert transaction.get_spans()
        assert len(transaction.get_spans()) == 2
        span = transaction.get_spans()[1]

        span_data = span.to_dict(config=self.client.config)

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'db.postgresql.sql'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Database'
        assert span_data['props']['SUBCATEGORY'] == 'Execute'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'DB Query'
        assert span_data['props']['COMPONENT_DETAIL'] == 'Execute SQL Query'
        assert span_data['props']['PROVIDER'] == 'postgresql'
        assert span_data['props']['URL'] == '127.0.0.1:1114'
        assert span_data['props']['SQL'] == 'SELECT * FROM testdb WHERE name LIKE %s OR name LIKE %s'
        assert span_data['props']['PREFIX_SQL_PARAMETERS'] == json.dumps([{1: 'JayR'}, {2: 'Python'}])
        assert span_data['props']['PREFIX_SQL_PARAMETER_COUNT'] == '2'

    def test_prepared_statement_limit_to_1000_char_param_value(self):
        statement = "SELECT * FROM testdb WHERE name LIKE %s"
        argument = ('JayR{}'.format('s' * 2000),)

        self.conn = psycopg2.connect(**self.params)
        self.cursor = self.conn.cursor()
        self.cursor.execute(statement, argument)
        self.conn.commit()

        transaction = execution_context.get_transaction()
        assert transaction
        assert transaction.get_spans()
        assert len(transaction.get_spans()) == 2
        span = transaction.get_spans()[1]

        span_data = span.to_dict(config=self.client.config)
        prefix_sql_parameters = json.loads(span_data['props']['PREFIX_SQL_PARAMETERS'])

        assert len(prefix_sql_parameters) == 1
        assert len(prefix_sql_parameters[0]['1']) == 1000
        assert span_data['props']['PREFIX_SQL_PARAMETER_COUNT'] == '1'

    def test_prepared_statement_limit_to_100_params(self):
        statement = "SELECT * FROM testdb WHERE name LIKE ANY(ARRAY[{}])".format(",".join(["%s"] * 101))
        argument = ('JayR',) * 101

        self.conn = psycopg2.connect(**self.params)
        self.cursor = self.conn.cursor()
        self.cursor.execute(statement, argument)
        self.conn.commit()

        transaction = execution_context.get_transaction()
        assert transaction
        assert transaction.get_spans()
        assert len(transaction.get_spans()) == 2
        span = transaction.get_spans()[1]

        span_data = span.to_dict(config=self.client.config)
        prefix_sql_parameters = json.loads(span_data['props']['PREFIX_SQL_PARAMETERS'])

        assert len(prefix_sql_parameters) == 100
        assert span_data['props']['PREFIX_SQL_PARAMETER_COUNT'] == '101'

    def assert_span(self, call, subcategory, component_category, component_detail, provider, sql=None):
        transaction = execution_context.get_transaction()
        assert transaction
        assert transaction.get_spans()
        if sql:
            assert len(transaction.get_spans()) == 2
            span = transaction.get_spans()[1]
        else:
            assert len(transaction.get_spans()) == 1
            span = transaction.get_spans()[0]

        span_data = span.to_dict()

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == call
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Database'
        assert span_data['props']['SUBCATEGORY'] == subcategory
        assert span_data['props']['COMPONENT_CATEGORY'] == component_category
        assert span_data['props']['COMPONENT_DETAIL'] == component_detail
        assert span_data['props']['PROVIDER'] == provider
        assert span_data['props']['URL'] == '127.0.0.1:1114'
        if sql:
            assert span_data['props']['SQL'] == sql


class ConnectionOrCursorMock(object):
    __wrapped__ = 'some_value'


class Psycopg2RegisterTypeInstrumentationTest(TestCase):
    def setUp(self):
        client = Client(CONFIG)
        transaction = Transaction("request", None, meta_data=client.get_meta_data())
        execution_context.set_transaction(transaction)

    def tearDown(self):
        execution_context.get_transaction(clear=True)

    def test_with_connection_or_cursor_in_kwargs(self):
        instrument = Psycopg2RegisterTypeInstrumentation()

        args, kwargs = instrument.call(None, None, lambda *args, **kwargs: (args, kwargs), None, (), {"conn_or_curs": ConnectionOrCursorMock()})

        assert args == ()
        assert kwargs["conn_or_curs"] == 'some_value'

    def test_with_connection_or_cursor_in_args(self):
        instrument = Psycopg2RegisterTypeInstrumentation()

        args, kwargs = instrument.call(None, None, lambda *args, **kwargs: (args, kwargs), None, ('foo', ConnectionOrCursorMock()), {})

        assert args == ('foo', 'some_value')
        assert not kwargs

    def test_with_register_json(self):
        instrument = Psycopg2RegisterTypeInstrumentation()

        args, kwargs = instrument.call(None, 'register_json', lambda *args, **kwargs: (args, kwargs), None, (ConnectionOrCursorMock(), 'foo'), {})

        assert args == ('some_value', 'foo')
        assert not kwargs
