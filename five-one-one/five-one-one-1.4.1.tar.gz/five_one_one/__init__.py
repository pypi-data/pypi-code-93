"""
    basic utility functions
"""
def is_python_version(*args):
    """
        Checks that the version of python being used is equal or higher than
        {args}.
        Usage options:
            assertPythonVersion("3.9.6")
            assertPythonVersion("3", "9", "6")
            assertPythonVersion(3, 9, 6)

        returns: bool
    """

    import re
    import sys

    m = re.search(r"^(?P<major>\d{1,2})\.(?P<minor>\d{1,2})\.(?P<patch>\d{1,2})", sys.version)
    actual_major = int(m.group("major"))
    actual_minor = int(m.group("minor"))
    actual_patch = int(m.group("patch"))

    if len(args) == 1 and isinstance(args[0], str):
        try:
            desired_major, desired_minor, desired_patch = args[0].split(".")
        except ValueError:
            raise TypeError(
                "Argument is in an unrecognized format. "
                "(should be assertPythonVersion(\"<major>.<minor>.<patch>\")"
            )
    elif len(args) == 3:
        desired_major, desired_minor, desired_patch = args
    else:
        raise TypeError(
            "Arguments are in an unrecognized format. "
            "(should be assertPythonVersion(<major>, <minor>, <patch>)"
        )

    try:
        desired_major = int(desired_major)
        desired_minor = int(desired_minor)
        desired_patch = int(desired_patch)
    except:
        raise TypeError(
            "Arguments are in an unrecognized format. "
            "(should be assertPythonVersion(<major>, <minor>, <patch>) "
            "where <major>, <minor>, <patch> are ints or castable to ints."
        )

    if desired_major < actual_major:
        return True
    elif desired_major == actual_major:
        if desired_minor < actual_minor:
            return True
        elif desired_minor == actual_minor:
            return (desired_patch <= actual_patch)

    return False
