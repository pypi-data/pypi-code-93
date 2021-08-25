from django.http import HttpResponseRedirect
from django.views import View

from ievv_opensource.ievv_i18n_url import i18n_url_utils


class RedirectToLanguagecodeView(View):
    def dispatch(self, request, languagecode, path):
        handler = i18n_url_utils.get_handler()
        return HttpResponseRedirect(handler.build_absolute_url(f'/{path}', languagecode=languagecode))
