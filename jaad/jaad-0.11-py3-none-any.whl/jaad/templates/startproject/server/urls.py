from django.conf.urls import url
from django.urls import include
from jaad.routes import jaad_views

urlpatterns = [
    url(r"^", jaad_views("index")),
    url(r"^doc/", include("documentation.urls")),
]
