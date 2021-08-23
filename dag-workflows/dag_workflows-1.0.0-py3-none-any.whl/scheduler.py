import datetime
import enum
import logging
import signal
import time

from croniter import croniter
from django.db import transaction
from django.utils import timezone

from workflows import bases, managers, models, utilities

LOGGER = logging.getLogger(__name__)


class State(enum.Enum):
    """Scheduler state, used to control behavior after receiving a signal"""

    STOPPED = "Stopped"
    RUNNING = "Running"
    SHUTDOWN = "Shutting down"
    TERMINATE = "Terminating"


class Scheduler:
    """
    Scheduler  handles the cron triggering and the stateful database management.
    Calls out to the task manager class to run tasks.
    """

    state = State.STOPPED

    def __init__(self, registry: bases.DagRegistry, task_manager: managers.TaskManager):
        self.registry = registry
        self.started = timezone.now()
        self.task_manager = task_manager

    def run(self):
        """Run DAGs as scheduled in a perpetual loop"""
        self.state = State.RUNNING
        self.handle_signals()
        LOGGER.info("Scheduler started")

        while True:
            LOGGER.debug("Scheduling loop started")
            loop_start = time.time()
            self.update_tasks()

            if self.state == State.RUNNING:
                self.start_tasks()
                if managers.try_advisory_lock("scheduler"):
                    self.trigger_dags()
                    self.trigger_tasks()
            elif self.state == State.SHUTDOWN:
                finished = self.task_manager.shutdown()
                if finished:
                    break
            else:  # State.TERMINATE
                self.task_manager.terminate()
                break

            # don't run the loop more than once per second
            loop_duration = time.time() - loop_start
            time.sleep(max(1 - loop_duration, 0))

        LOGGER.info("Scheduler exited")

    @utilities.close_on_exception
    def trigger_dags(self):
        """Create a new DagRun record for DAGs that are ready"""
        for dag in self.registry:
            LOGGER.debug("Considering dag %s", dag)
            if not dag.schedule:
                continue
            # trigger only the most recent missed run or wait for an initial run
            last_run = (
                models.DagRun.objects.filter(dag=dag.name, creator="scheduler")
                .order_by("-created")
                .first()
            )
            start_date = last_run.created if last_run else self.started
            next_run = croniter(dag.schedule, timezone.now()).get_prev(datetime.datetime)
            if start_date < next_run:
                LOGGER.info("Scheduling dag %s for %s", dag, next_run)
                dag_run = models.DagRun.objects.create(
                    dag=dag.name, creator="scheduler", created=next_run
                )
                self.registry.call_hooks(bases.Event.DAG_RUN_START, dag_run=dag_run)

    @utilities.close_on_exception
    def trigger_tasks(self):
        """Start tasks within a DAG"""
        # runs cannot overlap; only the earliest run will have tasks scheduled
        dag_runs = (
            models.DagRun.objects.filter(status=models.DagStatus.RUNNING)
            .order_by("dag", "created")
            .distinct("dag")
        )
        for dag_run in dag_runs:
            try:
                dag = self.registry[dag_run.dag]
            except (bases.RegistrationError, KeyError):
                LOGGER.warning("DAG %s not found, marking as failed", dag_run.dag)
                dag_run.status = models.DagStatus.FAILED
                dag_run.save()
                continue
            # get the latest status of each task
            task_statuses = {
                task_run.task: task_run.status
                for task_run in dag_run.taskrun_set.distinct("task").order_by("task", "-attempt")
            }
            # trigger runs for tasks with successful predecessors
            for node in dag.tasks():
                # skip if node already has a status
                if task_statuses.get(node) is not None:
                    continue
                upstream_statuses = {
                    task_statuses.get(upstream) for upstream in dag.tasks(inputs_to=node)
                }
                if upstream_statuses.issubset({models.TaskStatus.SUCCEEDED}):
                    LOGGER.debug("Scheduling task %s in DAG %s", node, dag_run)
                    models.TaskRun.objects.create(dag_run=dag_run, task=node)
                # record the status for the DAG status calculation below
                if models.TaskStatus.FAILED in upstream_statuses:
                    task_statuses[node] = models.TaskStatus.FAILED
                else:
                    task_statuses[node] = models.TaskStatus.WAITING

            # mark DAG as succeeded or failed if ALL tasks are finished
            dag_statuses = set(task_statuses.values())
            if dag_statuses.issubset({models.TaskStatus.SUCCEEDED}):
                LOGGER.debug("Marking DAG as successful %s", dag_run)
                dag_run.status = models.DagStatus.SUCCEEDED
            elif dag_statuses.issubset({models.TaskStatus.SUCCEEDED, models.TaskStatus.FAILED}):
                LOGGER.debug("Marking DAG as failed %s", dag_run)
                dag_run.status = models.DagStatus.FAILED
            else:  # pragma: no cover see https://github.com/nedbat/coveragepy/issues/198
                continue
            dag_run.save()
            self.registry.call_hooks(bases.Event.DAG_RUN_FINISH, dag_run=dag_run)

    @utilities.close_on_exception
    def start_tasks(self):
        ready_tasks = models.TaskRun.objects.filter(status=models.TaskStatus.WAITING).order_by(
            "created"
        )[: self.task_manager.slots]
        for task_run in ready_tasks:
            with transaction.atomic():
                # lock the row so no other worker considers this task
                task_run = (
                    models.TaskRun.objects.select_for_update(skip_locked=True)
                    .filter(id=task_run.id)
                    .first()
                )
                if not task_run:  # pragma: no cover hard to simulate the lock...
                    continue
                self.task_manager.start_task(task_run)

    @utilities.close_on_exception
    def update_tasks(self):
        running_tasks = models.TaskRun.objects.filter(status=models.TaskStatus.RUNNING).order_by(
            "created"
        )
        self.task_manager.update_tasks(running_tasks)

    def handle_signals(self):
        """
        Handle signals:
        - SIGINT waits for running tasks to stop, then exits
        - SIGTERM kills running tasks, saves to the database, and exits
        """

        def handle_sigterm(*args):
            self.state = State.TERMINATE
            LOGGER.warning("Received SIGTERM, killing running tasks and exiting.")

        def handle_sigint(*args):
            self.state = State.SHUTDOWN
            LOGGER.warning("Received SIGINT, shutting down after running tasks have finished.")
            LOGGER.warning("Press CTL-C again to shut down immediately.")
            signal.signal(signal.SIGINT, handle_sigterm)

        signal.signal(signal.SIGINT, handle_sigint)
        signal.signal(signal.SIGTERM, handle_sigterm)
