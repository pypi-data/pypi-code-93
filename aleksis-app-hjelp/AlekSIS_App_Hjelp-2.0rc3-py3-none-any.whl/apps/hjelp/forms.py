from django import forms
from django.utils.translation import gettext_lazy as _

from django_select2.forms import ModelSelect2Widget

from .models import FAQQuestion, FAQSection, IssueCategory


class FAQForm(forms.Form):
    """Form used to allow users to send in a question."""

    question = forms.CharField(widget=forms.Textarea(), label=_("Your question"), required=True)


FAQOrderFormSet = forms.modelformset_factory(
    FAQSection, can_order=True, extra=0, fields="__all__"
)  # noqa
FAQOrderFormSet.ordering_widget = forms.widgets.HiddenInput


class FAQQuestionForm(forms.ModelForm):
    class Meta:
        model = FAQQuestion
        fields = ("question_text", "answer_text", "show", "icon", "section")


class IssueForm(forms.Form):
    """Form used to allow users to report an issue."""

    category_1 = forms.ModelChoiceField(
        label=_("Category 1"),
        required=True,
        queryset=IssueCategory.objects.filter(parent=None),
        widget=ModelSelect2Widget(
            search_fields=["name__icontains"],
            attrs={
                "data-minimum-input-length": 0,
                "class": "browser-default",
                "data-placeholder": _("Select a category"),
            },
        ),
    )
    category_2 = forms.ModelChoiceField(
        label=_("Category 2"),
        required=False,
        queryset=IssueCategory.objects.exclude(parent=None),
        widget=ModelSelect2Widget(
            dependent_fields={"category_1": "parent"},
            search_fields=["name__icontains"],
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
        ),
    )
    category_3 = forms.ModelChoiceField(
        label=_("Category 3"),
        required=False,
        queryset=IssueCategory.objects.exclude(parent=None),
        widget=ModelSelect2Widget(
            dependent_fields={"category_2": "parent"},
            search_fields=["name__icontains"],
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
        ),
    )
    free_text = forms.CharField(
        label=_("Please specify the issue according to the chosen category."), required=False,
    )
    short_description = forms.CharField(
        label=_("Please describe the issue in one sentence."), required=True
    )
    long_description = forms.CharField(
        widget=forms.Textarea, label=_("Please describe the issue in more detail."), required=False,
    )


class FeedbackForm(forms.Form):
    ratings = [(5, 5), (4, 4), (3, 3), (2, 2), (1, 1)]

    design_rating = forms.ChoiceField(
        label=_("Design of the user interface"),
        choices=ratings,
        widget=forms.RadioSelect(),
        required=True,
    )

    performance_rating = forms.ChoiceField(
        label=_("Speed"), choices=ratings, widget=forms.RadioSelect(), required=True,
    )

    usability_rating = forms.ChoiceField(
        label=_("User friendliness"), choices=ratings, widget=forms.RadioSelect(), required=True,
    )

    overall_rating = forms.ChoiceField(
        label=_("AlekSIS in general"), choices=ratings, widget=forms.RadioSelect(), required=True,
    )

    apps = forms.CharField(
        label=_("What do you like? What would you change?"), required=False, widget=forms.Textarea,
    )

    more = forms.CharField(
        label=_("What else do you want to tell us?"), required=False, widget=forms.Textarea,
    )

    ideas = forms.CharField(
        label=_("What do you think should be added to AlekSIS?"),
        required=False,
        widget=forms.Textarea,
    )
