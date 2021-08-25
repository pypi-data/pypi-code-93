from .application import JupyterFederationApp


def _jupyter_server_extension_paths():
    return [{
        'module': 'jupytery_federation.application',
        'app': JupyterFederationApp
    }]
