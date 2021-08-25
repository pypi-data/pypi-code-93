from .application import JupyterContentApp


def _jupyter_server_extension_paths():
    return [{
        'module': 'jupytery_content.application',
        'app': JupyterContentApp
    }]
