import datetime
from typing import Any, Collection, Mapping, Union, cast

from py4j.java_collections import JavaArray, JavaMap, ListConverter
from py4j.java_gateway import JavaClass, JavaGateway, JavaObject


# No type stubs for py4j, so we ignore this error
def to_java_object_array(
    seq: Collection[Any],
    *,
    gateway: JavaGateway,  # type: ignore
) -> JavaArray:
    """Transform the Python collection into a Java array of strings.

    Args:
        gateway: the Java Gateway.
        seq: The collection to convert.

    """
    return to_typed_java_array(seq, gateway=gateway, array_type=gateway.jvm.Object)


def to_java_map(
    dictionary: Mapping[Any, Any],
    *,
    gateway: JavaGateway,  # type: ignore
) -> JavaMap:
    """Convert a Python dict to a JavaMap."""
    return _to_typed_java_map(dictionary, gateway=gateway, clazz="java.util.HashMap")


def _to_typed_java_map(
    to_convert: Mapping[Any, Any],
    *,
    gateway: JavaGateway,  # type: ignore
    clazz: str,
) -> JavaMap:
    """Convert to a map of the given type."""
    map_type = JavaClass(clazz, gateway._gateway_client)
    java_map = cast(JavaMap, map_type())
    for key in to_convert.keys():
        java_map[key] = as_java_object(to_convert[key], gateway=gateway)
    return java_map


def to_java_string_array(
    seq: Collection[str],
    *,
    gateway: JavaGateway,  # type: ignore
) -> JavaArray:
    """Transform the Python collection into a Java array of strings."""
    return to_typed_java_array(seq, gateway=gateway, array_type=gateway.jvm.String)


def to_java_object_list(
    seq: Collection[Any],
    *,
    gateway: JavaGateway,  # type: ignore
) -> Any:
    """Transform the Python collection into a Java list of object."""
    return ListConverter().convert(
        [as_java_object(e, gateway=gateway) for e in seq], gateway._gateway_client
    )


def to_typed_java_array(
    seq: Collection[Any],
    *,
    gateway: JavaGateway,  # type: ignore
    array_type: Any,
) -> JavaArray:
    """Transform to Java array of given type."""
    array = cast(JavaArray, gateway.new_array(array_type, len(seq)))
    if seq:
        for index, elem in enumerate(seq):
            array[index] = as_java_object(elem, gateway=gateway)
    return array


def to_java_date(
    date: Union[datetime.date, datetime.datetime],
    *,
    gateway: JavaGateway,  # type: ignore
) -> JavaObject:
    """Transform the Python date into a Java one."""
    if isinstance(date, datetime.datetime):
        if not date.tzinfo:
            return gateway.jvm.java.time.LocalDateTime.of(  # type: ignore
                date.year,
                date.month,
                date.day,
                date.hour,
                date.minute,
                date.second,
                date.microsecond * 1000,
            )
        raise NotImplementedError()
    if isinstance(date, datetime.date):
        # LocalDate of(int year, int month, int dayOfMonth)
        return gateway.jvm.java.time.LocalDate.of(date.year, date.month, date.day)  # type: ignore
    raise ValueError(f"Expected a date but got {date}")


def as_java_object(
    arg: Any,
    *,
    gateway: JavaGateway,  # type: ignore
) -> Any:
    """Try to convert the arg to a java argument.

    Args:
        gateway: the Java gateway
        arg: the argument to convert.

    """
    if isinstance(arg, (datetime.date, datetime.datetime)):
        return to_java_date(arg, gateway=gateway)
    if isinstance(arg, list):
        # Convert to Vector
        vector_package = gateway.jvm.com.qfs.vector.array.impl  # type: ignore
        if all(isinstance(x, float) for x in arg):
            array = to_typed_java_array(
                arg, gateway=gateway, array_type=gateway.jvm.double
            )
            return vector_package.ArrayDoubleVector(array)  # type: ignore
        if all(isinstance(x, int) for x in arg):
            array = to_typed_java_array(
                arg, gateway=gateway, array_type=gateway.jvm.long
            )
            return vector_package.ArrayLongVector(array)  # type: ignore
        array = to_java_object_array(arg, gateway=gateway)
        return vector_package.ArrayObjectVector(array)  # type: ignore
    return arg


def to_python_dict(
    java_map: JavaMap,  # type: ignore
) -> dict:
    """Convert a Java map to a python dict.

    Args:
        java_map: the java map to convert

    Returns:
        The Python dict equivalent of the map
    """
    return {key: java_map[key] for key in java_map.keySet().toArray()}  # type: ignore


def to_python_list(
    list_to_convert: JavaObject,  # type: ignore
) -> list:
    """Convert a Java list to a python list.

    Args:
        list_to_convert: the java list to convert

    Returns:
        The Python list equivalent of the Java list

    """
    # ignore types when calling a Java function
    return list(list_to_convert.toArray())  # type: ignore
