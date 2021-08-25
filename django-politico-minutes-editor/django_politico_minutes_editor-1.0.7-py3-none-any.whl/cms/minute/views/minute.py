from minutes.cms.common.views import CMSBaseView
from django.views.generic.base import RedirectView
from django.urls import reverse
from minutes.models import Edition, Vertical, Minute


class MinuteBase(CMSBaseView):
    template_name = "minute.html"
    model = Minute
    required_role = "REP"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        e = Edition.objects.get(id=kwargs["edition"])
        v = Vertical.objects.get(id=kwargs["vertical"])

        context["breadcrumbs"] = {
            "home": {"name": "Minutes", "url": reverse("minutes:cms:home")},
            "vertical": {
                "name": str(v),
                "url": reverse(
                    "minutes:cms:vertical", kwargs={"vertical": v.id}
                ),
            },
            "edition": {
                "name": str(e),
                "url": reverse(
                    "minutes:cms:edition-edit",
                    kwargs={"vertical": v.id, "edition": e.id},
                ),
            },
        }

        return context


class MinuteEditView(MinuteBase):
    def test_model_instance_exists(self, request, *args, **kwargs):
        Edition.objects.get(id=kwargs["edition"])
        Minute.objects.get(id=kwargs["minute"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["edition"] = kwargs["edition"]
        context["minute"] = kwargs["minute"]
        return context


class MinuteNewView(MinuteBase):
    def test_model_instance_exists(self, request, *args, **kwargs):
        Edition.objects.get(id=kwargs["edition"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["edition"] = kwargs["edition"]
        context["minute"] = None
        return context
