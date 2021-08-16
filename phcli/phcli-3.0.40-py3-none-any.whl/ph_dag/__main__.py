import click
from phcli.ph_dag.ph_airflow.__main__ import airflow


@click.group("dag", short_help='管理 DAG 相关技术栈')
def main():
    """
    管理 DAG 相关技术栈，如 Airflow
    """
    pass


main.add_command(airflow)

if __name__ == '__main__':
    main()
