from enum import Enum
from typing import Union


class AddProcess:

    def __init__(self, process_uuid: str, _type: str = ''):
        self._type = 'add_process'
        self.process_uuid = process_uuid

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AddProcess):
            return other.process_uuid == self.process_uuid
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"<process_uuid={self.process_uuid}>"


class Destination(Enum):
    Human = 'Human'
    Robot = 'Robot'

    @staticmethod
    def from_str(label: str):
        if label in ('Human', 'human'):
            return Destination.Human
        elif label in ('Robot', 'robot'):
            return Destination.Robot
        else:
            raise NotImplementedError


class MoveTask:

    def __init__(self, task_uuid: str, destination: Union[str, Destination], _type: str = ''):
        self._type = 'move_task'
        self.task_uuid = task_uuid
        self.destination = destination if type(destination) == Destination else Destination.from_str(destination)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, MoveTask):
            return other.task_uuid == self.task_uuid and \
                   other.destination == self.destination
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"<task_uuid={self.task_uuid},destination={self.destination}>"


class CompleteTask:

    def __init__(self, task_uuid: str, _type: str = ''):
        self._type = 'complete_task'
        self.task_uuid = task_uuid

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CompleteTask):
            return other.task_uuid == self.task_uuid
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"<task_uuid={self.task_uuid}>"


class ConfirmNeeded:

    def __init__(self, task_uuid: str, confirm_needed: bool, _type: str = ''):
        self._type = 'confirm_needed'
        self.task_uuid = task_uuid
        self.confirm_needed = confirm_needed

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ConfirmNeeded):
            return other.task_uuid == self.task_uuid \
                   and other.confirm_needed == self.confirm_needed
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"<task_uuid={self.task_uuid},confirm_needed={self.confirm_needed}>"


class ConfirmTask:

    def __init__(self, task_uuid: str, _type: str = ''):
        self._type = 'confirm_task'
        self.task_uuid = task_uuid

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ConfirmTask):
            return other.task_uuid == self.task_uuid
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"<task_uuid={self.task_uuid}>"
