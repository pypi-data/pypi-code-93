import re

from django import forms
from django.core.exceptions import ValidationError

from .models import Plan, Subscription


class SubscribeForm(forms.Form):
    stripe_token = forms.CharField(max_length=255)
    plan = forms.ModelChoiceField(queryset=Plan.objects.list_published())
    quiz = forms.CharField(max_length=500)

    def clean_stripe_token(self):
        data = self.cleaned_data['stripe_token']

        if not re.match(r'^(tok|pm)_[0-9a-zA-Z]+$', data):
            raise ValidationError('Token format validation failed')

        return data


class CancelSubscriptionForm(forms.Form):
    subscription_id = forms.CharField(max_length=255)

    def clean_subscription_id(self):
        data = self.cleaned_data['subscription_id']

        if not re.match(r'^sub_[0-9a-zA-Z]+$', data):
            raise ValidationError('Token format validation failed')

        return data
