import logging


def set_logger():
    logger = logging.getLogger('record')
    logger.setLevel('DEBUG')
    formatter = logging.Formatter('%(levelname)s : %(message)s : %(asctime)s')
    file_handler = logging.FileHandler('record.log')
    file_handler.setLevel('DEBUG')
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel('WARNING')
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)



