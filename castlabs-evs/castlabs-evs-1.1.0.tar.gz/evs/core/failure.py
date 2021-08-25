# Copyright 2020, castLabs GmbH

from os import environ

################################################################################

class _ForwardError_(Exception):
  def __init__(self, cls, msg):
    self._forward_class_name_ = cls
    super().__init__(msg)

class _ForwardArgs_(object):
  def __init__(self, fn, *args, **kwargs):
    self._fn_ = fn
    self._args_ = args
    self._kwargs_ = kwargs
  def __call__(self, *args, **kwargs):
    return self._fn_(*self._args_, *args, **self._kwargs_, **kwargs)

def conclude(e):
  j = {
    'errorType': getattr(e, '_forward_class_name_', e.__class__.__name__),
    'errorMessage': str(e),
  }
  if e.__cause__:
    j['errorCause'] = conclude(e.__cause__)
  return j

def gather(j):
  from . import error
  import builtins
  t = j.get('errorType', 'UnknownError')
  c = getattr(error, t, getattr(builtins, t, _ForwardArgs_(_ForwardError_, t)))
  e = c(j.get('errorMessage', j.get('message', 'No message')))
  if 'errorCause' in j:
    e.__cause__ = gather(j['errorCause'])
  return e

################################################################################

def die(e, code=1):
  if 'EVS_TRACE' in environ:
    raise e
  print('{}: {}'.format(getattr(e, '_forward_class_name_', e.__class__.__name__), e))
  e = e.__cause__
  while e:
    n, m = getattr(e, '_forward_class_name_', e.__class__.__name__), str(e)
    if m:
      print(' <- {}: {}'.format(n, m))
    else:
      print(' <- {}'.format(n))
    e = e.__cause__
  raise SystemExit(code)

################################################################################
