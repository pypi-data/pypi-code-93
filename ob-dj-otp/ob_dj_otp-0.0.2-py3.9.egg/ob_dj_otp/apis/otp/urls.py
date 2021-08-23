from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from ob_dj_otp.apis.otp.views import OneTimePairingViewSet

app_name = "otp"

router = DefaultRouter()

router.register(r"", OneTimePairingViewSet, basename="otp"),

urlpatterns = [
    path("", include(router.urls)),
]
