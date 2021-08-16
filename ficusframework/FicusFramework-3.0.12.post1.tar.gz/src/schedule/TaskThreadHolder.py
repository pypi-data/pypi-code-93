import json
import logging

from munch import Munch

from schedule.TaskThread import TaskThread
from libs.utils import stop_thread

__actor_port = 8011
__task_thread_cache = dict()

log = logging.getLogger('Ficus')


def registry_task_thread(task_id: int, handler, remove_old_reason: str):
    """
       注册一个任务线程
    :param task_id:
    :param handler: ITaskHandler
    :param remove_old_reason:
    :return:
    """
    # 实例化一个线程
    new_task_thread = TaskThread(handler, __actor_port)
    new_task_thread.start()  # 开启线程

    old_task_thread: TaskThread = __task_thread_cache.get(task_id)
    __task_thread_cache[task_id] = new_task_thread

    if old_task_thread is not None:
        old_task_thread.stop(remove_old_reason)
        stop_thread(old_task_thread)

    return new_task_thread


def callback_revoke(log_id):
    try:
        from handlers import revoke_handler
    except Exception as e:
        # 说明可能没有这个方法
        return

    # 这里就根据task_id去查询 log_id,job_id, task_handler
    from client import ScheduleJobTaskLogClient
    from api.handler.ICacheAbleHandler import CacheAbleHandlerHolder
    task_log = ScheduleJobTaskLogClient.get_task_log_by_id(log_id)

    # 这说明有这个方法了
    try:
        actorParam = Munch(json.loads(task_log.actorParam))
        # 设置缓存需要的key
        CacheAbleHandlerHolder.get_handler().set_local_code(actorParam["site_"] + "_" + actorParam["projectCode_"] + "_" + actorParam["code_"])
        CacheAbleHandlerHolder.get_handler().set_process_id(actorParam.get("__processLogId__"))

        revoke_handler(task_log.actorCode, task_log.actorHandler, actorParam["code_"],
                       actorParam["projectCode_"], actorParam["site_"], task_log.id, task_log.jobId,
                       task_log.messageId, False)
    except Exception as e:
        log.warning(f"任务:{task_log},取消回调失败:{str(e)}")


def remove_task_thread(job_id: int, remove_old_reason: str, log_id: int = None):
    """
    删除一个任务线程
    :param job_id:
    :param remove_old_reason:
    :return:
    """
    old_task_thread: TaskThread = __task_thread_cache.pop(job_id)

    if old_task_thread is not None:
        old_task_thread.stop(remove_old_reason)
        stop_thread(old_task_thread)
        # 这里也需要回调
        if log_id is not None:
            callback_revoke(log_id)


def cancel_task_thread(job_id: int, task_id: int, is_executing: bool):
    """
    停止某一个任务
    :param job_id:
    :param task_id:
    :param is_executing:
    :return:
    """
    task_thread: TaskThread = __task_thread_cache.get(job_id)

    if task_thread is not None:
        if is_executing:
            # 说明任务已经开始做了,不杀掉整个Job的Thread
            task_thread.kill_doing_task(task_id)
            callback_revoke(task_id)
        else:
            # 说明任务还没真正开始做,还在队列里面.
            task_thread.remove_trigger_queue(task_id)


def load_task_thread(task_id: int):
    """
    返回一个任务线程
    :param task_id:
    :return:
    """
    return __task_thread_cache.get(task_id)


def count_trigger_queue() -> dict:
    """
    返回一个 Map<Integer,Integer>
    :return:
    """
    result = {}
    for k, v in __task_thread_cache.items():
        result[k] = v.count_trigger_queue()

    return result
