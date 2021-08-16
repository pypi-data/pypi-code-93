from abc import abstractmethod

from client import ScheduleJobTaskLogClient


class IProgressAble:

    @abstractmethod
    def get_task_log_id(self):
        """
        获取任务的ID
        :return:
        """
        pass

    def update_task_progress(self, progress: float):
        """
        更新任务的进度
        :return:
        """
        task_log_id = self.get_task_log_id()
        if task_log_id is None:
            return

        ScheduleJobTaskLogClient.update_task_progress(task_log_id, progress)
