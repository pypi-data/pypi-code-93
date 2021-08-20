from django.http import Http404
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.conf import settings
from minutes.utils.auth import secure
from django.contrib.auth.mixins import UserPassesTestMixin
from minutes.models import User


@secure
class CMSBaseView(UserPassesTestMixin, TemplateView):
    model = None

    def setup(self, request, *args, **kwargs):
        if self.model:
            try:
                self.test_model_instance_exists(request, *args, **kwargs)
            except:
                raise Http404("No {} found.".format(self.model.__name__))

        return super().setup(request, *args, **kwargs)

    def test_func(self):
        """
        Used with the UserPassesTestMixin.
        """
        # if not hasattr(self, "required_role"):
        #     return True

        # u = User.get_from_user(self.request.user)
        # if u is None:
        #     return False

        # return u.role == self.required_role or u.role == "ADM"
        return True

    def test_model_instance_exists():
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = []
        context["API_TOKEN"] = settings.MINUTES_API_TOKEN
        context["SERVICES_TOKEN"] = settings.MINUTES_SERVICES_TOKEN
        context["INACTIVE_TIMEOUT"] = settings.MINUTES_INACTIVE_TIMEOUT
        context["API_ROOT"] = reverse_lazy("minutes:cms:api-root")

        if self.request.user.is_authenticated:
            context["user"] = self.request.user
            minutes_user = User.objects.get(user=self.request.user)
            context["user_role"] = minutes_user.role
            context["user_id"] = minutes_user.id
        else:
            context["user"] = None
            context["user_role"] = None
            context["user_id"] = None

        return context
