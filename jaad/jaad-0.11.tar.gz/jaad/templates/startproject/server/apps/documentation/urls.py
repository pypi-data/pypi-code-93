from rest_framework_swagger.views import get_swagger_view

from django.conf.urls import url

schema_view = get_swagger_view(title="API Documentation")

urlpatterns = [url(r"^$", schema_view)]
