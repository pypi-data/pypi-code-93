import logging

# Enable logging
logging.basicConfig(
    filename='qnaut.log'
    , filemode='a'
    , format='%(asctime)s, %(levelname)s, %(message)s'
    , datefmt='%A | %Y-%m-%d %H:%M:%S | %z'
    , level=logging.INFO
)

logger = logging.getLogger(__name__)

def log(level, message):
    '''ghi lai cac hoat dong cua thu vien va nguoi dung
    '''
    if level.lower() in ['debug']:
        logger.debug(message)
    elif level.lower() in ['info']:
        logger.info(message)
    elif level.lower() in ['warning']:
        logger.warning(message)
    elif level.lower() in ['error']:
        logger.error(message)
    elif level.lower() in ['critical']:
        logger.critical(message)
