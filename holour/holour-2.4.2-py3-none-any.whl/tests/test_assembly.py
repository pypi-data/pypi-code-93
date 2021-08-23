from unittest import TestCase

from holour import json_encode, json_decode
from holour.msg import AddProcess, MoveTask, CompleteTask, Destination, ConfirmNeeded, ConfirmTask


class TestAddProcess(TestCase):

    def test_add_process(self):
        add_process = AddProcess('uuid')
        add_process_string = json_encode(add_process)
        expected_string = '{"_type": "add_process", "process_uuid": "uuid"}'

        assert type(add_process_string) == str
        assert add_process_string == expected_string, f"Expected {expected_string}, got: {add_process_string}"

        add_process_decoded = json_decode(add_process_string)
        assert type(add_process_decoded) == AddProcess, f"Got: {type(add_process_decoded)}. Expected {AddProcess}"
        assert add_process_decoded == add_process, "The decoded object must be equal to the encoded"

    def test_add_process_equals(self):
        at1 = AddProcess('uuid')
        at2 = AddProcess('uuid')
        at3 = AddProcess('uuid2')

        assert at1 == at2
        assert at1 != at3
        assert at1 != "not status"

    def test_add_process_repr(self):
        add_task = AddProcess('uuid')
        expected, got = 'uuid', f'{add_task}'

        assert expected in got, f"Expected {expected} in got: {got}"


class TestMoveTask(TestCase):

    def test_move_task(self):
        move_task = MoveTask('uuid', Destination.Robot)
        move_task_string = json_encode(move_task)
        expected_string = '{"_type": "move_task", "task_uuid": "uuid", "destination": "Robot"}'

        assert type(move_task_string) == str
        assert move_task_string == expected_string, f"Expected {expected_string}, got: {move_task_string}"

        move_task_decoded = json_decode(move_task_string)
        assert type(move_task_decoded) == MoveTask, f"Got: {type(move_task_decoded)}. " \
                                                              f"Expected {MoveTask}"
        assert move_task_decoded == move_task, f"The decoded object: {move_task_decoded} " \
                                                         f"must be equal to the encoded: {move_task}"

    def test_move_task_equals(self):
        mo1 = MoveTask('uuid', Destination.Human)
        mo2 = MoveTask('uuid', Destination.Human)
        mo3 = MoveTask('uuid', Destination.Robot)

        assert mo1 == mo2, f"This: {mo1}, should be equal to this: {mo2}"
        assert mo1 != mo3, f"This: {mo1}, should not be equal to this: {mo3}"
        assert mo1 != "not status"

    def test_move_task_repr(self):
        move_task = MoveTask('uuid', Destination.Robot)
        expected, got = 'Robot', f'{move_task}'

        assert expected in got, f"Expected {expected} in got: {got}"


class TestCompleteTask(TestCase):

    def test_complete_task(self):
        complete_task = CompleteTask('uuid')
        complete_task_string = json_encode(complete_task)
        expected_string = '{"_type": "complete_task", "task_uuid": "uuid"}'

        assert type(complete_task_string) == str
        assert complete_task_string == expected_string, f"Expected {expected_string}, got: {complete_task_string}"

        complete_task_decoded = json_decode(complete_task_string)
        assert type(complete_task_decoded) == CompleteTask, f"Got: {type(complete_task_decoded)}. " \
                                                                      f"Expected {CompleteTask}"
        assert complete_task_decoded == complete_task, f"The decoded object: {complete_task_decoded} " \
                                                         f"must be equal to the encoded: {complete_task}"

    def test_complete_task_equals(self):
        co1 = CompleteTask('uuid')
        co2 = CompleteTask('uuid')
        co3 = CompleteTask('uuid2')

        assert co1 == co2
        assert co1 != co3
        assert co1 != "not status"

    def test_complete_task_repr(self):
        complete_task = CompleteTask('uuid')
        expected, got = 'uuid', f'{complete_task}'

        assert expected in got, f"Expected {expected} in got: {got}"


class TestConfirmNeeded(TestCase):

    def test_confirm_needed(self):
        confirm_needed = ConfirmNeeded('uuid', True)
        confirm_needed_string = json_encode(confirm_needed)
        expected_string = '{"_type": "confirm_needed", "task_uuid": "uuid", "confirm_needed": true}'

        assert type(confirm_needed_string) == str
        assert confirm_needed_string == expected_string, f"Expected {expected_string}, got: {confirm_needed_string}"

        confirm_needed_decoded = json_decode(confirm_needed_string)
        assert type(confirm_needed_decoded) == ConfirmNeeded, f"Got: {type(confirm_needed_decoded)}. " \
                                                              f"Expected {ConfirmNeeded}"
        assert confirm_needed_decoded == confirm_needed, f"The decoded object: {confirm_needed_decoded} " \
                                                         f"must be equal to the encoded: {confirm_needed}"

    def test_confirm_needed_equals(self):
        co1 = ConfirmNeeded('uuid', True)
        co2 = ConfirmNeeded('uuid',  True)
        co3 = ConfirmNeeded('uuid', False)

        assert co1 == co2
        assert co1 != co3
        assert co1 != "not status"

    def test_confirm_needed_repr(self):
        confirm_needed = ConfirmNeeded('uuid', True)
        expected, got = 'uuid', f'{confirm_needed}'

        assert expected in got, f"Expected {expected} in got: {got}"


class TestConfirmTask(TestCase):

    def test_confirm_task(self):
        confirm_task = ConfirmTask('uuid')
        confirm_task_string = json_encode(confirm_task)
        expected_string = '{"_type": "confirm_task", "task_uuid": "uuid"}'

        assert type(confirm_task_string) == str
        assert confirm_task_string == expected_string, f"Expected {expected_string}, got: {confirm_task_string}"

        confirm_task_decoded = json_decode(confirm_task_string)
        assert type(confirm_task_decoded) == ConfirmTask, f"Got: {type(confirm_task_decoded)}. " \
                                                          f"Expected {ConfirmTask}"
        assert confirm_task_decoded == confirm_task, f"The decoded object: {confirm_task_decoded} " \
                                                     f"must be equal to the encoded: {confirm_task}"

    def test_confirm_task_equals(self):
        co1 = ConfirmTask('uuid')
        co2 = ConfirmTask('uuid')
        co3 = ConfirmTask('uuid2')

        assert co1 == co2
        assert co1 != co3
        assert co1 != "not status"

    def test_confirm_task_repr(self):
        confirm_task = ConfirmTask('uuid')
        expected, got = 'uuid', f'{confirm_task}'

        assert expected in got, f"Expected {expected} in got: {got}"
