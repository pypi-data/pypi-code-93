from unittest import TestCase
import os
from os import path
import pandas as pd
import time
from tests.dummies import Dummy, CsvDataService_Dummy

class Test_ICsvDataService(TestCase):

    def test_addobj(self):
        dir = os.path.dirname(os.path.abspath(__file__))
        data_file = '/testData/utdummies.csv'
        file_path = dir + data_file

        try:
            ''' Arrange'''
            data_service = CsvDataService_Dummy(data_file_path=file_path)
            dummy = Dummy(
                id=0,
                a=1,
                b=2,
                c=3
            )

            ''' Act '''
            data_service.add_or_update(Dummy, objs=[dummy])

            ''' Assert '''
            df = pd.read_csv(file_path)
            self.assertEqual(df.shape[0], 1, f"{df.shape[0]} DNE 1")

        finally:
            ''' Cleanup '''
            if path.exists(file_path):
                os.remove(file_path)

    def test_updateobj(self):
        dir = os.path.dirname(os.path.abspath(__file__))
        data_file = '/testData/utdummies.csv'
        file_path = dir + data_file

        try:
            ''' Arrange'''
            data_service = CsvDataService_Dummy(data_file_path=file_path)
            dummy = Dummy(
                id=0,
                a=1,
                b=2,
                c=3
            )

            ''' Act '''
            data_service.add_or_update(Dummy, objs=[dummy])
            new_val = 100
            dummy.c = new_val
            data_service.add_or_update(Dummy, objs=[dummy])

            ''' Assert '''
            df = pd.read_csv(file_path)
            self.assertEqual(df.shape[0], 1, f"{df.shape[0]} DNE 1")
            self.assertEqual(df.at[0, 'c'], new_val,
                             f"{df.at[0, 'c']} DNE {new_val}")

        finally:
            ''' Cleanup '''
            if path.exists(file_path):
                os.remove(file_path)

    def test_retrieve_obj_data__valid_values(self):
        dir = os.path.dirname(os.path.abspath(__file__))
        data_file = '/testData/utdummies.csv'
        file_path = dir + data_file

        try:
            ''' Arrange'''
            data_service = CsvDataService_Dummy(data_file_path=file_path)
            identifier = 'a'
            dummies = []
            for ii in range(0, 5):
                dummies.append(Dummy(
                    id=0,
                    a=ii,
                    b=2,
                    c=3
                ))
            data_service.add_or_update(Dummy, objs=dummies)

            ''' Act '''
            ret_ids = ["1", "2", "3"]
            objs = data_service.retrieve_objs(Dummy, ids=ret_ids)

            ''' Assert '''
            self.assertIsNotNone(objs, "Expected real values")
            self.assertEqual(type(objs), list,
                             f"Return should be of type: {list}, but type {type(objs)} was returned")
            self.assertEqual(len(objs), 3, f"Wrong number of objs returned: {len(objs)} DNE 3")
            [self.assertIn(str(vars(obj)[identifier]), ret_ids) for obj in objs]

        finally:
            ''' Cleanup '''
            if path.exists(file_path):
                os.remove(file_path)

    def test_retrieve_equity_data__invalid_values(self):
        dir = os.path.dirname(os.path.abspath(__file__))
        data_file = '/testData/utdummies.csv'
        file_path = dir + data_file

        try:
            ''' Arrange'''
            data_service = CsvDataService_Dummy(data_file_path=file_path)
            identifier = 'a'

            for ii in range(0, 5):
                dummy = Dummy(
                    id=ii,
                    a=ii,
                    b=2,
                    c=3
                )
                data_service.add_or_update(Dummy, objs=[dummy])

            ''' Act '''
            ret_ids = ["a", "b", "c"]
            objs = data_service.retrieve_objs(Dummy, ids=ret_ids)

            ''' Assert '''
            self.assertIsNotNone(objs, "Expected real values for equities")
            self.assertEqual(type(objs), list,
                             f"Return should be of type: {list}, but type {type(objs)} was returned")
            self.assertEqual(len(objs), 0, f"Wrong number of equities returned: {len(objs)} DNE 0")
            [self.assertIn(str(vars(obj)[identifier]), ret_ids) for obj in objs]

        finally:
            ''' Cleanup '''
            if path.exists(file_path):
                os.remove(file_path)

    def test_delete(self):
        dir = os.path.dirname(os.path.abspath(__file__))
        data_file = '/testData/utdummies.csv'
        file_path = dir + data_file

        try:
            ''' Arrange'''
            data_service = CsvDataService_Dummy(data_file_path=file_path)
            identifier = 'a'

            dummies = []
            for ii in range(0, 5):
                dummy = Dummy(
                    id=ii,
                    a=ii,
                    b=2,
                    c=3
                )
                dummies.append(dummy)
            data_service.add_or_update(Dummy,  objs=dummies)

            ''' Act '''
            ret_ids = ["1", "2", "3"]
            successful_deletes = data_service.delete(obj_type=Dummy, ids=ret_ids)

            ''' Assert '''
            df = pd.read_csv(file_path)
            self.assertEqual(df.shape[0], 2, f"{df.shape[0]} DNE 2")
            [self.assertNotIn(row[identifier], ret_ids) for i, row in df.iterrows()]

        finally:
            ''' Cleanup '''
            if path.exists(file_path):
                os.remove(file_path)

    def test_add_or_update__bulk_performance(self):
        dir = os.path.dirname(os.path.abspath(__file__))
        data_file = '/testData/utdummies.csv'
        file_path = dir + data_file

        try:
            ''' Arrange'''
            data_service = CsvDataService_Dummy(data_file_path=file_path)
            identifier = 'a'

            dummies = []
            for ii in range(0, 10000):
                dummies.append(Dummy(
                    id=ii,
                    a=ii,
                    b=2,
                    c=3
                ))

            stored = data_service.add_or_update(Dummy, objs=dummies)
            for obj in stored:
                obj.c = 100

            ''' Act '''
            time_start = time.perf_counter()
            updated_objs = data_service.add_or_update(Dummy, objs=stored)
            elapsed = time.perf_counter() - time_start


            ''' Assert '''
            self.assertLess(elapsed, 3)
            [self.assertEqual(str(vars(obj)['c']), '100') for obj in updated_objs]

        finally:
            ''' Cleanup '''
            if path.exists(file_path):
                os.remove(file_path)