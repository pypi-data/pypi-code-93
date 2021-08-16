# -*- coding: utf-8 -*-
#
# 统计管理类
#
# django 常用导入
# =========================================
import datetime

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render



from framework.route import Route
from framework.views import JsonResponse
from ..models.log import LogDefine
from framework.utils import convert_to_datetime, trace_msg
from .query import query_view
from .statistic_module import StatisticManager
from ..models.query import Query
from ..models.statistic import QueryResult, Statistic


@Route('analysis/statistic/list')
def statistic_list(request, log_type=0):
    '''统计列表
    '''
    list_model = []
    log_type = int(log_type)

    log_type = int(request.GET.get('log_type', log_type))
    qs_type = int(request.GET.get('query_result', '0'))
    query_result_model = QueryResult.objects.all()

    q = Q()
    if qs_type:
        sid_by_group = QueryResult.objects.get(id=qs_type).statistic.all()
        sid_by_group = [i.id for i in sid_by_group]
        q = q & Q(id__in=sid_by_group)
    if log_type:
        q = q & Q(log_type=log_type)

    list_model = Statistic.objects.filter(q)
    # todo
    #from ..models import Server
    server_id = int(request.GET.get('server_id', '0'))
   # list_server = Server.get_server_list()
    list_log = LogDefine.objects.using('read').all()

    logDefine_list = LogDefine.objects.using('read').all()
    logDefineIdName = {}
    ResultTimes = {}

    not_center_log_id_list = []

    for logDefineItem in logDefine_list:
        logDefineIdName[logDefineItem.id] = logDefineItem.key
        if logDefineItem.status != LogDefine.PositionType.CENTER:
            not_center_log_id_list.append(logDefineItem.id)
    now = datetime.datetime.now()
    sdate = now.strftime('%Y-%m-%d 00:00:00')
    edate = now.strftime('%Y-%m-%d 23:59:59')

    for item in list_model:
        item.log_typeName = logDefineIdName.get(item.log_type, 0)
        item.last_exec_time = ResultTimes.get(item.id, item.last_exec_time)
        if not_center_log_id_list.__contains__(item.log_type):
            item.is_center_log = False
        else:
            item.is_center_log = True
    #import game_manage.views.widgets
    #group_servers_dict = game_manage.views.widgets.get_group_servers_dict(request)
    return render(request,'analysis/statistic_list.html', locals())

@Route('analysis/statistic/edit')
def statistic_edit(request, statistic_id=0, log_type=0):
    '''统计编辑
    '''
    statistic_id = int(statistic_id)
    log_type = int(log_type)
    is_copy = request.REQUEST.get('is_copy', '')
    if 0 == log_type:
        log_type = int(request.GET.get('log_type', 0))

    if 0 == statistic_id:
        statistic_id = int(request.GET.get('statistic_id', 0))

    if statistic_id > 0:
        model = Statistic.objects.get(id=statistic_id)
    else:
        model = Statistic()
        model.id = statistic_id
        model.log_type = log_type
        model.name = ''
    if is_copy:
        model.name = '%s-copy' % model.name
        model.id = 0

    if model.remove_field is None:
        model.remove_field = ""

    logs = LogDefine.objects.using('read').all()

    parg = {}
    parg["model"] = model
    parg["logs"] = logs

    return render(request,'analysis/statistic_edit.html', parg)

@Route('analysis/statistic/save')
def statistic_save(request, statistic_id=0):
    '''统计保存
    '''
    statistic_id = int(statistic_id)
    err_msg = ''
    if 0 == statistic_id:
        statistic_id = int(request.GET.get('statistic_id', 0))

    if statistic_id > 0:
        model = Statistic.objects.get(id=statistic_id)
    else:
        model = Statistic()
    try:
        model.log_type = int(request.POST.get('log_type', '0'))
        model.field_name = request.POST.get('field_name', '')
        model.remove_field = request.POST.get('remove_field', '')
        model.name = request.POST.get('name', '')
        model.set_attr('name', request.POST.get('name', ''), null=False)

        model.where = request.POST.get('where', '')
        model.count_type = int(request.POST.get('count_type', '0'))
        model.exec_interval = int(request.POST.get('exec_interval', '0'))
        model.is_save_center = int(request.POST.get('is_save_center', '0'))
        model.save_table_name = request.POST.get('save_table_name', '')
        model.last_exec_time = request.POST.get('last_exec_time')
        model.sql = request.POST.get('sql', '')

        model.is_auto_execute = int(request.POST.get('is_auto_execute', '0'))
        model.auto_exec_interval = int(request.POST.get('auto_exec_interval', '0'))
        model.remark = request.POST.get('remark', '')
        if model.last_exec_time == '':
            err_msg = "请输入开始时间"

        if not err_msg:
            model.save(using='write')
    except Exception as e:
        err_msg = trace_msg()

    return render(request,'feedback.html', locals())

@Route('analysis/statistic/remove')
def statistic_remove(request, statistic_id=0):
    '''统计删除
    '''
    model_id = int(statistic_id)

    if 0 == model_id:
        model_id = int(request.GET.get('statistic_id', 0))

    if model_id > 0:
        model = Statistic.objects.get(id=model_id)

        model.delete(using='write')

    return render(request,'feedback.html',locals())


@Route('analysis/statistic/test_query')
def test_query(request):
    '''测试查询
    '''
    statistic_id = int(request.REQUEST.get('statistic_id', '') or 0)
    try:
        if statistic_id:
            statistic_model = Statistic.objects.get(id=statistic_id)
            query_model = Query()
            query_model.sql = statistic_model.sql
            query_model.name = statistic_model.name
            query_model.select = 'time,game_alias,sdk_code,log_server,log_channel,log_channel2,log_tag,log_now,log_previous,log_result,log_data'
            query_model.log_def = statistic_model.log_def
            return query_view(request, query_model=query_model)
    except:
        err_msg = trace_msg()
    return HttpResponse(err_msg)


@Route('analysis/statistic/execute')
def statistic_execute(request, statistic_id=0, server_id=0):
    '''执行接口
    '''
    _r = {"code": -1, "msg": ""}
    server_id = int(request.REQUEST.get('server_id', '') or 0)
    statistic_id = int(request.REQUEST.get('statistic_id', '') or 0)
    sdate = request.REQUEST.get('sdate', '')
    edate = request.REQUEST.get('edate', '')

    try:
        assert sdate and edate and statistic_id, '时间或者统计ID为空!'
        sdate = convert_to_datetime(sdate)
        edate = convert_to_datetime(edate)
        server_ids = [server_id]
        statistic_ids = [statistic_id]
        sm = StatisticManager(sdate, edate, statistic_ids, server_ids)
        err_msgs = sm.start_update()[0]
        if not err_msgs:
            _r["code"] = 0
        _r["msg"] = '\n'.join(err_msgs)
    except:
        _r["msg"] = trace_msg()
    return JsonResponse(_r)
