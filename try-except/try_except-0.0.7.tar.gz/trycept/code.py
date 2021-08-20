def try_except(t, ex: Exception = Exception, *args):
  try:
    result = t(*args)
    return result
  except Exception as e:
    if isinstance(e,ex):
      return e
    elif ex is None:
      return None
    else:
      return False