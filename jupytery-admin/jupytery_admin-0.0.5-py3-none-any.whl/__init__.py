from .application import JupyterAdminApp


def _jupyter_server_extension_paths():
    return [{
        'module': 'jupytery_admin.application',
        'app': JupyterAdminApp
    }]
