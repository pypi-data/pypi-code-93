from textwrap import dedent

from django import forms
from django.utils.translation import ugettext_lazy as _
from fobi.base import BasePluginForm, get_theme


theme = get_theme(request=None, as_instance=True)


class MailForm(forms.Form, BasePluginForm):
    plugin_data_fields = [
        ("from_name", ""),
        ("from_email", ""),
        ("to_email_choice_field", ""),
        ("to_emails", ""),
        ("subject", ""),
        ("body", ""),
    ]

    from_name = forms.CharField(
        label=_("From name"),
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": theme.form_element_html_class}),
    )
    from_email = forms.EmailField(
        label=_("From email"),
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": theme.form_element_html_class}),
    )
    to_email_choice_field = forms.CharField(
        label=_("To email choice field"),
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": theme.form_element_html_class}),
    )
    to_emails = forms.CharField(
        label=_("To e-mails"),
        help_text=_(
            dedent(
                """The recipients list:<code><br />
            1, recipient1@example.com<br />
            2, recipient2@example.com, recipient3@example.com<br />
            ...<br />
            &lt;id&gt;, &lt;email&gt;[, &lt;email&gt;]
            </code>"""
            )
        ),
        required=True,
        widget=forms.widgets.Textarea(attrs={"class": theme.form_element_html_class}),
    )
    subject = forms.CharField(
        label=_("Subject"),
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": theme.form_element_html_class}),
    )
    body = forms.CharField(
        label=_("Body"),
        required=False,
        widget=forms.widgets.Textarea(attrs={"class": theme.form_element_html_class}),
    )
