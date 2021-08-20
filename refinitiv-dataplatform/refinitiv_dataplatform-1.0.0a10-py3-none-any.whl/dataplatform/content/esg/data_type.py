from enum import Enum, unique


@unique
class DataType(Enum):
    BasicOverview = "basic"
    FullMeasures = "measures-full"
    StandardMeasures = "measures-standard"
    FullScores = "scores-full"
    StandardScores = "scores-standard"

    @staticmethod
    def convert_to_str(data_type):
        if isinstance(data_type, DataType):
            return data_type.value
        elif data_type in _DATA_TYPE_VALUES:
            return data_type
        else:
            raise AttributeError(
                f"Data type value - {data_type} - must be in {_DATA_TYPE_VALUES}"
            )


_DATA_TYPE_VALUES = [k.value for k in DataType]
