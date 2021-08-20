from django.http import HttpResponse
from django.views.generic.base import RedirectView
from django.urls import reverse_lazy
from minutes.models import Vertical, User
from rest_framework.views import APIView


class HomeRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        url = reverse_lazy("minutes:cms:home")
        return url
