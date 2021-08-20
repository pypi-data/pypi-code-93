import json

from unittest import SkipTest
from unittest import TestCase

try:
    import pymssql
except Exception:
    raise SkipTest('Skipping due to version incompatibility')

from stackifyapm.base import Client
from stackifyapm.conf import constants
from stackifyapm.traces import execution_context
from stackifyapm.instrumentation import register
from stackifyapm.instrumentation import control


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


class MSSQLInstrumentationTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        register._cls_registers = {
            "stackifyapm.instrumentation.packages.pymssql.PyMSSQLInstrumentation",
        }

        self.params = {
            'database': 'test',
            'password': 'Qwert12345!',
            'user': 'SA',
            'host': '0.0.0.0',
            'port': 1115
        }

        self.conn = pymssql.connect(**self.params)
        self.cursor = self.conn.cursor()

        self.cursor.execute("CREATE TABLE testdb(id INT, name VARCHAR(30));")
        self.conn.commit()

    def tearDown(self):
        control.uninstrument()
        self.cursor.execute("DROP TABLE testdb;")
        self.conn.commit()

    def test_execute(self):
        control.instrument()
        self.client.begin_transaction("transaction_test")

        self.conn = pymssql.connect(**self.params)
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT * FROM testdb WHERE name LIKE 'JayR'")
        self.conn.commit()

        transaction = execution_context.get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict()

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'db.pymssql.sql'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Database'
        assert span_data['props']['SUBCATEGORY'] == 'Execute'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'DB Query'
        assert span_data['props']['COMPONENT_DETAIL'] == 'Execute SQL Query'
        assert span_data['props']['PROVIDER'] == 'pymssql'
        assert span_data['props']['URL'] == '0.0.0.0:1115'
        assert span_data['props']['SQL'] == 'SELECT * FROM testdb WHERE name LIKE \'JayR\''

    def test_truncated_statement(self):
        control.instrument()
        self.client.begin_transaction("transaction_test")

        statement = "SELECT * FROM testdb WHERE name LIKE '{}'".format('X' * 100000)
        self.conn = pymssql.connect(**self.params)
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute(statement)
        except Exception:
            raise SkipTest('Skipping due to truncated.DB-Lib')

        self.conn.commit()

        transaction = execution_context.get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict()

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'db.pymssql.sql'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Database'
        assert span_data['props']['SUBCATEGORY'] == 'Execute'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'DB Query'
        assert span_data['props']['COMPONENT_DETAIL'] == 'Execute SQL Query'
        assert span_data['props']['PROVIDER'] == 'pymssql'
        assert span_data['props']['URL'] == '0.0.0.0:1115'
        assert len(span_data['props']['SQL']) == constants.SQL_STATEMENT_MAX_LENGTH
        assert span_data['props']['SQL_TRUNCATED']

    def test_prepared_statement(self):
        control.instrument()
        self.client.begin_transaction("transaction_test")

        statement = "SELECT * FROM testdb WHERE name LIKE %s"
        argument = ('JayR',)

        self.conn = pymssql.connect(**self.params)
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute(statement, argument)
        except Exception:
            raise SkipTest('Skipping due to truncated.DB-Lib')

        self.conn.commit()

        transaction = execution_context.get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict(config=self.client.config)

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'db.pymssql.sql'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Database'
        assert span_data['props']['SUBCATEGORY'] == 'Execute'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'DB Query'
        assert span_data['props']['COMPONENT_DETAIL'] == 'Execute SQL Query'
        assert span_data['props']['PROVIDER'] == 'pymssql'
        assert span_data['props']['URL'] == '0.0.0.0:1115'
        assert span_data['props']['SQL'] == 'SELECT * FROM testdb WHERE name LIKE %s'
        assert span_data['props']['PREFIX_SQL_PARAMETERS'] == json.dumps([{1: 'JayR'}])
        assert span_data['props']['PREFIX_SQL_PARAMETER_COUNT'] == '1'

    def test_prepared_statement_with_multiple_params(self):
        control.instrument()
        self.client.begin_transaction("transaction_test")

        statement = "SELECT * FROM testdb WHERE name LIKE %s OR name LIKE %s"
        argument = ('JayR', 'Python')

        self.conn = pymssql.connect(**self.params)
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute(statement, argument)
        except Exception:
            raise SkipTest('Skipping due to truncated.DB-Lib')

        self.conn.commit()

        transaction = execution_context.get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict(config=self.client.config)

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'db.pymssql.sql'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Database'
        assert span_data['props']['SUBCATEGORY'] == 'Execute'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'DB Query'
        assert span_data['props']['COMPONENT_DETAIL'] == 'Execute SQL Query'
        assert span_data['props']['PROVIDER'] == 'pymssql'
        assert span_data['props']['URL'] == '0.0.0.0:1115'
        assert span_data['props']['SQL'] == 'SELECT * FROM testdb WHERE name LIKE %s OR name LIKE %s'
        assert span_data['props']['PREFIX_SQL_PARAMETERS'] == json.dumps([{1: 'JayR'}, {2: 'Python'}])
        assert span_data['props']['PREFIX_SQL_PARAMETER_COUNT'] == '2'

    def test_prepared_statement_limit_to_1000_char_param_value(self):
        control.instrument()
        self.client.begin_transaction("transaction_test")

        statement = "SELECT * FROM testdb WHERE name LIKE %s"
        argument = ('JayR{}'.format('s' * 2000),)

        self.conn = pymssql.connect(**self.params)
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute(statement, argument)
        except Exception:
            raise SkipTest('Skipping due to truncated.DB-Lib')

        self.conn.commit()

        transaction = execution_context.get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict(config=self.client.config)
        prefix_sql_parameters = json.loads(span_data['props']['PREFIX_SQL_PARAMETERS'])

        assert len(prefix_sql_parameters) == 1
        assert len(prefix_sql_parameters[0]['1']) == 1000
        assert span_data['props']['PREFIX_SQL_PARAMETER_COUNT'] == '1'

    def test_prepared_statement_limit_to_100_params(self):
        control.instrument()
        self.client.begin_transaction("transaction_test")

        statement = "SELECT * FROM testdb WHERE name LIKE ANY(ARRAY[{}])".format(",".join(["%s"] * 101))
        argument = ('JayR',) * 101

        self.conn = pymssql.connect(**self.params)
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute(statement, argument)
        except Exception:
            raise SkipTest('Skipping due to truncated.DB-Lib')

        transaction = execution_context.get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict(config=self.client.config)
        prefix_sql_parameters = json.loads(span_data['props']['PREFIX_SQL_PARAMETERS'])

        assert len(prefix_sql_parameters) == 100
        assert span_data['props']['PREFIX_SQL_PARAMETER_COUNT'] == '101'
