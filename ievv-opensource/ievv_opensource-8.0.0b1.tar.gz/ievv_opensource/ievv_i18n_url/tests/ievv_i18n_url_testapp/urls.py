from django.urls import path
from django.utils.translation import gettext_lazy

from . import views

urlpatterns = [
    path('my/unnamed/untranslated_example',
         views.unnamed_untranslated_exampleview),
    path(gettext_lazy('my/unnamed/translated_example'),
         views.unnamed_translated_exampleview),
    path('my/named/untranslated_example',
         views.named_untranslated_exampleview,
         name="ievv_i18n_url_testapp_untranslated_exampleview"),
    path(gettext_lazy('my/named/translated_example'),
         views.named_translated_exampleview,
         name="ievv_i18n_url_testapp_translated_exampleview"),
]
