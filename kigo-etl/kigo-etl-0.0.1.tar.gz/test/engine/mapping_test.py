import unittest
from kigo.etl.engine.mapping import bind_id, ID_CLASS_MAP


class MappingTestCase(unittest.TestCase):

    def tearDown(self) -> None:
        ID_CLASS_MAP.clear()

    def test_basic_mapping(self):
        # GIVEN
        obj_id = 'obj_1'

        @bind_id(object_id=obj_id)
        class SomeClass:
            data_1 = '[31:43]'
            data_2 = '[49:61]'

        # THEN
        self.assertIsNotNone(ID_CLASS_MAP.get(obj_id, None))

    def test_basic_mapping_of_several_classes(self):
        # GIVEN
        obj_id = 'obj_1'
        obj_id_2 = 'obj_2'

        @bind_id(object_id=obj_id)
        class SomeClass:
            data_1 = '[31:43]'
            data_2 = '[49:61]'

        @bind_id(object_id=obj_id_2)
        class SomeClass2:
            data_1 = '[31:43]'
            data_2 = '[49:61]'

        # THEN
        self.assertEqual(len(ID_CLASS_MAP), 2)

    def test_basic_mapping_of_several_classes_with_the_same_id(self):
        # GIVEN
        obj_id = 'obj_1'

        @bind_id(object_id=obj_id)
        class SomeClass:
            data_1 = '[31:43]'
            data_2 = '[49:61]'

        @bind_id(object_id=obj_id)
        class SomeClass2:
            data_1 = '[31:43]'
            data_2 = '[49:61]'

        # THEN
        self.assertEqual(len(ID_CLASS_MAP), 1)
        self.assertEqual(len(ID_CLASS_MAP.get(obj_id, None)), 2)


if __name__ == '__main__':
    unittest.main()
