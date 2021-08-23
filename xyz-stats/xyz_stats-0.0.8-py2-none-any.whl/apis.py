# -*- coding:utf-8 -*-
from __future__ import division, unicode_literals

from xyz_util.mongoutils import MongoPageNumberPagination

from . import models, serializers
from rest_framework import viewsets, decorators, response
from xyz_restful.decorators import register


@register()
class MeasureViewSet(viewsets.ModelViewSet):
    queryset = models.Measure.objects.all()
    serializer_class = serializers.MeasureSerializer
    search_fields = ('name', 'code', 'description')
    filter_fields = {
        'id': ['in', 'exact'],
        'name': ['exact'],
        'content_type': ['exact'],
        'is_active': ['exact'],
        'create_time': ['exact'],
    }


@register()
class ReportViewSet(viewsets.ModelViewSet):
    queryset = models.Report.objects.all()
    serializer_class = serializers.ReportSerializer
    search_fields = ('name', 'description')
    filter_fields = {
        'id': ['in', 'exact'],
        'name': ['exact'],
        'is_active': ['exact'],
        'create_time': ['exact'],
    }
    pagination_class = MongoPageNumberPagination


    @decorators.action(['GET'], detail=True)
    def daily(self, request, pk):
        report = self.get_object()
        qps = request.query_params
        rs = report.daily_query(begin_date=qps.get('begin_date'), end_date=qps.get('end_date'))
        ds = self.paginate_queryset(rs)
        return self.get_paginated_response(list(ds))
        # return response.Response(dict(results=ds, fields=report.get_table_fields()))

    @decorators.action(['POST'], detail=True)
    def run(self, request, pk):
        report = self.get_object()
        from xyz_util.dateutils import date_range
        qd = request.data
        rs = []
        for d in date_range(qd.get('begin_date'), qd.get('end_date')):
            report.daily_store(d)
            rs.append((d.isoformat(), 'ok'))
        return response.Response(dict(results=rs))


@register()
class ReportMeasureViewSet(viewsets.ModelViewSet):
    queryset = models.ReportMeasure.objects.all()
    serializer_class = serializers.ReportMeasureSerializer
    search_fields = ('name',)
    filter_fields = {
        'id': ['in', 'exact'],
        'report': ['exact'],
        'measure': ['exact']
    }

    def get_serializer_class(self):
        if self.action == 'full':
            return serializers.ReportMeasureFullSerializer
        return super(ReportMeasureViewSet, self).get_serializer_class()

    @decorators.action(['GET'], detail=False)
    def full(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @decorators.action(['POST'], detail=True)
    def history_run(self, request, pk, *args, **kwargs):
        rm = self.get_object()
        rs = rm.history_run()
        return response.Response(dict(results=rs))
