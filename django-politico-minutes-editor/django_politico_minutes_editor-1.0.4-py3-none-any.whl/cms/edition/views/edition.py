from minutes.cms.common.views import CMSBaseView
from django.views.generic.base import RedirectView
from django.urls import reverse
from minutes.models import Vertical, Edition


class EditionBase(CMSBaseView):
    template_name = "edition.html"
    model = Edition
    required_role = "REP"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vertical"] = kwargs["vertical"]
        v = Vertical.objects.get(id=kwargs["vertical"])

        context["breadcrumbs"] = {
            "home": {"name": "Minutes", "url": reverse("minutes:cms:home")},
            "role": {
                "name": "Editorial",
                "url": reverse("minutes:cms:vertical-list"),
            },
            "vertical": {
                "name": str(v),
                "url": reverse(
                    "minutes:cms:vertical", kwargs={"vertical": v.id}
                ),
            },
        }

        return context


class EditionEditView(EditionBase):
    def test_model_instance_exists(self, request, *args, **kwargs):
        Vertical.objects.get(id=kwargs["vertical"])
        Edition.objects.get(id=kwargs["edition"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["edition"] = kwargs["edition"]
        return context


class EditionNewView(EditionBase):
    def test_model_instance_exists(self, request, *args, **kwargs):
        Vertical.objects.get(id=kwargs["vertical"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["edition"] = None
        return context
