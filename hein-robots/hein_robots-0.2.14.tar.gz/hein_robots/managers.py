from typing import List, Tuple, Dict, Optional, Union, Any
import json
from hein_robots.base.robot_arms import RobotArm
from hein_robots.grids import LocationGroup
from hein_robots.robotics import Location


class ManagerError(Exception):
    pass


class LocationManagerError(ManagerError):
    pass


class LocationManagerEmptyError(LocationManagerError):
    pass


class LocationManager:
    """
    The LocationManager class is a simple class that is meant to be subclassed for working with specific location groups.
    LocationManager classes will keep track of the "current" index in a list of grids, and allow the user to increment the
    "current" index to the next location. It will also raise a LocationManagerEmptyError once it has run out of indexes.
    """
    def __init__(self, robot: RobotArm, groups: List[LocationGroup], state_file: Optional[str]=None):
        """
        :param robot: an instance of RobotArm
        :param groups: a list of LocationGroup instances
        """
        self.robot = robot
        self.groups = groups
        self.current_indexes_index = 0
        self.indexes: List[Tuple[LocationGroup, str]] = []
        self.state_file = state_file

        self.indexes = self.build_indexes()
        self.load_state()

    @property
    def remaining(self) -> int:
        """ Get the number of remaining indexes """
        return len(self.indexes) - self.current_indexes_index

    @property
    def empty(self) -> bool:
        """ Return True if there are no remaining indexes """
        return self.current_indexes_index >= len(self.indexes)

    @property
    def current_location(self) -> Location:
        """ Get the location at the current index """
        group, index = self.indexes[self.current_indexes_index]
        return group.locations[index]

    @property
    def current_group(self) -> LocationGroup:
        """ Get the current LocationGroup instance """
        group, index = self.indexes[self.current_indexes_index]
        return group

    @property
    def current_index(self) -> str:
        """ Get the current index key """
        group, index = self.indexes[self.current_indexes_index]
        return index

    @property
    def state(self) -> Dict[str, Any]:
        """ Get or set a dictionary with the current state of the LocationManager """
        return {
            'current_indexes_index': self.current_indexes_index
        }

    def reset(self):
        """ Reset the current index to the start """
        self.current_indexes_index = 0
        self.save_state()

    def build_indexes(self):
        indexes = []

        for group in self.groups:
            indexes += [(group, index) for index in group.indexes()]

        return indexes

    def increment_location(self):
        """ Incrememnt the current index, raises a LocationManagerEmptyError if empty """
        if self.remaining <= 0:
            raise LocationManagerEmptyError(f'Location groups empty')

        self.current_indexes_index += 1
        self.save_state()

    def save_state(self):
        if self.state_file is None:
            return

        with open(self.state_file, 'w') as state_file:
            json.dump(self.state, state_file)

    def load_state(self):
        if self.state_file is None:
            return

        try:
            with open(self.state_file, 'r') as state_file:
                state = json.load(state_file)

                for key, val in state.items():
                    setattr(self, key, val)
        except FileNotFoundError:
            pass
