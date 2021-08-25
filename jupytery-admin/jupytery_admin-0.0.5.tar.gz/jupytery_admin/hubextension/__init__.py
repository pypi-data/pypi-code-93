import os

from tornado.web import StaticFileHandler

# from jupyterhub.handlers.static import CacheControlStaticFilesHandler

from .main import AdminHandler

from .data_files import DATA_FILES_PATH

jupytery_admin_extra_handlers = [
    (r'jupytery-admin-ui', AdminHandler),    
    (r'jupytery-admin-static/(.*)', StaticFileHandler, dict(path=os.path.join(DATA_FILES_PATH, "static"))),
]
