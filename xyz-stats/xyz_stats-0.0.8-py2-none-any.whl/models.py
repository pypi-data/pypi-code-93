# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.functional import cached_property
from xyz_util.datautils import str2dict
from django.contrib.contenttypes.models import ContentType


# Create your models here.

class Measure(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "度量"
        unique_together = ('content_type', 'code')

    content_type = models.ForeignKey(ContentType, verbose_name='归类', related_name='stats_measures',
                                     on_delete=models.PROTECT)
    code = models.CharField('编码', max_length=64)
    name = models.CharField('名称', max_length=64)
    description = models.TextField('描述', blank=True, default='')
    query_str = models.CharField('查询语句', blank=True, max_length=255, default='')
    agg_str = models.CharField('计算语句', blank=True, max_length=255, default='')
    time_field = models.CharField('时间字段', blank=True, max_length=64, default='')
    is_active = models.BooleanField('有效', blank=True, default=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('创建时间', auto_now=True)

    def __str__(self):
        return self.name

    def get_datetime_fields(self):
        m = self.content_type.model_class()._meta
        for f in m.get_fields():
            if isinstance(f, models.DateTimeField):
                yield f

    def save(self, **kwargs):
        if not self.time_field:
            fs = list(self.get_datetime_fields())
            if fs:
                self.time_field = fs[0].name
        super(Measure, self).save(**kwargs)

    def stat(self, base_queries='', context={}):
        from xyz_util.statutils import QuerySetStat, smart_filter_queryset
        qset = self.content_type.model_class()._base_manager.all()
        qs = self.query_str
        if base_queries:
            qs = base_queries + '&' + qs
        if 'the_date' in context:
            qs += '&%s__date=${the_date}' % self.time_field
        for k, v in context.items():
            qs = qs.replace('${%s}' % k, v)
        print(qs)
        qset = smart_filter_queryset(qset, qs)
        s = QuerySetStat(qset, measures=[self.agg_str])
        return s.stat()[self.agg_str]


class Report(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "报表"

    name = models.CharField('名称', max_length=64, unique=True)
    is_active = models.BooleanField('有效', blank=True, default=True)
    description = models.TextField('描述', blank=True, default='')
    measures = models.ManyToManyField(Measure, verbose_name=Measure._meta.verbose_name, blank=True, null=True,
                                      through='ReportMeasure', related_name='reports')
    base_queries = models.TextField('基础查询条件', blank=True, default='')
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('创建时间', auto_now=True)

    def __str__(self):
        return self.name

    @cached_property
    def contenttype_query_map(self):
        d = {}
        for k, v in str2dict(self.base_queries).items():
            if not k:
                continue
            ct = ContentType.objects.get_by_natural_key(*k.split('.'))
            d[ct] = v
        return d

    def get_base_queries(self, measure):
        return self.contenttype_query_map.get(measure.content_type)

    def stat(self, context={}):
        d = {}
        for rm in self.measure_relations.all():
            m = rm.measure
            d[m.code] = m.stat(base_queries=self.get_base_queries(m), context=context)
        return d

    def daily_store(self, the_date=None):
        from xyz_util.dateutils import format_the_date, get_next_date
        if not the_date:
            the_date = get_next_date(None, -1)
        else:
            the_date = format_the_date(the_date)
        the_date = the_date.isoformat()
        data = self.stat(dict(the_date=the_date))
        from .stores.stats import Report as ReportStore
        rs = ReportStore()
        rs.daily(self.id, the_date, data)

    def daily_query(self, begin_date=None, end_date=None):
        from .stores.stats import Report as ReportStore
        rs = ReportStore()
        fs = dict([(a, 1) for a in self.measures.all().values_list('code', flat=True)])
        fs['_id'] = 0
        fs['the_date'] = 1
        qd = {'id': self.id}
        if begin_date:
            qd.setdefault('the_date', {})['$gte'] = begin_date
        if end_date:
            qd.setdefault('the_date', {})['$lte'] = end_date
        return rs.collection.find(qd, fs).sort([('the_date', -1)])

    def get_table_fields(self):
        return [dict(name='the_date', label='日期')] \
               + [dict(name=rm.measure.code, label=rm.name, type='number') for rm in
                  self.measure_relations.all().order_by('order_num')]


class ReportMeasure(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "报表字段"
        unique_together = ('report', 'measure')
        ordering = ('report', 'order_num')

    report = models.ForeignKey(Report, verbose_name=Report._meta.verbose_name, related_name='measure_relations',
                               on_delete=models.PROTECT)
    measure = models.ForeignKey(Measure, verbose_name=Measure._meta.verbose_name, related_name='report_relations',
                                on_delete=models.PROTECT)
    name = models.CharField('名称', max_length=64, blank=True, default='')
    order_num = models.PositiveIntegerField('序号', blank=True, default=0)

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.name:
            self.name = self.measure.name
        super(ReportMeasure, self).save(**kwargs)

    def history_run(self):
        from .stores.stats import Report as ReportStore
        rs = ReportStore()
        rid = self.report_id
        hs = list(rs.collection.find(dict(id=rid), dict(_id=0, the_date=1)))
        for a in hs:
            the_date = a['the_date']
            v = self.measure.stat(base_queries=self.report.get_base_queries(self.measure),
                                  context=dict(the_date=the_date))
            d = {self.measure.code: v}
            rs.daily(rid, the_date, d)
            a['value'] = v
        return hs
