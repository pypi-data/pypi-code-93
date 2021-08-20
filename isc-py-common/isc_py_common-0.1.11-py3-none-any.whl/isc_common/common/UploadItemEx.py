import os
import uuid
from pathlib import Path

import magic
from isc_common.common.UploadItem import UploadItem

class UploadItemEx(UploadItem):

    def get_path(self, name):
        return os.path.dirname(os.path.abspath(name)).replace(os.sep, os.altsep) if os.altsep else os.path.dirname(os.path.abspath(name))

    def __init__(self, logger=None, **kwargs):
        super().__init__(logger=logger, dictionary=kwargs)

        if self.real_file_name is not None and self.file_mime_type is None:
            mime = magic.Magic(mime=True)
            if os.path.exists(self.real_file_name):
                self.file_mime_type = mime.from_file(self.real_file_name)
                stat = Path(self.real_file_name).stat()
            else:
                self.file_mime_type = mime.from_file(self.tmp_file_name)
                stat = Path(self.tmp_file_name).stat()


        if self.file_size is None:
            self.file_size = stat.st_size

        if self.stored_file_name is None:
            self.stored_file_name = str(uuid.uuid4()).upper()
