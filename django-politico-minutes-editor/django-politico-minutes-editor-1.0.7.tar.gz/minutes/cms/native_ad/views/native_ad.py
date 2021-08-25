from minutes.cms.common.views import CMSBaseView
from django.urls import reverse
from minutes.models import NativeAd


class NativeAdBase(CMSBaseView):
    template_name = "native-ad.html"
    model = NativeAd
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


class NativeAdEditView(NativeAdBase):
    def test_model_instance_exists(self, request, *args, **kwargs):
        NativeAd.objects.get(id=kwargs["native_ad"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["native_ad"] = kwargs["native_ad"]
        return context


class NativeAdNewView(NativeAdBase):
    def test_model_instance_exists(self, request, *args, **kwargs):
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["native_ad"] = None
        return context
