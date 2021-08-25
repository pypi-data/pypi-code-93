from typing import NewType

AppStatus = NewType('AppStatus', object)

APP_ERROR = AppStatus(object())
APP_SUCCESS = AppStatus(object())
