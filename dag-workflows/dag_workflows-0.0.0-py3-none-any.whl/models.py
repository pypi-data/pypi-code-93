from django.db import models
from django.utils import timezone

from workflows import bases


class DagStatus(models.TextChoices):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(models.TextChoices):
    WAITING = "waiting"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


def current_time():
    """Make the time easier to read"""
    return timezone.now().replace(microsecond=0)


class DagRun(models.Model):
    """A single run of a DAG"""

    dag = models.TextField()
    created = models.DateTimeField(default=current_time)
    creator = models.TextField()  # ie auto from schedule or a person
    status = models.TextField(choices=DagStatus.choices, default=DagStatus.RUNNING)
    parameters = models.JSONField(default=dict)

    class Meta:
        unique_together = ["dag", "created"]
        indexes = [
            models.Index(
                fields=["status"],
                name="workflows_dagrun_status_sparse",
                condition=models.Q(status=DagStatus.RUNNING),
            )
        ]

    def __str__(self):
        return f"DagRun({self.dag} @ {self.created})"


class TaskRun(models.Model):
    """A single run of a Task"""

    dag_run = models.ForeignKey(DagRun, models.PROTECT)
    task = models.TextField()
    attempt = models.IntegerField(default=1)
    status = models.TextField(choices=TaskStatus.choices, default=TaskStatus.WAITING)
    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(null=True)
    ended = models.DateTimeField(null=True)
    host = models.TextField(null=True)

    class Meta:
        unique_together = ["task", "dag_run", "attempt"]
        indexes = [
            models.Index(
                fields=["status"],
                name="workflows_taskrun_stat_sparse",
                condition=models.Q(status__in=[TaskStatus.RUNNING, TaskStatus.WAITING]),
            )
        ]

    def __str__(self):
        return f"TaskRun({self.dag_run.dag}:{self.task} #{self.attempt})"

    def mark_started(self, registry: bases.DagRegistry):
        registry.call_hooks(bases.Event.TASK_RUN_FINISH, task_run=self)

        self.started = timezone.now()
        self.status = TaskStatus.RUNNING
        self.save()

    def mark_succeeded(self, registry: bases.DagRegistry):
        self.status = TaskStatus.SUCCEEDED
        self._finish(registry)

    def mark_failed(self, registry: bases.DagRegistry):
        self.status = TaskStatus.FAILED
        self._finish(registry)

    def _finish(self, registry: bases.DagRegistry):
        # started will be null if we are here bc the task failed to start
        self.started = self.started or timezone.now()
        self.ended = timezone.now()
        self.save()

        registry.call_hooks(bases.Event.TASK_RUN_FINISH, task_run=self)

        if self.status is TaskStatus.FAILED and self.attempt < 3:
            # queue another attempt
            TaskRun.objects.create(
                dag_run_id=self.dag_run_id, task=self.task, attempt=self.attempt + 1
            )
