"""
android constants and helper functions
======================================

to include this ae namespace portion into your project add the following import statement into your main module
(main.py) of your application project::

    import ae.droid

this import will ensure that all your permissions will be requested on app startup. on other platforms than Android it
will have no effect.

many thanks to Robert Flatt for his investigations, findings and documentations to code and build Kivy apps for the
Android OS - see https://github.com/RobertFlatt, and to Gabriel Pettier for his service osc example - see
https://github.com/tshirtman.

android service examples and documentation:
    * https://github.com/tshirtman/kivy_service_osc/blob/master/src/main.py
    * https://python-for-android.readthedocs.io/en/latest/services/#arbitrary-scripts-services
    * https://blog.kivy.org/2014/01/building-a-background-application-on-android-with-kivy/

"""
import os

from ae.base import BUILD_CONFIG_FILE, build_config_variable_values, os_platform                # type: ignore


__version__ = '0.2.8'


if os_platform == 'android':
    # noinspection PyUnresolvedReferences
    from android.permissions import request_permissions, Permission     # type: ignore # pylint: disable=import-error
    from jnius import autoclass                                         # type: ignore

    def log(log_level: str, message: str, file_path: str = ""):
        """ print log message. """
        if not file_path:
            file_path = f"ae_droid_{log_level}.log"
        with open(file_path, 'a') as log_file:
            log_file.write(message + "\n")

    PACKAGE_NAME = 'unspecified_package'
    PACKAGE_DOMAIN = 'org.test'
    PERMISSIONS = "INTERNET, VIBRATE, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE"
    if os.path.exists(BUILD_CONFIG_FILE):
        PACKAGE_NAME, PACKAGE_DOMAIN, PERMISSIONS = build_config_variable_values(
            ('package.name', PACKAGE_NAME),
            ('package.domain', PACKAGE_DOMAIN),
            ('android.permissions', PERMISSIONS))
    else:
        log('debug', f"{BUILD_CONFIG_FILE} is not bundled into the APK - using defaults")

    # request app/service permissions
    permissions = list()
    for permission_str in PERMISSIONS.split(','):
        permission = getattr(Permission, permission_str.strip(), None)
        if permission:
            permissions.append(permission)
    request_permissions(permissions)

    def start_service(service_arg: str = ""):
        """ start service.

        :param service_arg:     string value to be assigned to environment variable PYTHON_SERVICE_ARGUMENT on start.
        """
        service_instance = autoclass(f"{PACKAGE_DOMAIN}.{PACKAGE_NAME}.Service{PACKAGE_NAME.capitalize()}")
        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        service_instance.start(activity, service_arg)        # service_arg will be in env var PYTHON_SERVICE_ARGUMENT

        return service_instance
