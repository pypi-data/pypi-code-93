from divinegift import main
from divinegift import sender

import os
import logging
from logging.handlers import TimedRotatingFileHandler
import traceback

from typing import List, Dict, Optional


logger: Optional[logging.Logger] = None
log_dir_g = None
log_name_g = None


def log_debug(*args, separator: str = ' '):
    """
    Logging a debug message
    :param msg: Message which would be logged
    :return: None
    """
    if logger:
        logger.debug(separator.join([str(x) for x in args]))
    else:
        logging.debug(separator.join([str(x) for x in args]))


def log_info(*args, separator: str = ' '):
    """
    Logging a info
    :param separator: Separator
    :param msg: Message which would be logged
    :return: None
    """
    if logger:
        logger.info(separator.join([str(x) for x in args]))
    else:
        logging.info(separator.join([str(x) for x in args]))


def log_warning(*args, separator: str = ' '):
    """
    Logging a warning
    :param separator: Separator
    :param msg: Message which would be logged
    :type msg: string
    :return: None
    """
    if logger:
        logger.warning(separator.join([str(x) for x in args]))
    else:
        logging.warning(separator.join([str(x) for x in args]))


def log_err(*args, separator: str = ' ', src: str = None, mode: List = None, channel: Dict = None):
    """
    Logging an error with monitoring if parameters were filled
    :param separator: Separator
    :param msg: Error message which will logged
    :param src: Source which raised error
    :type src: string
    :param mode: List of monitoring's mode (telegram, email, email_attach, slack)
    :type mode: list
    :param channel: Dict with parameters of monitoring (e.g. {'telegram': -1001343660695}
    :type channel: dict
    :return: None
    """
    if logger:
        logger.exception(separator.join([str(x) for x in args]))
    else:
        logging.exception(separator.join([str(x) for x in args]))
    error_txt = f'An error has occurred in {src}\nError text: {separator.join([str(x) for x in args])}\n{traceback.format_exc()}'

    if mode:
        #if 'vk' in mode:
        #   send_vk(error_txt, vk_chat[channel.get('vk')], channel.get('vk', 'private'))
        if 'telegram' in mode:
            sender.send_telegram(error_txt, chat_id=channel.get('telegram', -1001343660695))
        if 'slack' in mode:
            sender.send_slack(error_txt)
        if 'email' in mode:
            sender.send_email(error_txt, f'{src} ERROR', **channel.get('email'))
        if 'email_attach' in mode:
            if log_dir_g and log_name_g:
                log = main.get_list_files(log_dir_g, log_name_g, add_path=True)
            else:
                log = []
            sender.send_email(error_txt, f'{src} ERROR', attachments=log, **channel.get('email_attach'))


def log_crit(*args, separator: str = ' '):
    logging.critical(separator.join([str(x) for x in args]))


def set_loglevel(log_level: str, log_name: str = None, log_dir: str = './logs/', when: str = 'midnight', interval: int = 1, backupCount: int = 7):
    """
    This set up log_level and name of logfile
    :param log_level: String with log_level (e.g. 'INFO')
    :param log_name: Name of file with logs
    :param log_dir: Directory which should keep logs
    :param when: When rotate log
    :param interval: How often
    :param backupCount: How many version need to keep
    :return: None
    """
    global logger
    global log_name_g
    global log_dir_g

    logger = logging.getLogger('Rotating log')
    # Remove all existing handlers
    [logger.removeHandler(handler) for handler in logger.handlers[:]]
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % log_level)
    logger.setLevel(numeric_level)
    formatter = logging.Formatter('%(levelname)-8s [%(asctime)s] %(message)s')
    if log_name:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        handler = TimedRotatingFileHandler(os.path.join(log_dir, log_name), when=when, interval=interval, backupCount=backupCount, encoding='utf-8')
        log_name_g = log_name
        log_dir_g = log_dir
    else:
        handler = logging.StreamHandler()

    handler.setFormatter(formatter)
    logger.addHandler(handler)


if __name__ == '__main__':
    pass
