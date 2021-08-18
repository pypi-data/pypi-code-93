'''
    Copyright 2018 SerialLab, CORP

    This file is part of SerialBox.

    SerialBox is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    SerialBox is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with SerialBox.  If not, see <http://www.gnu.org/licenses/>.
'''
from django.conf.urls import url
from serialbox.api import views, viewsets

import importlib
from django.apps import apps as django_apps
from serialbox.flavor_packs import FlavorPackApp
from serialbox.api.routers import urlpatterns as viewpatterns

urlpatterns = [
    url(r'^$', views.APIRoot.as_view(), name='api-index'),
    #####pools#####
    url(r'^pools/$', viewsets.pool_list, name='pool-list'),
    url(r'^pool-create/$', viewsets.pool_create, name='pool-create'),
    url(r'^pool-detail/(?P<machine_name>[\w\-\_]{1,100})/$',
        viewsets.pool_detail,
        name='pool-detail'),
    url(r'^pool-modify/(?P<machine_name>[\w\-\_]{1,100})/$',
        viewsets.pool_modify,
        name='pool-modify'),
    url(r'^pool-form/(?P<machine_name>[0-9a-zA-Z_\-]{1,100})/$',
        viewsets.pool_form,
        name='pool-form'),
    #####regions#####
    url(r'^sequential-regions/$',
        viewsets.sequential_region_list,
        name='sequential-region-list'),
    url(r'^sequential-region-create/$',
        viewsets.sequential_region_create,
        name='sequential-region-create'),
    url(r'^sequential-region-detail/(?P<machine_name>[\w\-\_]{1,100})/$',
        viewsets.sequential_region_detail,
        name='sequential-region-detail'),
    url(r'^sequential-region-modify/(?P<machine_name>[\w\-\_]{1,100})/$',
        viewsets.sequential_region_modify,
        name='sequential-region-modify'),
    url(r'^sequential-region-form/(?P<machine_name>[\w\-\_]{1,100})/$',
        viewsets.sequential_region_form,
        name='sequential-region-form'),
    #####allocation#####
    url(r'^allocate/$',
        views.AllocateView.as_view(),
        name='allocate'),
    url(r'^allocate/(?P<pool>[\w\-\_]{1,100})/(?P<size>[\d]{1,19})/$',
        views.AllocateView.as_view(), name='allocate-numbers'),
]

urlpatterns += viewpatterns

# This auto-magically imports and includes any flavorpack API urls into
# the overall API by going through each app and looking for app.api.urls confs
# and adding them..
allapps = django_apps.app_configs
for app in allapps.values():
    try:
        if isinstance(app, FlavorPackApp):
            importlib.import_module('%s.api.urls' % app.name)
            urlpatterns += app.module.api.urls.urlpatterns
    except ImportError:
        raise
