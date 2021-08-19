from minutes.cms.common.views import CMSBaseView
from django.views.generic.base import RedirectView
from django.urls import reverse, reverse_lazy
from minutes.models import Vertical, User


class BusinessAdmin(CMSBaseView):
    template_name = "business-admin.html"
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
