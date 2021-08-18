
class TraccarControllerException(Exception):

    def __init__(self, info):
        """
        Args:
            info: Message to append to the error
        """
        self.info = info

    def __str__(self):
        return 'TraccarController error: {}'.format(self.info)


class BadRequestException(TraccarControllerException):
    def __init__(self, message):
        """
        Args:
            message:
        """
        super().__init__(info=message)


class ObjectNotFoundException(TraccarControllerException):

    def __init__(self, obj):
        """
        Args:
            obj:
            obj_type:
        """
        message = '[{} not found]'.format(obj)
        super().__init__(info=message)


class ForbiddenAccessException(TraccarControllerException):

    def __init__(self):
        message = '[Access is denied]: Wrong username or password'
        super().__init__(info=message)


class UserPermissionException(TraccarControllerException):

    def __init__(self):
        message = '[User has not enough permissions]'
        super().__init__(info=message)


class InvalidTokenException(TraccarControllerException):

    def __init__(self):
        message = '[Invalid user token]'
        super().__init__(info=message)

class BadParamsException(TraccarControllerException):
    
    def __init__(self,message):
        super().__init__(info=message)

class DuplicateEntryException(TraccarControllerException):
    def __init__(self,value):
        message = "Device already exist for uniqueId: {}".format(value)
        super().__init__(info=message)