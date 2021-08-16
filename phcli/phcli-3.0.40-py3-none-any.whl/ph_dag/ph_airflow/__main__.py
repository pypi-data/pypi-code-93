import requests
import json
import click

AIRFLOW_DOMAIN = 'http://airflow.pharbers.com'
AIRFLOW_API_VERSION = '/api/v1'
BASE_URL = AIRFLOW_DOMAIN + AIRFLOW_API_VERSION
DAGS_URL = BASE_URL+'/dags'
DAG_URL = BASE_URL+'/dags/{dag_id}'
DAG_TASKS_URL = BASE_URL+'/dags/{dag_id}/tasks'
DAG_TASK_URL = BASE_URL+'/dags/{dag_id}/tasks/{task_id}'
DAG_RUNS_URL = BASE_URL+'/dags/{dag_id}/dagRuns'
auth_user = ()


def format_json_str(j):
    return json.dumps(j, sort_keys=True, indent=4, separators=(',', ':'))


@click.group("airflow")
@click.option("-u", "--user", help="验证用户", default=':')
def airflow(user):
    """
    airflow 管理
    """
    global auth_user
    auth_user = tuple(user.split(':'))


@airflow.group("dag")
def dag():
    """
    airflow DAG 管理
    """
    pass


@dag.command("list", short_help='列出符合条件的 DAG 信息')
@click.option("-o", "--owners", help="所有者", default=None)
@click.option("-t", "--include_tags", help="包含标签", default=None)
@click.option("-T", "--exclude_tags", help="排除标签", default='example, example2, example3')
def dag_list(**kwargs):
    result = requests.get(DAGS_URL, auth=auth_user).json()

    include_owners = [owner.strip() for owner in kwargs['owners'].split(',')] if kwargs['owners'] else []
    include_tags = [tag.strip() for tag in kwargs['include_tags'].split(',')] if kwargs['include_tags'] else []
    exclude_tags = [tag.strip() for tag in kwargs['exclude_tags'].split(',')] if kwargs['exclude_tags'] else []

    # 筛选 DAG
    dags = []
    for dag in result['dags']:
        # 按照 tag 筛选
        flag = False if include_tags else True
        for tag in [tag['name'] for tag in dag['tags']]:
            if tag in exclude_tags:
                flag = False
                break
            if tag in include_tags:
                flag = True
        if not flag:
            continue

        # 按照 owner 筛选
        flag = False if include_owners else True
        for owner in dag['owners']:
            if owner in include_owners:
                flag = True
        if not flag:
            continue

        dags.append(dag)
    result['dags'] = dags
    result['total_entries'] = len(dags)

    print(format_json_str(result))


@dag.command("summary", short_help='统计指定 DAG 的运行信息')
@click.option("--dag_id", help="DAG ID", default=None)
def dag_summary(**kwargs):
    dag_id = kwargs['dag_id']
    if not dag_id:
        click.secho(str('未指定 DAG ID'), fg='red', blink=True, bold=True)
        return

    dag_info = requests.get(DAG_URL.format(dag_id=dag_id), auth=auth_user).json()

    dag_task_list = requests.get(DAG_TASKS_URL.format(dag_id=dag_id), auth=auth_user).json()
    dag_info['tasks'] = dag_task_list

    dag_run_list = requests.get(DAG_RUNS_URL.format(dag_id=dag_id), params={'limit': 10000}, auth=auth_user).json()
    state_summary = {}
    for dag_run in dag_run_list['dag_runs']:
        state = dag_run['state']
        state_summary[state] = state_summary.get(state, 0) + 1
    dag_run_list['success_entries'] = state_summary.get('success', 0)
    dag_run_list['failed_entries'] = state_summary.get('failed', 0)
    dag_run_list['running_entries'] = state_summary.get('running', 0)
    dag_info['dag_runs'] = dag_run_list

    print(format_json_str(dag_info))


@dag.command("trigger", short_help='执行指定 DAG')
@click.option("--dag_id", help="DAG ID", default=None)
@click.argument('args', nargs=1, default="{}")
def dag_trigger(**kwargs):
    dag_id = kwargs['dag_id']
    if not dag_id:
        click.secho(str('未指定 DAG ID'), fg='red', blink=True, bold=True)
        return

    dag_trigger = requests.post(DAG_RUNS_URL.format(dag_id=dag_id),
                                json={"conf": json.loads(kwargs['args'])},
                                auth=auth_user).json()
    print(format_json_str(dag_trigger))


@airflow.group("task")
def task():
    """
    airflow TASK 管理
    """
    pass


@task.command("list", short_help='列出指定 DAG 的 TASK 信息')
@click.option("--dag_id", help="DAG ID")
@click.option("-ed", "--execution_date", help="TASK 启动时间")
def task_list_by_dag(**kwargs):
    dag_id = kwargs['dag_id']
    if not dag_id:
        click.secho(str('未指定 DAG ID'), fg='red', blink=True, bold=True)
        return



