from django.urls import path
from . import views


urlpatterns = [
    path('silent-check-sso/', views.SilentCheckSSOView.as_view(), name="silent-check-sso"),
    path('logout/', views.DnoticiasOIDCLogoutView.as_view(), name="dnoticias-auth-logout"),
]
