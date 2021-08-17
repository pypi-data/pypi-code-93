import random
import time
import json
import requests
import traceback
from multiprocessing.managers import BaseManager


from retry import retry
from loger import log


class HubManager(BaseManager):
    pass


class Task():
    key = ""
    task_type = ""
    priority = 1
    data = dict()
    status = "wait"
    start_time = 0
    nodeId = 0

    def __init__(self, key: str, priority: int, data: dict, task_type: str = ""):
        """[初始化Task]

        Args:
            key (str): [任务关键字，应保持唯一]
            priority (int): [优先级， 0 < priority < 1000000]
            data (dict): [数据收集，dict即可，但要保证可json序列化]

        Raises:
            TaskInitError: [初始化错误，检查数据格式与范围]
        """
        if isinstance(key, str) and isinstance(priority, int) and isinstance(data, dict)\
                and isinstance(task_type, str) and 0 < priority < 1000000:
            self.key = key
            self.priority = priority if priority < 1000000 else 1000000
            self.data = data
            self.task_type = task_type
        else:
            raise TaskInitError()

    def get_dict(self):
        return {
            "key": self.key,
            "priority": self.priority,
            "status": self.status,
            "data": self.data,
            "start_time": self.start_time,
            "nodeId": 0,
            "task_type": self.task_type
        }

    def __str__(self):
        return json.dumps(self.get_dict(), ensure_ascii=False)


class TaskHub():
    name = "taskhub"
    tasks = dict()
    lock = False
    back_end_url = ""
    timeout = 600
    check_gap = 20

    def __init__(self, sync):
        self.sync = sync

    def add(self, task: Task):
        """[summary]

        Args:
            task (Task): [要添加的task]

        Raises:
            TaskAlreadyExist: [task key已经存在]

        Returns:
            [bool]: [成功返回True]
        """

        # 加锁
        self.get_lock()
        # 检查是否存在
        if not self.tasks.get(task.key):
            # 不存在则添加
            self.tasks[task.key] = task
            log("task added!", 4)
            # 释放锁并返回
            self.release_lock()
            return True
        else:
            # 存在则释放锁并抛出异常
            self.release_lock()
            raise TaskAlreadyExist()

    def get(self, nodeId: int, filter_list: list = []):
        # 加锁
        self.get_lock()
        # 根据优先级排序 然后便利
        for key, task in sorted(self.tasks.items(), key=lambda item: item[1].priority):
            # 获取第一个是wait的 设置数据并返回
            if task.status == "wait" and task.task_type not in filter_list:
                task.node_id = nodeId
                task.status = "running"
                self.release_lock()
                return task
        else:
            # 全部遍历后均没有wait则释放锁返回None
            self.release_lock()

    def upload(self, task: Task):
        """[worker 向taskhub 上载数据，标志着该任务的完成]

        Args:
            task (Task): [任务对象，数据应在task.data]

        Raises:
            NodeIdNotMatch: [节点id不匹配，该任务不是由该节点获得，请检查]
            TaskNotRunning: [任务不是running状态]
            TaskNotExist: [任务不存在]

        Returns:
            [bool]: [成功则为true]
        """

        # 加锁
        self.get_lock()
        # 检查任务是否存在
        target_task = self.tasks.get(task.key)
        if target_task:
            # 检查任务状态是否正确
            if target_task.status == "running":
                # 检查nodeid是否正确
                if target_task.nodeId == task.nodeId:
                    target_task.data = task.data
                    target_task.status = "done"
                    self.release_lock()
                    return True
                else:
                    self.release_lock()
                    raise NodeIdNotMatch()
            else:
                self.release_lock()
                raise TaskNotRunning()
        else:
            self.release_lock()
            raise TaskNotExist()

    def serve(self):
        t = 0
        while True:
            if time.time() - t > self.check_gap:

                try:
                    # 加锁
                    self.get_lock()
                    # 输出状态
                    status_count = dict()
                    for key, task in self.tasks.items():
                        status_count[task.status] = status_count[task.status] + 1 if status_count.get(task.status) else 1
                    status_str = ""
                    for statu, amount in status_count.items():
                        status_str += "{}:{}  ".format(statu, amount)
                    log(status_str)

                    # 检查需要同步的数据
                    for_del_key = []
                    for key, task in self.tasks.items():
                        if task.status == "done":
                            # 将数据同步到后端
                            if self.sync(task):
                                for_del_key.append(key)
                    # 删除同步成功的
                    for key in for_del_key:
                        del self.tasks[key]

                except:
                    log("未知异常：{}".format(traceback.format_exc()), 1)

                finally:
                    # 释放锁
                    self.release_lock()

                t = time.time()
                time.sleep(1)

    def get_lock(self):
        # log("getting lock ....")
        while self.lock:
            time.sleep(random.random())
        self.lock = True
        # log("lock got!")

    def release_lock(self):
        self.lock = False
        # log("lock released!")


class TaskIdExitRequired(Exception):
    def __str__(self, task):
        return "id is required for a task dict!{}".format(task)


class TaskAlreadyExist(Exception):
    def __str__(self):
        return "task already exist! "


class TaskNotExist(Exception):
    def __str__(self, ):
        return "task not exist! "


class TaskInitError(Exception):
    def __str__(self):
        return "task pramar invalid! key:str priority:0<int<1000000 data:dict"


class TaskNotRunning(Exception):
    def __str__(self):
        return "task should be running but it in {} now"


class NodeIdTypeError(Exception):
    def __str__(self):
        return "nodeId must be int!"


class NodeIdNotMatch(Exception):
    def __str__(self):
        return "nodeId doesn`t match!"
