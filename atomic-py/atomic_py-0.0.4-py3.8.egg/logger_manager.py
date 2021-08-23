import logging


def get_logger() -> logging.Logger:
  """
    Devuelve el logger de atomic
    :return: Logger
    :rtype: logging.Logger
    """
  return logging.getLogger("atomic")
