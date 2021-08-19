from django.conf.urls import re_path

from unicef_snapshot.views import ActivityListView

app_name = 'snapshot'
urlpatterns = (
    re_path(r'^activity/$', view=ActivityListView.as_view(), name='activity-list'),
)
