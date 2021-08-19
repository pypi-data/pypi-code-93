from enum import Enum
# from proto_formatter.formatter import Formatter


class Position(Enum):
    LEFT = 'left'
    Right = 'right'
    TOP = 'top'
    BELOW = 'below'


class Comment():
    def __init__(self, text: str, position: Position):
        self.text = text
        self.position = position


class Syntax():
    def __init__(self, value, comments: list):
        self.value = value
        self.comments = comments


class Package():
    def __init__(self, value, comments: list):
        self.value = value
        self.comments = comments


class Import():
    def __init__(self, value, comments: list):
        self.value = value
        self.comments = comments


class Option():
    def __init__(self, name, value, comments: list):
        self.name = name
        self.value = value
        self.comments = comments


class MessageElement():
    def __init__(self, type, name, number, label=None, comments=[]):
        self.label = label
        self.type = type
        self.name = name
        self.number = number
        self.comments = comments


class Message():
    def __init__(self, name, elements=[], comments=[]):
        self.name = name
        self.elements = elements
        self.comments = comments


class EnumElement():
    def __init__(self, name, number, comments=[]):
        self.name = name
        self.number = number
        self.comments = comments


class ProtoEnum():
    def __init__(self, name, elements=[], comments=[]):
        self.name = name
        self.elements = elements
        self.comments = comments


#  rpc SeatAvailability (SeatAvailabilityRequest) returns (SeatAvailabilityResponse);
class ServiceElement():
    def __init__(self, label, name, request, response, comments=[]):
        self.label = label
        self.name = name
        self.request = request
        self.response = response
        self.comments = comments


class Service():
    def __init__(self, name, elements=[], comments=[]):
        self.name = name
        self.elements = elements
        self.comments = comments


class ProtoBufStructure():
    def __init__(self):
        self.syntax = None
        self.package = None
        self.options = []
        self.imports = []
        self.objects = []
        # self.formatter = Formatter()

    # def to_string(self):
    #     return self.formatter.to_string(self)
