from urllib.parse import urlparse, parse_qs, urlencode
from typing import Union

from django.urls import reverse
from django import template

register = template.Library()


def _build_url(reverse_url: str, context: dict, next_url: Union[str, None], to_root: bool) -> str:
    """
    Builds and return an url to login/logout an user
    Typed params are used to prevent unwanted types and a posible error during the process.
    """
    request = context.get("request")
    next_url = next_url or request.COOKIES.get("next", None)
    params = {}

    if not next_url and not to_root:
        location = '/' if to_root else None
        next_url = request.build_absolute_uri(location)
    else:
        absolute_url = urlparse(request.build_absolute_uri())
        url = urlparse(next_url)

        params = parse_qs(url.query)
        absolute_params = parse_qs(absolute_url.query)
        absolute_params.update(params)

        next_url = request.build_absolute_uri(request.path)
        next_url = "{}?{}".format(next_url, urlencode(absolute_params))

    params['next'] = next_url

    return "{}?{}".format(
        reverse(reverse_url),
        urlencode(params),
    )


@register.simple_tag(takes_context=True)
def get_logout_url(context, next_url=None, to_root=False):
    """
    Builds the logout URL with a next url param
    """
    return _build_url('dnoticias-auth-logout', context, next_url, to_root)


@register.simple_tag(takes_context=True)
def get_login_url(context, next_url=None, to_root=False):
    """
    Same as get_logout_url but in login action
    """
    return _build_url('oidc_authentication_init', context, next_url, to_root)
