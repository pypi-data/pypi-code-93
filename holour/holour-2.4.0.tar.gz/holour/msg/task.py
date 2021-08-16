from typing import List
from holour.msg import Pose


class Task:

    def __init__(self, uuid: str, name: str, product_uuid: str, pose: Pose, automated: bool = False,
                 conditions: List[str] = None, conditions_fulfilled: bool = True, description: str = "",
                 _type: str = ''):
        conditions = conditions if conditions else []
        assert type(uuid) == str
        assert type(name) == str
        assert type(product_uuid) == str
        assert type(pose) == Pose
        assert type(automated) == bool
        assert type(conditions) == list, f"Type of conditions: {type(conditions)}"
        assert type(conditions_fulfilled) == bool
        assert type(description) == str

        self._type = 'task'
        self.uuid = uuid
        self.name = name
        self.product_uuid = product_uuid
        self.pose = pose
        self.automated = automated
        self.conditions = conditions
        self.conditions_fulfilled = conditions_fulfilled
        self.description = description

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Task):
            return other.uuid == self.uuid \
                   and other.product_uuid == self.product_uuid \
                   and other.pose == self.pose \
                   and other.automated == self.automated \
                   and other.conditions == self.conditions \
                   and other.conditions_fulfilled == self.conditions_fulfilled \
                   and other.description == self.description
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"<uuid={self.uuid},name={self.name},product_uuid={self.product_uuid},pose={self.pose}," \
               f"automated={self.automated},conditions={self.conditions}," \
               f"conditions_fulfilled={self.conditions_fulfilled},description={self.description}>"
