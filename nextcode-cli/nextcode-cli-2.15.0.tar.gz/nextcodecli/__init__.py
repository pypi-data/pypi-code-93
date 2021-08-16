import os
import nextcode


def read_version():
    directory = os.path.dirname(__file__)
    with open(os.path.join(directory, 'VERSION'), 'r') as version_file:
        version = version_file.readline().strip()
        date = version_file.readline().strip()
        return version, date


__version__, version_date = read_version()


def get_version_string():
    format_str = "nextcode-cli/{version} ({version_date}) nextcode-sdk/{sdk_version}"
    version_msg = format_str.format(
        version=__version__, version_date=version_date, sdk_version=nextcode.__version__
    )
    return version_msg
