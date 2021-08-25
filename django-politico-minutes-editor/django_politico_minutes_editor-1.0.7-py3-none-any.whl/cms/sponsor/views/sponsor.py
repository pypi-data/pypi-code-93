from minutes.cms.common.views import CMSBaseView
from django.views.generic.base import RedirectView
from django.urls import reverse
from minutes.models import Edition, Sponsor


class SponsorBase(CMSBaseView):
    template_name = "sponsor.html"
    model = Sponsor
    required_role = "ADV"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["breadcrumbs"] = {
            "home": {"name": "Minutes", "url": reverse("minutes:cms:home")},
            "role": {
                "name": "Business",
                "url": reverse("minutes:cms:business-admin"),
            },
        }

        return context


class SponsorEditView(SponsorBase):
    def test_model_instance_exists(self, request, *args, **kwargs):
        Sponsor.objects.get(id=kwargs["sponsor"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sponsor"] = kwargs["sponsor"]
        return context


class SponsorNewView(SponsorBase):
    def test_model_instance_exists(self, request, *args, **kwargs):
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sponsor"] = None
        return context


class SponsorListView(CMSBaseView):
    template_name = "sponsor-list.html"
    required_role = "ADV"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["breadcrumbs"] = {
            "home": {"name": "Minutes", "url": reverse("minutes:cms:home")},
            "role": {
                "name": "Advertisements",
                "url": reverse("minutes:cms:sponsor-list"),
            },
        }

        return context
