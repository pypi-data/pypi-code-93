from django.conf.urls import include, url
from minidebconf.views import RegisterView, UnregisterView, RegistrationFinishedView

urlpatterns = [
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^unregister/$', UnregisterView.as_view(), name='unregister'),
    url(r'^register/finished/$', RegistrationFinishedView.as_view(), name='registration_finished'),
    url(r'', include('debconf.urls')),
    url(r'', include('wafer.urls')),
]
