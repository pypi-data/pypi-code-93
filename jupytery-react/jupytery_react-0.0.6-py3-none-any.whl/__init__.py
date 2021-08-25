from .application import JupyterReactApp


def _jupyter_server_extension_paths():
    return [{
        'module': 'jupytery_react.application',
        'app': JupyterReactApp
    }]
