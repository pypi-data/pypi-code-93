import os

# --- Jupyter Admin ---
from jupytery_admin.hubextension.app import jupytery_admin_TEMPLATE_PATHS
c.JupyterHub.template_paths = jupytery_admin_TEMPLATE_PATHS

from jupytery_admin.hubextension import jupytery_admin_extra_handlers
c.JupyterHub.extra_handlers = jupytery_admin_extra_handlers

# --- Common ---
c.JupyterHub.ip = '0.0.0.0'
c.JupyterHub.port = 8686
c.JupyterHub.cookie_secret = bytes.fromhex(os.environ['DATALAYER_JUPYTERHUB_COOKIE_SECRET'])
c.JupyterHub.confirm_no_ssl = True
c.JupyterHub.log_level = 'DEBUG'
c.JupyterHub.admin_access = True

# --- ConfigurableHTTPProxy ---
c.ConfigurableHTTPProxy.api_url = 'http://0.0.0.0:8687'
c.ConfigurableHTTPProxy.pid_file = '/tmp/jupyterhub-proxy.pid'
c.ConfigurableHTTPProxy.auth_token = os.environ['DATALAYER_JUPYTERHUB_HTTP_PROXY_AUTH_TOKEN']

# --- Users ---
c.Authenticator.allowed_users = {
    os.environ['USER'],
    'datalayer-test',
}
c.Authenticator.admin_users = {
    os.environ['USER'],
}

# --- Authenticator ---
c.JupyterHub.authenticator_class = 'oauthenticator.LocalGitHubOAuthenticator'
c.GitHubOAuthenticator.client_id = os.environ['DATALAYER_GITHUB_CLIENT_ID']
c.GitHubOAuthenticator.client_secret = os.environ['DATALAYER_GITHUB_CLIENT_SECRET']
c.GitHubOAuthenticator.oauth_callback_url =  os.environ['DATALAYER_GITHUB_OAUTH_CALLBACK_URL']
c.LocalAuthenticator.create_system_users = False

# --- Spawner ---
c.JupyterHub.spawner_class = 'jupyterhub.spawner.LocalProcessSpawner'
c.Spawner.debug = True
c.LocalProcessSpawner.debug = True
c.Spawner.cmd = ["jupyter-labhub"]
c.Spawner.default_url = '/lab'
