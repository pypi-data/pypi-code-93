from typing import Dict, List

from media_platform.lang.serialization import Serializable, Deserializable
from media_platform.service.file_descriptor import FileDescriptor


class SanitationNode(Serializable, Deserializable):
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

    def serialize(self) -> Dict:
        return {
            'name': self.name,
            'value': self.value
        }

    @classmethod
    def deserialize(cls, data: Dict):
        return SanitationNode(data['name'], data['value'])


class SanitationParams(Serializable, Deserializable):
    def __init__(self, sanitized: bool, sanitized_nodes: List[SanitationNode]):
        self.sanitized_nodes = sanitized_nodes
        self.sanitized = sanitized

    def serialize(self) -> Dict:
        return {
            'sanitized': self.sanitized,
            'removedNodes': [node.serialize() for node in self.sanitized_nodes] if self.sanitized_nodes else []
        }

    @classmethod
    def deserialize(cls, data: Dict):
        return SanitationParams(data['sanitized'], [SanitationNode.deserialize(node) for node in data['removedNodes']])


class SanitationResult(Serializable, Deserializable):
    def __init__(self, optimized: bool, sanitation_params: SanitationParams):
        self.sanitation_params = sanitation_params
        self.optimized = optimized

    def serialize(self) -> Dict:
        return {
            'sanitation': self.sanitation_params.serialize(),
            'optimized': self.optimized
        }

    @classmethod
    def deserialize(cls, data: Dict):
        return SanitationResult(data['optimized'], SanitationParams.deserialize(data['sanitation']))


class SanitationResponse(Serializable, Deserializable):
    def __init__(self, file_descriptor: FileDescriptor, sanitation_result: SanitationResult):
        self.file_descriptor = file_descriptor
        self.sanitation_result = sanitation_result

    def serialize(self) -> Dict:
        return {
            'fileDescriptor': self.file_descriptor.serialize(),
            'sanitationResult': self.sanitation_result.serialize()
        }

    @classmethod
    def deserialize(cls, data: Dict):
        file_descriptor = FileDescriptor.deserialize(data['fileDescriptor'])
        sanitation_result = SanitationResult.deserialize(data['sanitationResult'])

        return SanitationResponse(file_descriptor, sanitation_result)
