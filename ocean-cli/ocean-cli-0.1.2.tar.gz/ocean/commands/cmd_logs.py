import click
import time
import urllib3
import json
import sys

from ocean import api, code
from ocean.main import pass_env

from kubernetes import client, watch, config
from kubernetes.client.rest import ApiException


@click.command()
@click.argument("job-name")
@pass_env
def cli(ctx, job_name):
    _logs(ctx, job_name)


def _logs(ctx, job_name):
    config.load_incluster_config()

    try:
        api = client.CoreV1Api()

        label_selector = f"job-name={ctx.get_uuid()}-{job_name}"
        response = api.list_namespaced_pod(
            namespace="ocean", label_selector=label_selector
        )

        if len(response.items) == 1:
            pod_name = response.items[0].metadata.name

            start = time.time()
            since_seconds = None
            finish = False
            while not finish:
                finish = True
                try:
                    r = api.read_namespaced_pod_log(
                        name=pod_name,
                        namespace="ocean",
                        follow=True,
                        _preload_content=False,
                        _request_timeout=1,
                        since_seconds=since_seconds,
                    )
                    for log in r:
                        print(log.decode(), end="")
                        start = time.time()
                        since_seconds = None
                except urllib3.exceptions.ReadTimeoutError:
                    finish = False
                    since_seconds = int(time.time() - start + 0.6)
                    print(
                        f"{'Loading' + '.' * ((since_seconds % 5)-1):11} {since_seconds:3}s",
                        end="\r",
                    )
                    sys.stdout.write(
                        "\033[2K\033[1G"
                    )  # erase and go to beginning of line

                except ApiException as e:
                    finish = False
                    body = json.loads(e.body)
                    print(body["message"], end="\r")
                    sys.stdout.write(
                        "\033[2K\033[1G"
                    )  # erase and go to beginning of line

                except KeyboardInterrupt:
                    break

            click.echo("Job Finished.")
        else:
            click.echo("Invalid Job.")
    except Exception as e:
        click.echo(e)
