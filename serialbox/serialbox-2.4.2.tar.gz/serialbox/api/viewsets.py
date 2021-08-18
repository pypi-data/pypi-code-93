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
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from rest_framework import renderers
from rest_framework.decorators import action
from rest_framework.response import Response

from serialbox import models, viewsets
from serialbox.api import serializers
from serialbox.errors import RegionBoundaryException


class FormMixin(object):

    @action(renderer_classes=[renderers.HTMLFormRenderer], detail=True)
    def form(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)


class NumberResponseViewset(viewsets.ModelViewSet):
    """
    The default viewset for the Number Response model.
    """
    queryset = models.Response.objects.all()


class ResponseRuleViewSet(viewsets.ModelViewSet):
    '''
    CRUD ready model view for the ResponseRule model.
    '''
    queryset = models.ResponseRule.objects.all()
    serializer_class = serializers.ResponseRuleSerializer
    search_fields = ['=name', 'pool__readable_name', 'pool__machine_name',
                     'rule__name']

    def get_queryset(self):
        pool_id = self.kwargs.get('pool_id')
        if pool_id:
            return models.ResponseRule.objects.filter(pool=pool_id)
        else:
            return super().get_queryset()


class PoolViewSet(viewsets.SerialBoxModelViewSet, FormMixin):
    '''
    ## Description

    Returns info on a specific pool if a machine_name is supplied
    within the request.  To create Pool instances use the POST method
    on the pool-list API.

    ## Methods Supported
    *    GET - Will return the field info for a given Pool instance.

    ## Query Parameters

    * `related` If you would like the related Regions to come back as
    Hyperlinked Relations, pass in a query parameter of related and set
    it to true.
    * `format` The format parameters depend on your *Django Rest Framework*
    configuration and can be found on the API page listed under the **GET**
    button at the left upper side of each page.
    '''
    queryset = models.Pool.objects.all()
    lookup_field = 'machine_name'
    search_fields = ['readable_name', 'machine_name']

    def get_serializer_class(self):
        '''
        Return a different serializer depending on the client request.
        '''
        ret = serializers.PoolModelSerializer
        try:
            if self.request.query_params.get('related') == 'true':
                ret = serializers.PoolHyperlinkedSerializer
        except AttributeError:
            pass
        return ret

    def dispatch(self, request, *args, **kwargs):
        return viewsets.ModelViewSet.dispatch(self, request, *args, **kwargs)

    def get_view_name(self):
        return _('Pool API')


pool_list = PoolViewSet.as_view({'get': 'list', })
pool_create = PoolViewSet.as_view({'post': 'create'})
pool_detail = PoolViewSet.as_view({'get': 'retrieve', })
pool_modify = PoolViewSet.as_view(
    {'put': 'partial_update', 'delete': 'destroy', },
    lookup_field='machine_name')
pool_form = PoolViewSet.as_view({'get': 'form'},
                                renderer_classes=[renderers.HTMLFormRenderer])


class SequentialRegionViewSet(viewsets.SerialBoxModelViewSet, FormMixin):
    '''

    # Sequential Region API

    The Sequential Region API supports the following HTTP actions:

    * GET - Retrieve a region using the `machine_name`
    * POST - Create a region by posting a serialized sequential region in *JSON*
    or *XML* format.
    * PUT - Update a region by posting a serialized sequential region in *JSON*
    or *XML* format.
    * DELETE - Delete a region by using the `machine_name` of the region.

    '''
    queryset = models.SequentialRegion.objects.all()
    lookup_field = 'machine_name'

    def list(self, request, *args, **kwargs):
        return viewsets.ModelViewSet.list(self, request, *args, **kwargs)

    def get_serializer_class(self):
        '''
        Return a different serializer depending on the client request.
        '''
        ret = serializers.SequentialRegionSerializer
        try:
            if self.request.query_params.get('related') == 'true':
                ret = serializers.SequentialRegionHyperlinkedSerializer
        except AttributeError:
            pass
        return ret

    def create(self, request, *args, **kwargs):
        try:
            return viewsets.ModelViewSet.create(self, request, *args, **kwargs)
        except ValidationError as v:
            raise RegionBoundaryException(v.detail)


sequential_region_list = SequentialRegionViewSet.as_view({
    'get': 'list'
})
sequential_region_create = SequentialRegionViewSet.as_view({
    'post': 'create'
})
sequential_region_detail = SequentialRegionViewSet.as_view({
    'get': 'retrieve'
})
sequential_region_modify = SequentialRegionViewSet.as_view({
    'put': 'partial_update',
    'delete': 'destroy'
})
sequential_region_form = SequentialRegionViewSet.as_view({
    'get': 'form'
})
sequential_region_form = SequentialRegionViewSet.as_view({
    'get': 'form'
}, renderer_classes=[renderers.HTMLFormRenderer])
