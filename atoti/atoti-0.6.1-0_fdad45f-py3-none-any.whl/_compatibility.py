from typing import List


def check_python_version(expected: List[int]):
    """Check that the Python version is compatible with atoti.

    Args:
        expected: The expected version of Python.
    """
    import sys

    if sys.version_info < tuple(expected):
        expected_version = ".".join(map(str, expected))
        current_version = ".".join(map(str, sys.version_info[:3]))
        raise Exception(
            f"atoti only supports Python versions >= {expected_version}, "
            f"your version is {current_version}."
        )


check_python_version([3, 7])


def check_java_version(java_path: str, expected: List[int]):
    """Check that the Java version is greater than or equal to the expected one.

    Args:
        java_path: The path to java.
        expected: The expected version of Java.
    """
    import subprocess  # nosec

    # Get the Java version.
    try:
        command_result = subprocess.check_output(  # nosec
            [java_path, "-version"], stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL
        ).decode("utf-8")
    except:
        raise Exception(
            f"Cannot find a Java {expected} installation. Install it or set the JAVA_HOME environment variable."
        ) from None

    # Validate it.
    java_version = _extract_java_version(command_result)
    if java_version < expected:
        expected_version = ".".join(map(str, expected))
        raise Exception(
            f"atoti only supports Java version >= {expected_version}, "
            f"your version is {_get_java_version_string(command_result)}"
        )


def _get_java_version_string(command_result: str) -> str:
    """Extract the Java version string from the result command string.

    Args:
        command_result: The result of the ``java -version`` command.

    Returns:
        the Java version string, for instance ``11.0.2`` or ``1.8.0_212`` or ``14-ea``.
    """
    lines = command_result.splitlines()
    split_lines = [line.split(" ") for line in lines]
    version_line = [
        line for line in split_lines if len(line) > 0 and line[1] == "version"
    ][0]
    version_string = version_line[2].replace('"', "")
    return version_string


def _extract_java_version(command_result: str) -> List[int]:
    """Extract the Java version from the result command string.

    Parse the Java version to an array of integers for instance ``[11, 0 ,2]``.
    String values are replaced by ``-1``.

    Args:
        command_result: The result of the ``java -version`` command.

    Returns:
        the Java version as a list.
    """
    import re

    string_array_version = re.split("\\.|_|-", _get_java_version_string(command_result))

    def convert_element_to_int(element: str) -> int:
        try:
            return int(element)
        except ValueError:
            return -1

    return list(map(convert_element_to_int, string_array_version))
