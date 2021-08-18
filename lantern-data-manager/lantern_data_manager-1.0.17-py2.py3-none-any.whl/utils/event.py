from lantern_data_manager.utils.logger import logger
import jwt

def extract_params(event, arguments,optionals=[]):
    """ Extract params from event (local or gateway) """
    data = event
    data = event["body"] if "body" in event and event["body"] else event
    data = event["query"] if "query" in event and event["query"] else data
    total_params = {}
    for name in arguments:
        if name not in data:
            logger.error("{} column is required in event with event: {}".format(name, event))
            raise Exception("{} column is required in event".format(name))
        total_params[name] = data[name]
    for name in optionals:
        if name in data:
            total_params[name] = data[name]
    return total_params


def get_token_attributes(event, names):
    """ decode and extract a list of names from decode jwt token (based on cognito) """
    try:
        authorization_header = event.get("headers", None).get("Authorization", None)
        authorization_header = authorization_header.replace("Bearer","")
        authorization_header = authorization_header.replace("bearer","")
        authorization_header = authorization_header.replace(" ", "")
        logger.info("authorization_header: {}".format(authorization_header))
        decoded = jwt.decode(authorization_header, verify=False)
        logger.info("decoded: {}".format(decoded))
        total_values = {}
        logger.info("names to extract: {}".format(names))
        for name in names:
            total_values[name] = decoded.get(name, None)
        return total_values
    except Exception as e:
        logger.error("Error decoding jwt and extracting values: {}".format(str(e)))