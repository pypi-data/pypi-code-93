from django.urls import include, path
from rest_framework import routers
from .cms.urls import urlpatterns as cms_urls
from .api.urls import urlpatterns as api_urls
from .views import HomeRedirectView

app_name = "minutes"

urlpatterns = [
    path("", HomeRedirectView.as_view()),
    path("cms/", include((cms_urls, "cms"), namespace="cms")),
    path("api/", include((api_urls, "api"), namespace="api")),
]
