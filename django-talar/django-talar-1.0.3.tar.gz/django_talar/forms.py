from django import forms
from django.forms import HiddenInput


class PaymentForm(forms.Form):
    key_id = forms.CharField(widget=HiddenInput)
    encrypted = forms.CharField(widget=HiddenInput)

    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['key_id'].initial = data['key_id']
        self.fields['encrypted'].initial = data['encrypted']
