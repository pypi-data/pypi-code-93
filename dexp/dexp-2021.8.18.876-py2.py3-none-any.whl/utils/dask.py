from dask.distributed import Client
from typing import Tuple, List
import subprocess


def dask_init_client(port: int = 8786, n_gpus: int = 1, n_cpu_process: int = 1) \
        -> Tuple[Client, List[subprocess.Popen]]:
    commands = [
        f'dask-scheduler --port {port}',
        f'dask-worker tcp://localhost:{port} --nprocs {n_cpu_process} --nthreads 1 --resources CPU=1 --memory-limit=30e9 --name read-worker',
        f'dask-cuda-worker tcp://localhost:{port} --resources GPU={n_gpus} --name gpu-worker',
        f'dask-worker tcp://localhost:{port} --nprocs {n_cpu_process} --nthreads 1 --resources CPU=1 --memory-limit=30e9 --name write-worker',
    ]
    processes = [subprocess.Popen(c, shell=True) for c in commands]
    client = Client(f'127.0.0.1:{port}')
    return client, processes
