from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin as GlobalPermissionRequiredMixin
from django.forms.forms import BaseForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.generic import FormView

from material import Layout, Row
from rules.contrib.views import permission_required
from templated_email import send_templated_mail

from aleksis.core.mixins import AdvancedCreateView, AdvancedDeleteView, AdvancedEditView
from aleksis.core.models import Activity
from aleksis.core.util.core_helpers import get_site_preferences

from .forms import FAQForm, FAQOrderFormSet, FAQQuestionForm, FeedbackForm, IssueForm
from .models import FAQQuestion, FAQSection, IssueCategory


@permission_required("hjelp.view_faq_rule")
def faq(request):
    """Show the FAQ page."""
    context = {
        "sections": FAQSection.objects.filter(show=True),
    }
    return render(request, "hjelp/faq.html", context)


class OrderFAQ(GlobalPermissionRequiredMixin, FormView):
    queryset = FAQSection.objects.all()
    template_name = "hjelp/order_faq.html"
    form_class = FAQOrderFormSet
    success_url = "#"
    permission_required = "hjelp.change_faq_rule"
    success_message = _("The FAQ was updated successfully.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["layout"] = Layout("name", "icon", "show")

        return context

    def form_valid(self, form):
        for individual_form in form.forms:
            pos = individual_form.cleaned_data["ORDER"]
            individual_form.cleaned_data["position"] = pos
            individual_form.instance.position = pos
            individual_form.instance.save()

        questions_and_sections = zip(
            self.request.POST.getlist("question-ids[]"),
            self.request.POST.getlist("question-sections[]"),
        )

        for question, section in questions_and_sections:
            q = FAQQuestion.objects.get(pk=question)
            q.section = FAQSection.objects.get(pk=section)
            q.save()

        messages.success(self.request, self.success_message)

        return super().form_valid(form)


class CreateFAQSection(GlobalPermissionRequiredMixin, AdvancedCreateView):
    model = FAQSection
    template_name = "hjelp/hjelp_crud_views.html"
    success_message = _("The FAQ section was created successfully!")
    fields = ("name", "icon", "show")
    permission_required = "hjelp.change_faq_rule"

    def form_valid(self, form: BaseForm) -> HttpResponse:
        super().form_valid(form)
        messages.success(self.request, self.success_message)
        return redirect("order_faq")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = _("Create FAQ section")
        context["layout"] = Layout(Row("name"), Row("icon"), Row("show"))
        return context


class DeleteFAQSection(GlobalPermissionRequiredMixin, AdvancedDeleteView):
    model = FAQSection
    template_name = "core/pages/delete.html"
    success_message = _("The FAQ section was deleted successfully.")
    success_url = reverse_lazy("order_faq")
    permission_required = "hjelp.change_faq_rule"


class CreateFAQQuestion(GlobalPermissionRequiredMixin, AdvancedCreateView):
    form_class = FAQQuestionForm
    template_name = "hjelp/hjelp_crud_views.html"
    success_message = _("The FAQ question was created successfully.")
    permission_required = "hjelp.change_faq_rule"

    def form_valid(self, form: BaseForm) -> HttpResponse:
        super().form_valid(form)
        messages.success(self.request, self.success_message)
        return redirect("order_faq")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = _("Create FAQ question")
        context["layout"] = Layout(
            Row("question_text"), Row("icon", "section"), Row("show"), Row("answer_text")
        )
        return context


class UpdateFAQQuestion(GlobalPermissionRequiredMixin, AdvancedEditView):
    model = FAQQuestion
    form_class = FAQQuestionForm
    template_name = "hjelp/hjelp_crud_views.html"
    success_message = _("The FAQ question was edited successfully.")
    success_url = reverse_lazy("order_faq")
    permission_required = "hjelp.change_faq_rule"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = _("Edit FAQ question")
        context["layout"] = Layout(
            Row("question_text"), Row("icon", "show", "section"), Row("answer_text")
        )
        return context


class DeleteFAQQuestion(GlobalPermissionRequiredMixin, AdvancedDeleteView):
    model = FAQQuestion
    template_name = "core/pages/delete.html"
    success_message = _("The FAQ question was deleted successfully.")
    success_url = reverse_lazy("order_faq")
    permission_required = "hjelp.change_faq_rule"


@never_cache
@permission_required("hjelp.ask_faq_rule")
def ask_faq(request):
    if request.method == "POST":
        form = FAQForm(request.POST)
        if form.is_valid():
            # Read out form data
            question = form.cleaned_data["question"]

            act = Activity(
                title=_("You have submitted a question."),
                description=question,
                app="Hjelp",
                user=request.user.person,
            )
            act.save()

            context = {
                "question": question,
                "user": request.user,
            }

            send_templated_mail(
                template_name="faq",
                from_email=request.user.person.mail_sender_via,
                headers={
                    "Reply-To": request.user.person.mail_sender,
                    "Sender": request.user.person.mail_sender,
                },
                recipient_list=[get_site_preferences()["hjelp__faq_recipient"]],
                context=context,
            )

            return render(request, "hjelp/question_submitted.html")
    else:
        form = FAQForm()

    return render(request, "hjelp/ask.html", {"form": form})


def add_arrows(array: list):
    return " → ".join([item for item in array if item != "" and item.lower() != "none"])


@never_cache
def issues_get_next_properties(request):
    _id = request.GET.get("id", None)
    issue_category = get_object_or_404(IssueCategory, id=_id)
    next_properties = {
        "icon": issue_category.icon,
        "free_text": issue_category.free_text,
        "placeholder": issue_category.placeholder,
        "has_children": issue_category.children.exists(),
    }
    return JsonResponse(next_properties)


@never_cache
@permission_required("hjelp.report_issue_rule")
def report_issue(request):
    if request.method == "POST":
        form = IssueForm(request.POST)
        if form.is_valid():
            # Read out form data
            category_1 = str(form.cleaned_data["category_1"])
            category_2 = str(form.cleaned_data["category_2"])
            category_3 = str(form.cleaned_data["category_3"])
            free_text = form.cleaned_data["free_text"]
            short_description = form.cleaned_data["short_description"]
            long_description = form.cleaned_data["long_description"]

            # Register activity
            desc_categories = add_arrows([category_1, category_2, category_3, free_text,])
            desc_act = f"{desc_categories} | {short_description}"
            act = Activity(
                title=_("You reported a problem."),
                description=desc_act,
                app="Hjelp",
                user=request.user.person,
            )
            act.save()

            # Send mail
            context = {
                "categories": add_arrows([category_1, category_2, category_3, free_text,]),
                "categories_single": (
                    element
                    for element in [category_1, category_2, category_3, free_text,]
                    if element and element != "None"
                ),
                "short_description": short_description,
                "long_description": long_description,
                "user": request.user,
            }
            send_templated_mail(
                template_name="rebus",
                from_email=request.user.person.mail_sender_via,
                headers={
                    "Reply-To": request.user.person.mail_sender,
                    "Sender": request.user.person.mail_sender,
                },
                recipient_list=[get_site_preferences()["hjelp__issue_report_recipient"]],
                context=context,
            )

            return render(request, "hjelp/issue_report_submitted.html")
    else:
        form = IssueForm()

    return render(request, "hjelp/issue_report.html", {"form": form})


@never_cache
@permission_required("hjelp.send_feedback_rule")
def feedback(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            # Read out form data
            design_rating = form.cleaned_data["design_rating"]
            performance_rating = form.cleaned_data["performance_rating"]
            usability_rating = form.cleaned_data["usability_rating"]
            overall_rating = form.cleaned_data["overall_rating"]
            more = form.cleaned_data["more"]
            ideas = form.cleaned_data["ideas"]
            apps = form.cleaned_data["apps"]

            # Register activity
            act = Activity.objects.create(
                title=_("You submitted feedback."),
                description=_(f"You rated AlekSIS with {overall_rating} out of 5 stars."),
                app="Feedback",
                user=request.user.person,
            )

            # Send mail
            context = {
                "design_rating": design_rating,
                "performance_rating": performance_rating,
                "usability_rating": usability_rating,
                "overall_rating": overall_rating,
                "more": more,
                "apps": apps,
                "ideas": ideas,
                "user": request.user,
            }
            send_templated_mail(
                template_name="feedback",
                from_email=request.user.person.mail_sender_via,
                headers={
                    "Reply-To": request.user.person.mail_sender,
                    "Sender": request.user.person.mail_sender,
                },
                recipient_list=[get_site_preferences()["hjelp__feedback_recipient"]],
                context=context,
            )

            return render(request, "hjelp/feedback_submitted.html")
    else:
        form = FeedbackForm()

    return render(request, "hjelp/feedback.html", {"form": form})
