from django import forms


class SearchForm(forms.Form):
    search = forms.CharField(max_length=150, required=False, label='')
