from django.conf import settings
from django.shortcuts import render
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt

from mozilla_django_oidc.views import OIDCLogoutView

from .utils import get_cookie_equivalency

class SilentCheckSSOView(View):
    @method_decorator(xframe_options_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, "authentication/silent-check-sso.html", locals())

class DnoticiasOIDCLogoutView(OIDCLogoutView):
    http_method_names = ['get', 'post']

    @property
    def redirect_url(self):
        return self.request.POST.get("next", self.get_settings('LOGOUT_REDIRECT_URL', '/'))

    def post(self, request):
        """
        This method extends the original oidc logout method and aditionally deletes
        the authentication cookies
        """
        response = super().post(request)
        auth_cookies = get_cookie_equivalency(all_names=True)
        extra = {
            "domain": settings.AUTH_COOKIE_DOMAIN,
            "samesite": "Strict"
        }

        # Deletes JUST the cookies that we need
        [response.delete_cookie(cookie, **extra) for _, cookie in auth_cookies.items()]

        return response
