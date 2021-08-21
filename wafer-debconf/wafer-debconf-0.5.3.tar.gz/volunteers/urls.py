from django.conf.urls import url

from volunteers.views import (
    TaskView, TasksView, VideoMassScheduleView, VideoShirtView,
    VolunteerStatisticsView, VolunteerView, VolunteerUpdate,
)

urlpatterns = [
    url(r'^$', TasksView.as_view(), name='wafer_tasks'),
    url(r'^tasks/(?P<pk>\d+)/$', TaskView.as_view(), name='wafer_task'),
    url(r'^statistics/$', VolunteerStatisticsView.as_view(),
        name='wafer_volunteer_statistics'),
    url(r'^(?P<slug>[\w.@+-]+)/$', VolunteerView.as_view(),
        name='wafer_volunteer'),
    url(r'^(?P<slug>[\w.@+-]+)/update/$', VolunteerUpdate.as_view(),
        name='wafer_volunteer_update'),
    url(r'^admin/video_mass_schedule/$', VideoMassScheduleView.as_view(),
        name='wafer_volunteer_video_mass_schedule'),
    url(r'^admin/video_shirts/$', VideoShirtView.as_view(),
        name='wafer_volunteer_video_shirt'),
]
