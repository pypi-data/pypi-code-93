from django.conf.urls import url
from django.views.generic import RedirectView

from debconf.views import (
    ContentStatisticsView, DebConfScheduleView, IndexView,
    RobotsView, StatisticsView, now_or_next,
)

urlpatterns = [
    url(r'^favicon.ico$', RedirectView.as_view(url="/static/img/favicon.ico", permanent=True)),
    url(r'^schedule/$', DebConfScheduleView.as_view(),
        name='wafer_full_schedule'),
    url(r'^now_or_next/(?P<venue_id>\d+)/$', now_or_next, name="now_or_next"),
    url(r'^robots.txt$', RobotsView.as_view()),
    url(r'^$', IndexView.as_view()),
    url(r'^statistics/$', StatisticsView.as_view()),
    url(r'^talks/statistics/$', ContentStatisticsView.as_view(),
        name='content-statistics'),
]
