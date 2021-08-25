import os

from hybridcontents import HybridContentsManager

from jupytery_content.gcp.content import GoogleStorageContentManager
from jupyter_server.services.contents.largefilemanager import LargeFileManager


c.HybridContentsManager.manager_classes = {
    "_SHARED_": GoogleStorageContentManager,
    "": LargeFileManager,
}

c.HybridContentsManager.manager_kwargs = {
    "shared": {
    },
    "": {
        "root_dir": os.getenv('HOME'),
    },
}

# c.NotebookApp.contents_manager_class = 'jupytery_content.content.GoogleStorageContentManager'
# c.ServerApp.contents_manager_class = 'jupytery_content.content.GoogleStorageContentManager'
c.NotebookApp.contents_manager_class = HybridContentsManager
c.ServerApp.contents_manager_class = HybridContentsManager
