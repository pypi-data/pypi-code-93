# -*- coding: utf-8 -*-
# @Time : 2020-06-08 16:17
# @Author : xzr
# @File : static.py
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc :
import mimetypes
import os
import posixpath
import stat

from django.http import (
    FileResponse, Http404, HttpResponseNotModified,
)
from django.utils._os import safe_join
from django.utils.http import http_date
from django.utils.translation import gettext_lazy as _
from django.views.static import directory_index, was_modified_since
import settings
from django.views import static
from .views import notauth
from django.contrib.staticfiles import finders
from django.conf import settings

@notauth
def serve(request, path, insecure=False, **kwargs):
    """
    Serve static files below a given point in the directory structure.

    To use, put a URL pattern such as::

        from django.views.static import serve

        url(r'^(?P<path>.*)$', serve, {'document_root': '/path/to/my/files/'})

    in your URLconf. You must provide the ``document_root`` param. You may
    also set ``show_indexes`` to ``True`` if you'd like to serve a basic index
    of the directory.  This index view will use the template hardcoded below,
    but if you'd like to override it, you can create a template called
    ``static/directory_index.html``.
    """

    normalized_path = posixpath.normpath(path).lstrip('/')
    absolute_path = finders.find(normalized_path) or os.path.join(settings.STATIC_ROOT, normalized_path)
    if not absolute_path:
        if path.endswith('/') or path == '':
            raise Http404("Directory indexes are not allowed here.")
        raise Http404("'%s' could not be found" % path)
    document_root, path = os.path.split(absolute_path)
    return static.serve(request, path, document_root=document_root, **kwargs)

