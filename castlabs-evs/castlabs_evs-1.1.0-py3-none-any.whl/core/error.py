# Copyright 2020, castLabs GmbH

################################################################################

class UnsupportedError(NotImplementedError):
  pass

class ForbiddenError(PermissionError):
  pass

class InvalidParamError(RuntimeError):
  pass

class InvalidDataError(RuntimeError):
  pass

class ValidityError(RuntimeError):
  pass

################################################################################

class RequestError(RuntimeError):
  pass

class HTTPError(RuntimeError):
  pass

################################################################################

class NonInteractiveError(RuntimeError):
  pass

################################################################################
