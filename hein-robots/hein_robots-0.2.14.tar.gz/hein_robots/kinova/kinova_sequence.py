from typing import Dict, List, Optional, Tuple
import json
from hein_robots.robotics import Location
from hein_robots.grids import LocationGroup


class KinovaSequence(LocationGroup):
    @staticmethod
    def parse_sequence_file(sequence_file_path: str) -> Tuple[Dict[str, Location], Dict[str, List[float]]]:
        with open(sequence_file_path) as sequence_file:
            locations = {}
            joint_positions = {}
            data = json.load(sequence_file)
            tasks = data['sequences']['sequence'][0]['tasks']

            for task in tasks:
                if 'reachPose' in task['action']:
                    pose = task['action']['reachPose']['targetPose']
                    location = Location(pose['x'], pose['y'], pose['z'], pose['thetaX'], pose['thetaY'], pose['thetaZ'])
                    locations[task['action']['name']] = location.convert_m_to_mm()

                if 'reachJointAngles' in task['action']:
                    joints_info = task['action']['reachJointAngles']['jointAngles']['jointAngles']
                    joints = [0] * len(joints_info)

                    for joint_info in joints_info:
                        joints[joint_info['jointIdentifier']] = joint_info['value']

                    joint_positions[task['action']['name']] = joints

            return locations, joint_positions

    def __init__(self, sequence_json_file: str, location_names: Optional[List[str]] = None):
        self.locations, self.joints = self.parse_sequence_file(sequence_json_file)

        if location_names is not None:
            for name in location_names:
                if name not in self.locations:
                    raise KinovaSequenceError(f'Location "{name}" not found in Kinova sequence file: {sequence_json_file}')

    def __len__(self):
        return len(self.locations)

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.locations[item]

        return [self.locations[item] for item in item]

    def indexes(self) -> List[str]:
        return list(self.locations.keys())


class KinovaSequenceError(Exception):
    pass
