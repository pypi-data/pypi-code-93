import logging

from celery.signals import task_revoked

from api.model.ResultVO import ResultVO, FAIL_CODE
from cloudcelery import celery
from schedule import TriggerActor
from munch import Munch
import json

log = logging.getLogger('Ficus')


@celery.task(name='tasks.on_request', bind=True, max_retries=2, default_retry_delay=1 * 6)
def on_request(self, protocol):
    """
    从celery接收协议
    :param self:
    :param protocol:
    :return:
    """
    log.info(f"从celery中获取到任务:{protocol}")
    try:
        # 子进程中也开启eureka_client的刷新,因为celery也会起子进程,所以只能在这里初始化了
        from discovery import discovery_service_proxy
        import config
        discovery_service_proxy().registry_discovery(config.eureka_default_zone, renewal_interval_in_secs=4)
    except:
        pass

    try:
        # 在celery环境中,需要在celery的子进程中也初始化这个监听
        # 这里要提前获取一次,便于提前加载和开启数据库连接以及FD的变化监听
        from factdatasource import FactDatasourceProxyService
        FactDatasourceProxyService.fd_client_proxy()
        log.info("完成FD服务监听加载")
    except:
        pass

    body = Munch(json.loads(protocol))

    result: ResultVO = TriggerActor.handle_trigger(body, True)  # ResultVO
    log.info(f"任务执行完成，jobId:{body.jobId} logId:{body.logId}")

    if result.code == FAIL_CODE:
        # 让celery的任务也置失败
        raise RuntimeError(result.msg)

    return {'status': True, 'data': result.to_dict()}


@task_revoked.connect(sender=on_request,dispatch_uid="cloudcelery.CeleryOnRequest.on_request")
def on_revoke(request=None, terminated=None, signum=None, expired=None, **kwargs):

    if str(signum) != 'Signals.SIGKILL':
        return

    log.info(f"celery服务器:{request.hostname} 接收到任务:{request.id} 的取消事件(terminated:{terminated},expired:{expired})")
    log_id = request.reply_to

    try:
        from handlers import revoke_handler
    except Exception as e:
        # 说明可能没有这个方法
        return

    try:
        # 子进程中也开启eureka_client的刷新,因为celery也会起子进程,所以只能在这里初始化了
        from discovery import discovery_service_proxy
        import config
        discovery_service_proxy().registry_discovery(config.eureka_default_zone, renewal_interval_in_secs=4)
    except:
        pass

    # 这里就根据task_id去查询 log_id,job_id, task_handler
    from client import ScheduleJobTaskLogClient
    from api.handler.ICacheAbleHandler import CacheAbleHandlerHolder
    task_log = ScheduleJobTaskLogClient.get_task_log_by_id(log_id)

    # 这说明有这个方法了
    try:
        actorParam = Munch(json.loads(task_log.actorParam))
        #设置缓存需要的key
        CacheAbleHandlerHolder.get_handler().set_local_code(actorParam["site_"] + "_" + actorParam["projectCode_"] + "_" + actorParam["code_"])
        CacheAbleHandlerHolder.get_handler().set_process_id(actorParam.get("__processLogId__"))

        revoke_handler(task_log.actorCode, task_log.actorHandler, actorParam["code_"],
                       actorParam["projectCode_"], actorParam["site_"], task_log.id, task_log.jobId,
                       task_log.messageId, expired)
    except Exception as e:
        log.warning(f"任务:{task_log},取消回调失败:{str(e)}")
