from django.urls import path

from lfl_admin.common.views.auth import login

urlpatterns = [
    path('login', login),
]
