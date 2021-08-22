"""Common data for gitlab scripts
"""
import os

from gitlab import endpoints


def get(var) -> str:
    """Get an environmental variable
    """
    return os.environ[var]

PROJECT_ID = int(get('CI_PROJECT_ID'))
USER_ID = int(get("GITLAB_USER_ID"))
USER_EMAIL = get("GITLAB_USER_EMAIL")
USER_LOGIN = get("GITLAB_USER_LOGIN")
ENDPOINT_URL = get('CI_API_V4_URL')
TOKEN = get('API_AUTH_TOKEN')

ENDPOINT = endpoints.GitLabEndpoint(ENDPOINT_URL, token=TOKEN)
