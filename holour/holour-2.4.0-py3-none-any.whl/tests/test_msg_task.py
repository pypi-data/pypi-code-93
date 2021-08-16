from unittest import TestCase

from holour import json_encode, json_decode
from holour.msg import Task, Pose, Vector3


class Test(TestCase):

    def test_task(self):

        task = Task('uuid', 'name', 'product_uuid', Pose(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)))
        task_string = json_encode(task)
        expected_string = '{"_type": "task", "uuid": "uuid", "name": "name", "product_uuid": "product_uuid", ' \
                          '"pose": {"_type": "pose", "name": "", "position": {"_type": "vector3", "x": 0.0, ' \
                          '"y": 0.0, "z": 0.0}, "rotation": {"_type": "vector3", "x": 0.0, "y": 0.0, "z": 0.0}}, ' \
                          '"automated": false, "conditions": [], "conditions_fulfilled": true, "description": ""}'

        self.assertIs(type(task_string), str, f"Got: {type(task_string)}. Expected {str}")
        self.assertEqual(task_string, expected_string, f"Expected {expected_string}, got: {task_string}")

        task_decoded = json_decode(task_string)
        assert type(task_decoded) == Task, f"Got: {type(task_decoded)}. Expected {Task}"
        assert task_decoded == task, "The decoded object must be equal to the encoded"

    def test_task_equals(self):
        task1 = Task('uuid', 'name', 'product_uuid', Pose(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)))
        task2 = Task('uuid', 'name', 'product_uuid', Pose(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)))
        task3 = Task('other', 'name', 'product_uuid', Pose(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)))

        assert task1 == task2
        assert task1 != task3
        assert task1 != "not status"

    def test_task_repr(self):
        task = Task('uuid', 'name', 'product_uuid', Pose(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)),
                    description="Hard task!")
        expected, got = 'Hard task!', f'{task}'

        assert expected in got, f"Expected {expected} in got: {got}"

