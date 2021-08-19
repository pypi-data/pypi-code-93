""" Errors related to Diffusion services. """

from diffusion.internal.exceptions import DiffusionError


class ServiceError(DiffusionError):
    """ Error in a service. """


class UnknownServiceError(ServiceError):
    """ Raised when an undefined service was requested. """


class UnknownHandlerError(ServiceError):
    """ Raised when a requested handler key has not been registered in a session. """
