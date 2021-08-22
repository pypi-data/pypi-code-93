from django.urls import path
from .views import ListView
from .views import ReportView

app_name = 'apistat'
# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('list/', ListView.as_view()),
    path('report/<int:pk>', ReportView.as_view()),
]