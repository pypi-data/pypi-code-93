import logging

from django.conf import settings
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt

from mozilla_django_oidc.views import OIDCLogoutView

from .utils import get_cookie_equivalency

logger = logging.getLogger(__name__)


class SilentCheckSSOView(View):
    @method_decorator(xframe_options_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, "authentication/silent-check-sso.html", locals())


class DnoticiasOIDCLogoutView(OIDCLogoutView):
    http_method_names = ['get', 'post']

    @property
    def redirect_url(self) -> str:
        """
        This function was created using the keycloak redirect URL as a LOGOUT_REDIRECT_URL
        /auth/realms/<realm>/protocol/openid-connect/logout?redirect_uri=<URL>

        If we provide a next value via POST, the redirect_uri will be that value.
        If we do not have a next value, the redirect_uri will be the base url.
        """
        logout_url = self.get_settings('LOGOUT_REDIRECT_URL', None)
        base_url = self.get_settings('BASE_URL', None)
        next_url = self.request.POST.get('next') or self.request.GET.get('next', '') or base_url

        if not logout_url:
            logout_url = ''
            logger.warning("No LOGOUT_REDIRECT_URL configured!")

        if not base_url:
            base_url = '/'
            logger.warning("No BASE_URL configured! Using / as default...")

        return logout_url + next_url if logout_url else base_url

    def post(self, request) -> HttpResponseRedirect:
        """
        This method extends the original oidc logout method and aditionally deletes
        the authentication cookies
        """
        super().post(request)

        # Response is defined first because we need to delete the cookies before redirect
        response = HttpResponseRedirect(self.redirect_url)
        auth_cookies = get_cookie_equivalency(all_names=True)
        extra = {
            "domain": settings.AUTH_COOKIE_DOMAIN,
            "samesite": "Strict"
        }

        # Deletes ONLY the cookies that we need
        [response.delete_cookie(cookie, **extra) for _, cookie in auth_cookies.items()]

        return response
