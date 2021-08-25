from minutes.cms.common.views import CMSBaseView
from django.views.generic.base import RedirectView
from django.urls import reverse
from minutes.models import Vertical


class VerticalListView(CMSBaseView):
    template_name = "vertical-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["breadcrumbs"] = {
            "home": {"name": "Minutes", "url": reverse("minutes:cms:home")},
            "role": {
                "name": "Editorial",
                "url": reverse("minutes:cms:vertical-list"),
            },
        }

        return context


class VerticalView(CMSBaseView):
    template_name = "vertical.html"
    model = Vertical

    def test_model_instance_exists(self, request, *args, **kwargs):
        Vertical.objects.get(id=kwargs["vertical"])

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
