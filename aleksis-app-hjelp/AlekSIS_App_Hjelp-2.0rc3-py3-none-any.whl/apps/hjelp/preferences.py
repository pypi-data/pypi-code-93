from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from dynamic_preferences.preferences import Section
from dynamic_preferences.types import BooleanPreference, StringPreference

from aleksis.core.registries import site_preferences_registry

hjelp = Section("hjelp")


@site_preferences_registry.register
class PublicFAQ(BooleanPreference):
    section = hjelp
    name = "public_faq"
    default = False
    required = False
    verbose_name = _("Public visibility of FAQ")


@site_preferences_registry.register
class FAQRecipient(StringPreference):
    field_class = forms.EmailField
    section = hjelp
    name = "faq_recipient"
    default = settings.DEFAULT_FROM_EMAIL
    required = False
    verbose_name = _("Recipient e-mail address for FAQ questions")


@site_preferences_registry.register
class IssueReportRecipient(StringPreference):
    field_class = forms.EmailField
    section = hjelp
    name = "issue_report_recipient"
    default = settings.DEFAULT_FROM_EMAIL
    required = False
    verbose_name = _("Recipient e-mail address for issue reports")


@site_preferences_registry.register
class FeedbackRecipient(StringPreference):
    field_class = forms.EmailField
    section = hjelp
    name = "feedback_recipient"
    default = settings.DEFAULT_FROM_EMAIL
    required = False
    verbose_name = _("Recipient e-mail address for feedback")
