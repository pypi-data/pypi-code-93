import geoip2
from django.contrib.auth import get_user_model
from django.contrib.gis.geoip2 import GeoIP2
from django.http import HttpRequest


def ip_to_country(ip):
    g = GeoIP2()
    try:
        return g.country(ip)["country_code"]
    except geoip2.errors.AddressNotFoundError:
        return None


class AuthenticatedHttpRequest(HttpRequest):
    user: get_user_model()


def request_to_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")
