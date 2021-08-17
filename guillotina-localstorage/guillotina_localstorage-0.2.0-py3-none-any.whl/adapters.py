from guillotina import configure
from guillotina.interfaces import IFileNameGenerator
from guillotina.interfaces import IResource
from guillotina.utils import get_content_path
from guillotina.utils import get_current_container
from guillotina.utils import get_current_request
from guillotina_localstorage.interfaces import IDiskFileField

import uuid


@configure.adapter(for_=(IResource, IDiskFileField), provides=IFileNameGenerator)
class FileNameGenerator:
    def __init__(self, context, field):
        self.context = context
        self.field = field

    def __call__(self):
        request = get_current_request()
        if "X-UPLOAD-FILENAME" in request.headers:
            filename = request.headers["X-UPLOAD-FILENAME"].replace("/", "_")
        else:
            filename = uuid.uuid4().hex
        return "{}{}/{}/{}".format(
            get_current_container().id,
            get_content_path(self.context),
            self.context.__uuid__,
            filename,
        )
