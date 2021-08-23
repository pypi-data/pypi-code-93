import base64
import subprocess
import sys
from functools import wraps
from typing import Optional, Tuple

import typer
import yaml


def kubectl(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except FileNotFoundError as e:
            if 'kubectl' in str(e):
                typer.echo('\'kubectl\' must be available. See https://kubernetes.io/docs/tasks/tools/install-kubectl.')
            else:
                typer.echo(str(e))
            sys.exit(1)
        except subprocess.CalledProcessError:
            sys.exit(1)

    return wrapped


@kubectl
def check_context(context: str) -> bool:
    return context == subprocess.check_output(['kubectl', 'config', 'current-context']).decode().strip()


@kubectl
def get_current_context() -> str:
    return subprocess.check_output(['kubectl', 'config', 'current-context']).decode().strip()


@kubectl
def get_cluster_info(context: str) -> Optional[Tuple[str, str]]:
    configs = yaml.load(subprocess.check_output(['kubectl', 'config', 'view', '--raw']).decode().strip(), yaml.FullLoader)
    for context_info in configs['contexts']:
        if context_info['name'] == context:
            cluster_name = context_info['context']['cluster']
            break
    else:
        typer.echo(f'No such context: {context}')
        sys.exit(1)

    for cluster_info in configs['clusters']:
        if cluster_info['name'] == cluster_name:
            cluster_info = cluster_info['cluster']
            ssl_ca_cert_base64_encoded = ''
            if 'certificate-authority' in cluster_info:
                with open(cluster_info['certificate-authority'], 'r') as f:
                    ssl_ca_cert_base64_encoded = base64.b64encode(f.read().encode()).decode()
            elif 'certificate-authority-data' in cluster_info:
                ssl_ca_cert_base64_encoded = cluster_info['certificate-authority-data']

            return cluster_info['server'], ssl_ca_cert_base64_encoded

    typer.echo(f'No such context: {context}')
    sys.exit(1)


@kubectl
def get_service_account_token(namespace: str) -> Optional[str]:
    try:
        service_account = yaml.load(subprocess.check_output(['kubectl', 'get', 'serviceaccounts/savvihub', '-n', namespace, '-o', 'yaml']), yaml.FullLoader)
    except subprocess.CalledProcessError:
        sys.exit(1)

    secret_name = service_account.get('secrets', [{}])[0].get('name')
    if secret_name is None:
        typer.echo('The service account does not have a required secret token.')
        sys.exit(1)

    try:
        secret = yaml.load(subprocess.check_output(['kubectl', 'get', 'secrets', secret_name, '-n', namespace, '-o', 'yaml']), yaml.FullLoader)
    except subprocess.CalledProcessError:
        sys.exit(1)

    return base64.b64decode(secret['data']['token']).decode()


@kubectl
def get_agent_access_token(namespace: str) -> Optional[str]:
    secret = yaml.load(
        subprocess.check_output(['kubectl', 'get', 'secrets', 'savvihub-agent', '-n', namespace, '-o', 'yaml']),
        yaml.FullLoader,
    )
    return base64.b64decode(secret['data']['access-token']).decode()
