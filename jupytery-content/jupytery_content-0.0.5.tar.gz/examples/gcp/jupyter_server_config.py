import os

from hybridcontents import HybridContentsManager
from jupyter_server.services.contents.largefilemanager import LargeFileManager

from jupytery_content.gcp.content import GoogleStorageContentManager


c.ServerApp.contents_manager_class = HybridContentsManager

c.GoogleStorageContentManager.project = 'jupytery-content-78026'
c.GoogleStorageContentManager.keyfile = './gcp-key.json'
c.GoogleStorageContentManager.hide_dotted_blobs = True
# c.GoogleStorageContentManager.default_path = 'path/without/starting/slash'
# c.GoogleStorageContentManager.default_path = '.'

c.HybridContentsManager.manager_classes = {
    "_BUCKETS_": GoogleStorageContentManager,
    "": LargeFileManager,
}

c.HybridContentsManager.manager_kwargs = {
    "shared": {
        "project": "jupytery-content-78026",
        "keyfile": "./gcp-key.json",
    },
    "": {
        "root_dir": os.getenv('HOME'),
    },
}
