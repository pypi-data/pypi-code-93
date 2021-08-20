# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
from xyz_restful.mixins import IDAndStrFieldSerializerMixin
from rest_framework import serializers
from . import models


class ReportSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Report
        exclude = ()
        read_only_fields = ('create_time', 'update_time')


class MeasureSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    content_type_name = serializers.CharField(source='content_type.__str__', read_only=True)

    class Meta:
        model = models.Measure
        exclude = ()
        read_only_fields = ('create_time', 'update_time')

class ReportMeasureSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    report_name = serializers.CharField(source='report.__str__', read_only=True)
    measure_name = serializers.CharField(source='measure.__str__', read_only=True)

    class Meta:
        model = models.ReportMeasure
        exclude = ()


class ReportMeasureFullSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    measure = MeasureSerializer(read_only=True)

    class Meta:
        model = models.ReportMeasure
        exclude = ()
