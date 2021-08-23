"""
    CALLBACKS
        - python functions executed on specific success/failure events
"""
import logging
from sdc_helpers.slack_helper import SlackHelper

logger = logging.getLogger(None)

def generate_slack_message(
    status: str,
    task: str,
    dag: str,
    exec_date: str,
    log_url: str,
    short_description: str = None,
):
    """generates a slack message from provided dag-task attributes"""
    if status == "success":
        symbol = ":large_green_circle:"
        if short_description is None:
            short_description = "Task Succeeded."
        else:
            short_description = short_description
    elif status == "failure":
        symbol = ":red_circle:"
        if short_description is None:
            short_description = "Task Failed."
        else:
            short_description = short_description
    else:
        symbol = ":warning:"
        if short_description is None:
            short_description = "no detail provided."
        else:
            short_description = short_description
    return """
        {symbol} {short_description}
        *Task*: {task}  
        *Dag*: {dag} 
        *Execution Time*: {exec_date}  
        *Log Url*: {log_url}
    """.format(
        symbol=symbol,
        short_description=short_description,
        task=task,
        dag=dag,
        exec_date=exec_date,
        log_url=log_url,
    )

def slack_notification_success(context):
    ti = context['task_instance']
    slack_msg = generate_slack_message(
        status='success',
        task=ti.task_id,
        dag=ti.dag_id,
        exec_date=context.get('execution_date'),
        log_url=ti.log_url,
    )
    slack_helper = SlackHelper()
    slack_helper.send_critical(message=slack_msg)

def slack_notification_failure(context):
    ti = context['task_instance']
    slack_msg = generate_slack_message(
        status='failure',
        task=ti.task_id,
        dag=ti.dag_id,
        exec_date=context.get('execution_date'),
        log_url=ti.log_url,
    )

    slack_helper = SlackHelper()
    slack_helper.send_critical(message=slack_msg)

def slack_notification_retry(context):
    ti = context['task_instance']
    slack_msg = generate_slack_message(
        status='warning',
        task=ti.task_id,
        dag=ti.dag_id,
        exec_date=context.get('execution_date'),
        log_url=ti.log_url,
        short_description="Task up for retry"
    )

    slack_helper = SlackHelper()
    slack_helper.send_critical(message=slack_msg)

def slack_notification_sla(context):
    ti = context['task_instance']
    slack_msg = generate_slack_message(
        status='warning',
        task=ti.task_id,
        dag=ti.dag_id,
        exec_date=context.get('execution_date'),
        log_url=ti.log_url,
        short_description="Failed to meet SLA"
    )

    slack_helper = SlackHelper()
    slack_helper.send_critical(message=slack_msg)
