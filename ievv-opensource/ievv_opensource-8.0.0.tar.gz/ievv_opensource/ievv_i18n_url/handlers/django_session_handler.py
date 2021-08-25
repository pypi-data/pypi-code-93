from django.utils import translation

from . import abstract_handler


class DjangoSessionHandler(abstract_handler.AbstractHandler):
    """
    Django session based i18n url handler.

    .. warning::

        Please read the *A warning about session based translations* in the docs before
        deciding to use this handler.
    """

    @classmethod
    def detect_current_languagecode(cls, base_url, request):
        return translation.get_language_from_request(request)

    # @classmethod
    # def strip_languagecode_from_urlpath(cls, base_url, languagecode, path):
    #     return path

    def get_languagecode_from_url(self, url):
        return self.active_languagecode

    def build_absolute_url(self, path, languagecode=None, base_url=None):
        base_url = base_url or self.active_base_url
        return base_url.build_absolute_url(path)

    @classmethod
    def transform_url_to_languagecode(cls, url, languagecode, translate_path=True):
        return url
