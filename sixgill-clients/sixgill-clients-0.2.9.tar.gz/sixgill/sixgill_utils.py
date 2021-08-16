import logging


def streamify(batch_func):
    def streamify_wrapper(*args, **kwargs):
        batch = batch_func(*args, **kwargs)
        while batch:
            for indicator in batch:
                yield indicator
            batch = batch_func(*args, **kwargs)

    return streamify_wrapper


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s %(levelname)s: %(message)s [in %(filename)s:%(lineno)d]")
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.DEBUG)
    return logger


def is_darkfeed_indicator(indicator):
    return "indicator" == indicator.get("type", "")


def is_cvefeed_indicator(indicator):
    return "x-cybersixgill-com-cve-event" == indicator.get("type", "")


def is_indicator(indicator):
    return is_darkfeed_indicator(indicator) or is_cvefeed_indicator(indicator)
