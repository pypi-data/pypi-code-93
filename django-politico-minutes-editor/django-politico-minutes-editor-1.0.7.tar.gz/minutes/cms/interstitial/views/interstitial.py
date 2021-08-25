from minutes.cms.common.views import CMSBaseView
from django.views.generic.base import RedirectView
from django.urls import reverse
from minutes.models import Edition, Interstitial


class InterstitialBase(CMSBaseView):
    template_name = "interstitial.html"
    model = Interstitial
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


class InterstitialEditView(InterstitialBase):
    def test_model_instance_exists(self, request, *args, **kwargs):
        Interstitial.objects.get(id=kwargs["interstitial"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["interstitial"] = kwargs["interstitial"]
        return context


class InterstitialNewView(InterstitialBase):
    def test_model_instance_exists(self, request, *args, **kwargs):
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["interstitial"] = None
        return context
