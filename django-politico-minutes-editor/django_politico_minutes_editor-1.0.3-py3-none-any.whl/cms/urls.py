from django.urls import include, path
from rest_framework import routers
from django.contrib import admin
from .common.viewsets import EditingSessionViewset
from .edition.viewset import EditionViewset
from .minute.viewset import MinuteViewset
from .interstitial.viewset import InterstitialViewset
from .vertical.viewset import VerticalViewset
from .interstitial_instance.viewset import InterstitialInstanceViewset
from .sponsor.viewset import SponsorViewset

from .business.views import BusinessAdmin
from .home.views import HomeView, HomeAdminView
from .vertical.views import VerticalListView, VerticalView
from .edition.views import EditionNewView, EditionEditView
from .minute.views import MinuteNewView, MinuteEditView
from .interstitial.views import InterstitialNewView, InterstitialEditView
from .sponsor.views import SponsorNewView, SponsorEditView, SponsorListView

app_name = "cms"


router = routers.DefaultRouter()
router.register(
    r"editing-session", EditingSessionViewset, base_name="editing-session"
)
router.register(r"edition", EditionViewset, base_name="edition")
router.register(r"minute", MinuteViewset, base_name="minute")
router.register(r"interstitial", InterstitialViewset, base_name="interstitial")
router.register(r"vertical", VerticalViewset, base_name="vertical")
router.register(
    r"interstitial-instance",
    InterstitialInstanceViewset,
    base_name="interstitial-instance",
)
router.register(r"sponsor", SponsorViewset, base_name="sponsor")

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("api/", include(router.urls)),
    path("home/", HomeAdminView.as_view(), name="home-admin"),
    path("business/", BusinessAdmin.as_view(), name="business-admin"),
    path("vertical/", VerticalListView.as_view(), name="vertical-list"),
    path("vertical/<vertical>/", VerticalView.as_view(), name="vertical"),
    path(
        "vertical/<vertical>/edition/",
        EditionNewView.as_view(),
        name="edition-new",
    ),
    path(
        "vertical/<vertical>/edition/<edition>/",
        EditionEditView.as_view(),
        name="edition-edit",
    ),
    path(
        "vertical/<vertical>/edition/<edition>/minute/",
        MinuteNewView.as_view(),
        name="minute-new",
    ),
    path(
        "vertical/<vertical>/edition/<edition>/minute/<minute>/",
        MinuteEditView.as_view(),
        name="minute-edit",
    ),
    path(
        "business/interstitial/",
        InterstitialNewView.as_view(),
        name="interstitial-new",
    ),
    path(
        "business/interstitial/<interstitial>/",
        InterstitialEditView.as_view(),
        name="interstitial-edit",
    ),
    path("business/sponsor/", SponsorNewView.as_view(), name="sponsor-new"),
    path(
        "business/sponsor/<sponsor>/",
        SponsorEditView.as_view(),
        name="sponsor-edit",
    ),
]
