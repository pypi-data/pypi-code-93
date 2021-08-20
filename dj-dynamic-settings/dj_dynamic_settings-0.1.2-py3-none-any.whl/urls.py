from rest_framework.routers import DefaultRouter

from dj_dynamic_settings.views import DynamicSettingsViewSet

router = DefaultRouter()
router.register(r"dynamic_settings", DynamicSettingsViewSet)

urlpatterns = router.urls
