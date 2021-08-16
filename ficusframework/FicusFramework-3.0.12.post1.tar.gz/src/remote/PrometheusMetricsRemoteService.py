from flask import Response

from service import TaskQueueService
from . import remote

WAITING_TASK = "waiting_tasks"
WAITING_TASK_HELP = f"# HELP {WAITING_TASK} Number of tasks on waiting queue."
WAITING_TASK_TYPE = f"# TYPE {WAITING_TASK} gauge"
WAITING_TASK_CONTENT = f"{WAITING_TASK_HELP}\n{WAITING_TASK_TYPE}\n{WAITING_TASK} "


@remote.route('/metrics', methods=['GET'])
def metrics():
    """
    返回prometheus要求的数据指标
    我们的服务就增加一个指标即可.

    # HELP waiting_tasks Number of tasks on waiting queue.
    # TYPE waiting_tasks gauge
    waiting_tasks 10

    :return:
    """
    task_queue_proxy = TaskQueueService.task_queue_proxy()

    return Response(WAITING_TASK_CONTENT + str(task_queue_proxy.count_waiting_tasks()), mimetype='text/plain')
