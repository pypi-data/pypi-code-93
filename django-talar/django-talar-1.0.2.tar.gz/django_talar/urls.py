from django.urls import path

from . import views


urlpatterns = [
    path('notify/', views.NotifyView.as_view(), name='notify'),
]
