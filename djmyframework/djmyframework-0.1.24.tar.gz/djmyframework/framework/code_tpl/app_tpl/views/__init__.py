# -*- coding: utf-8 -*-

from framework.translation import _
from drf_yasg.utils import swagger_auto_schema

from framework.filters import MyFilterBackend, MyFilterSerializer, OrderingFilter
from framework.route import Route
from framework.serializer import BaseModelSerializer, EditParams, IdSerializer, IdsSerializer, \
    PaginationSerializer, ParamsSerializer, s
from framework.views import action, BaseViewSet,CurdViewSet, notcheck, Request, Response, RspError,action_get,render_to_response,action_post