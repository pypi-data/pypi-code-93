from enum import unique, Enum


@unique
class DataType(Enum):
	String = 1
	Object = 2
	OneOf = 3
	Array = 4
	Integer =5
	Float = 6
	Boolean = 7


@unique
class VersionMutationType(Enum):
	AddField = 1 # name + def
	RemoveField = 2 # name
	MutateField = 3 # name + new def
	AddRule = 4 # index
	RemoveRule = 5 # rule index
	MutateRule = 6 # rule index + new rule + config
