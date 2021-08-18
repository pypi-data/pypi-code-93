import os
from lantern_data_manager.utils.logger import logger

def get_server_credentials(server_id="1"):
    """ Return Traccar Server URL, User, Pass
    based on server_id received in parameters, this should be a valid server. 
    Conditions:
        1. If server_id is None, we will return Main server creadentials which will exist always. (server with id=1)
        2. If server_id is defined, we will find a exact match with configuration, if no config is found a exception will be triggered.
        3. If server_id matches with configuration we will return that configuration.
        -- We will validate ALL 3 configuration variables are defined and have a valid value. 

    Args:
        server_id ([type]): [description]
    """
    logger.debug("get_server_credentials with server_id: {}".format(server_id))
    base_url_env_name = "TRACCAR_API_URL_{server_id}"
    base_user_env_name = "TRACCAR_API_HTTP_USER_{server_id}"
    base_pass_env_name = "TRACCAR_API_HTTP_PASS_{server_id}"

    if server_id is None:
        raise Exception("server_id is None")


    # getting full env variable names
    _url_env = base_url_env_name.format(server_id=server_id)
    _user_env = base_user_env_name.format(server_id=server_id)
    _pass_env = base_pass_env_name.format(server_id=server_id)
    
    # validating all those variables are defined in env
    _url_env_val = os.environ.get(_url_env, None)
    _user_env_val = os.environ.get(_user_env, None)
    _pass_env_val = os.environ.get(_pass_env, None)
    if not _url_env_val or not _user_env_val or not _pass_env_val:
        raise Exception("Configuration ERROR: At least one required ENV is not defined for selected Traccar instance. \
            Please check this variables in serverless: {}, {}, {}".format(_url_env, _user_env, _pass_env))
    
    return _url_env_val, _user_env_val, _pass_env_val