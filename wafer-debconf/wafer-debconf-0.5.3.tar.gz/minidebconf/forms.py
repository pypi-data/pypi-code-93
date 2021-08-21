from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as _p
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Hidden, Submit, Button
from minidebconf.models import Registration


class RegisterForm(forms.ModelForm):
    full_name = forms.CharField(max_length=256, label=_('Full name'))
    class Meta:
        model = Registration
        fields = ['full_name', 'involvement', 'gender', 'country', 'city_state', 'days']
        widgets = {
            'days': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["full_name"].initial = self.instance.full_name
        self.helper = FormHelper()

        if self.instance.id:
            submit = _p("conference", "Update registration")
        else:
            submit = _p("conference", "Register")
        self.helper.add_input(Submit("submit", submit))


    def save(self):
        super().save()
        name = self.cleaned_data['full_name'].split()
        user = self.instance.user
        user.first_name = name[0]
        user.last_name = " ".join(name[1:])
        user.save()
