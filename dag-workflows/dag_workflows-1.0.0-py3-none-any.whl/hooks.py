"""
Optional hooks for handling events
"""
import requests

from workflows import bases


def make_slack_notification_hook(webhook_url: str, message_template: str):
    """
    Use this function to get an event hook that posts to Slack. Usage::

        from workflows import dags, hooks

        DAGS = dags.register_directory('dags')
        DAGS.register_hook(hooks.make_slack_notification_hook(
            os.environ['SLACK_WEBHOOK'], "Task {dag}:{task} failed with exception: {exception}. "
            f"Go to {os.environ['APP_DASHBOARD']} to see the full log output."
        ))
    """

    def slack_notification_hook(
        event: bases.Event, task: bases.Task = None, exception: Exception = None, **_
    ):
        if event is not bases.Event.TASK_FINISH or exception is None:
            return
        payload = {
            "text": message_template.format(dag=task.dag.name, task=task.name, exception=exception)
        }
        requests.post(url=webhook_url, json=payload)

    return slack_notification_hook
