from django.urls.conf import path
from django.views.generic import RedirectView

app_name = "edc_mnsi"

urlpatterns = [
    path("", RedirectView.as_view(url="/admin/"), name="home_url"),
]
