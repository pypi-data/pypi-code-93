import unittest
from ibm_watson_machine_learning.tests.utils import is_cp4d
from ibm_watson_machine_learning.tests.autoai.abstract_tests_classes import\
    AbstractTestAutoAIDatabaseConnection


@unittest.skipIf(not is_cp4d(), "Not supported on Cloud")
class TestAutoAIMSSQLServer(AbstractTestAutoAIDatabaseConnection, unittest.TestCase):
    database_name = "sqlserver"
    schema_name = "connections"
    max_connection_nb = None


@unittest.skipIf(not is_cp4d(), "Not supported on Cloud")
class TestAutoAIDB2(AbstractTestAutoAIDatabaseConnection, unittest.TestCase):
    database_name = "db2"
    schema_name = "CJB94327"
    table_name = "IRIS"
    max_connection_nb = 2


@unittest.skipIf(not is_cp4d(), "Not supported on Cloud")
class TestAutoAIPostgresSQL(AbstractTestAutoAIDatabaseConnection, unittest.TestCase):
    database_name = "postgresql"
    schema_name = "public"
    max_connection_nb = None


@unittest.skipIf(not is_cp4d(), "Not supported on Cloud")
@unittest.skip("The writing of training data is broken for now.")
class TestAutoAIMySQL(AbstractTestAutoAIDatabaseConnection, unittest.TestCase):
    database_name = "mysql"
    schema_name = "mysql"
    max_connection_nb = 15

if __name__ == "__main__":
    unittest.main()
