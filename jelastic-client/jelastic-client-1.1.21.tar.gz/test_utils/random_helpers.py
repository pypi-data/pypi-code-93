import random
import string

from jelastic_client import ControlClient


def create_random_env_name(commit_sha: str, worker_id: str) -> str:
    env_id = "".join(random.choice(string.digits) for _ in range(7))
    return "-".join([commit_sha, worker_id, env_id])


def get_new_random_env_name(control_client: ControlClient, commit_sha: str, worker_id: str) -> str:
    env_name = create_random_env_name(commit_sha, worker_id)
    while control_client.get_env_info(env_name).exists():
        env_name = create_random_env_name(commit_sha, worker_id)
    return env_name
