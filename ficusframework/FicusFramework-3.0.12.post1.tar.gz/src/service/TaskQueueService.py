import logging

from client import ScheduleCloudClient
from config.annotation import Value
from libs.utils import Singleton
from schedule import TaskThreadHolder

log = logging.getLogger('Ficus')

class ITaskQueueProxy(object):

    def count_waiting_tasks(self) -> int:
        pass


class LocalTaskQueueProxy(ITaskQueueProxy, Singleton):
    """
    本地模式的任务队列
    """

    def count_waiting_tasks(self) -> int:
        queue = TaskThreadHolder.count_trigger_queue()

        if len(queue) == 0:
            return 0

        result = 0
        for count in queue.values():
            result = result + count
        return result


class CeleryTaskQueueProxy(ITaskQueueProxy, Singleton):
    """
    云调度模式的任务队列
    """

    def count_waiting_tasks(self) -> int:
        # 2020-04-29 11:39:27 这里要修改一下, 更换成为调用 云调度的接口,而不是直接访问celery的redis,
        # 原因在于, redis的等待队列,在任务接收或执行的时候,就已经在队列中被移除了.这样的数量就不正确了.

        import config
        try:
            return ScheduleCloudClient.count_tasks(config.actor_name, status=["NEW", "RECEIVED", "STARTED"])
        except Exception as e:
            log.warn(f"count_waiting_tasks error:{str(e)}")
            return 0

        # import cloudcelery
        # import config
        # try:
        #     redis = cloudcelery.celery_redis_client()
        #     return redis.llen(config.actor_name)
        # except Exception as e:
        #     print(f"{str(e)}")
        #     return 0


class TaskQueueProxyFactory(Singleton):
    __instance = None

    @Value("${celery.enable:false}")
    def enable_celery(self):
        pass

    def get_task_queue_proxy(self) -> ITaskQueueProxy:
        if self.__instance:
            return self.__instance

        if self.enable_celery():
            # 使用celery 即云调度模式
            self.__instance = CeleryTaskQueueProxy.instance()
        else:
            # 使用本地模式
            self.__instance = LocalTaskQueueProxy.instance()

        return self.__instance


def task_queue_proxy() -> ITaskQueueProxy:
    return TaskQueueProxyFactory.instance().get_task_queue_proxy()
