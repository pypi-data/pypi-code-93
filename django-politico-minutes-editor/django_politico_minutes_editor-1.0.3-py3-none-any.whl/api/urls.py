from django.urls import include, path
from rest_framework import routers
from .edition.viewset import EditionViewset
from .vertical.viewset import VerticalViewset

app_name = "api"

router = routers.DefaultRouter()
router.register(r"edition", EditionViewset, base_name="edition")
router.register(r"vertical", VerticalViewset, base_name="vertical")

urlpatterns = [path("", include(router.urls))]
