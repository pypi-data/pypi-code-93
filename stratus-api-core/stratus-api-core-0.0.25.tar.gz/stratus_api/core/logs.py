LOGGER = None


def get_logger():
    import logging, sys
    import os
    import json
    import logging.config
    global LOGGER
    if LOGGER is None:
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        if os.getenv('LOGGING_CONFIG_PATH'):
            with open(os.getenv('LOGGER_CONFIG_PATH'), 'rt', encoding='utf-8') as f:
                config = json.load(f)
            logging.config.dictConfig(config=config)
        else:
            logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        LOGGER = logging.getLogger()
    return LOGGER


def log_event(level, start, end, status, process_type, payload, attributes=None, failure_classification=None,
              logger=None):
    import json
    from stratus_api.core.requests import get_request_context
    assert isinstance(payload, dict)
    assert isinstance(attributes, dict) or attributes is None
    assert status in {'success', 'anomalous', 'failure', 're-queued'}
    level_mapping = dict(
        critical=50,
        error=40,
        warning=30,
        info=20,
        debug=10
    )
    log_message = {
        "process_start_utc": start.timestamp(),
        "process_end_utc": end.timestamp(),
        "process_type": process_type,
        "status": status,
        "attributes": attributes if attributes is not None else {},
        "payload": payload
    }
    context = get_request_context()
    if context is not None and context.get('user'):
        log_message['user_id'] = context['user']
    if failure_classification:
        log_message["failure_classification"]= failure_classification
    get_logger().log(level=level_mapping[level.lower()], msg=json.dumps(log_message))
    return log_message
