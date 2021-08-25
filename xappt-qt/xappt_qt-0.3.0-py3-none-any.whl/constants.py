import xappt

from xappt_qt.utilities import safe_file_name


__all__ = [
    'APP_INTERFACE_NAME',
    'APP_PACKAGE_NAME',
    'APP_TITLE',
    'APP_PROPERTY_RUNNING',
    'APP_PROPERTY_LAUNCHER',
    'APP_CONFIG_PATH',
]


APP_INTERFACE_NAME = "qt"
APP_TITLE = "Xappt QT"
APP_PACKAGE_NAME = safe_file_name(APP_TITLE)
APP_PROPERTY_RUNNING = "running"
APP_PROPERTY_LAUNCHER = "launcher"
APP_CONFIG_PATH = xappt.user_data_path().joinpath(APP_PACKAGE_NAME)
