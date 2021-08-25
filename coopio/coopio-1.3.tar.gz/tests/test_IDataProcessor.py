from unittest import TestCase
from unittest.mock import Mock, MagicMock
from tests.dummies import Dummy, DummyDataProcessor, init_sql_dataservice, ORM_Dummy, CsvDataService_Dummy
from coopio.sql.SQLDataService import delete_db
import os


class Test_IDataProcessor(TestCase):
    # Create DataService
    servername = r'localhost\SQLEXPRESS'
    db_name = 'coopio_testdb'

    def tearDown(self) -> None:
        delete_db(self.servername, self.db_name)

    def test_add(self):
        '''Arrange'''
        mock_primary = Mock()
        mock_secondary = Mock()

        data_processor = DummyDataProcessor(mock_primary, [mock_secondary])

        dummies = []
        for ii in range(0, 5):
            dummy = Dummy(
                id=ii,
                a=ii,
                b=2,
                c=3
            )
            dummies.append(dummy)

        '''Act'''
        data_processor.add_or_update(obj_type=Dummy, objs=dummies)

        '''Assert'''
        mock_primary.add_or_update.assert_called_once_with(obj_type=Dummy, objs=dummies)
        mock_secondary.add_or_update.assert_called_once_with(obj_type=Dummy, objs=dummies)

    def test_retrieve(self):
        '''Arrange'''
        mock_primary = Mock()
        mock_secondary = Mock()

        data_processor = DummyDataProcessor(mock_primary, [mock_secondary])

        '''Act'''
        ret_ids = ["1", "2"]
        data_processor.retrieve_objs(Dummy, ids=ret_ids)

        '''Assert'''
        mock_primary.retrieve_objs.assert_called_once_with(obj_type=Dummy, ids=ret_ids)
        mock_secondary.retrieve_objs.assert_not_called()

    def test_delete(self):
        '''Arrange'''
        mock_primary = Mock()
        mock_secondary = Mock()

        mock_primary.delete = MagicMock(return_value={})
        mock_secondary.delete = MagicMock(return_value={})

        data_processor = DummyDataProcessor(mock_primary, [mock_secondary])
        dummies = []
        for ii in range(0, 5):
            dummy = Dummy(
                id=ii,
                a=ii,
                b=2,
                c=3
            )
            dummies.append(dummy)

        '''Act'''
        data_processor.delete(obj_type=Dummy, objs=dummies)

        '''Assert'''
        mock_primary.delete.assert_called_once_with(obj_type=Dummy, ids=[str(vars(dummy)[data_processor.obj_identifier]) for dummy in dummies])
        mock_secondary.delete.assert_called_once_with(obj_type=Dummy, ids=[str(vars(dummy)[data_processor.obj_identifier])  for dummy in dummies])


    def test_overwrite_peripheral_with_primary(self):
        '''Arrange'''
        dir = os.path.dirname(os.path.abspath(__file__))
        data_file = '/testData/utdummies.csv'
        file_path = dir + data_file
        primary = CsvDataService_Dummy(file_path)
        secondary = init_sql_dataservice(self.servername, self.db_name)

        data_processor = DummyDataProcessor(primary, [secondary])
        dummies = []
        for ii in range(0, 5):
            dummy = Dummy(
                id=ii,
                a=ii,
                b=2,
                c=3
            )
            dummies.append(dummy)

        '''Act'''
        data_processor.add_or_update(obj_type=Dummy, objs=dummies)
        secondary.delete(obj_type=Dummy, ids=[x.id for x in dummies])

        secondary_objects = secondary.retrieve_objs(Dummy)
        self.assertEqual(len(secondary_objects), 0)

        data_processor.overwrite_peripherals_with_primary(Dummy)

        '''Assert'''
        primary_objects = primary.retrieve_objs(Dummy)
        secondary_objects = secondary.retrieve_objs(Dummy)

        self.assertEqual(len(primary_objects), len(secondary_objects))
        self.assertNotEqual(len(primary_objects), 0)


