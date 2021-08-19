"""
Set of environments that change the global state of the CLI.

Variables
---------

    * `ENVIRONMENT`: Describes which environment the application is
    running in. This can be either `production` or `development`.
    This variable determines a number of behavior changes in the app,
    including logging, tracking, and error handling.

    * `GRID_URL`: Address used to register with GitHub as an Oauth
    provider. This must match what is registered in GitHub.

    * `DEBUG`: If gridrunner should print additional information for
    debugging purposes.

    * `SHOW_PROCESS_STATUS_DETAILS`: Global flag used to print Run submit details.

    * `SEGMENT_KEY`: Key to send data analytics to Segment.

    * `GRID_DISABLE_TRACKING`: If tracking should be disabled

    * `IGNORE_WARNINGS`: if we should ignore warning prompts throughout the CLI.

    * `GRID_SKIP_VERSION_CHECK`: skips version check between client and backend.

"""
import logging
import os

from grid.cli.utilities import get_graphql_url

ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

DEFAULT_GRID_URL = 'https://platform.grid.ai/graphql'
GRID_URL = get_graphql_url(os.getenv('GRID_URL', DEFAULT_GRID_URL))

USER_ID = os.getenv('GRID_USER_ID')
API_KEY = os.getenv('GRID_API_KEY')
SEGMENT_KEY = os.getenv('SEGMENT_KEY', "VqTtJqOy7yCzJFhoyfNAT5IJusE8zVQR")
GRID_DISABLE_TRACKING = os.getenv('GRID_DISABLE_TRACKING')

DEBUG = bool(os.getenv('DEBUG'))

logger = logging.getLogger(__name__)  # pragma: no cover

SHOW_PROCESS_STATUS_DETAILS = False

IGNORE_WARNINGS = None

SKIP_VERSION_CHECK = bool(os.getenv('GRID_SKIP_VERSION_CHECK'))

GRID_SSH_CONFIG = os.getenv("GRID_SSH_CONFIG", default=os.path.join(os.path.expanduser("~"), ".ssh", "config"))
