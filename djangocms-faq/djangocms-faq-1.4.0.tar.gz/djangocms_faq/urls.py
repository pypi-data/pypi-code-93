from django.urls import path

from . import views


urlpatterns = [
    path("", views.AnswerView, name="Answer Api"),
]
