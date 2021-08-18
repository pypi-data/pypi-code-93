import logging
import os
from typing import Text, Dict
import typing

import convo.shared.utils.io
from convo.constants import (
    ENVIRONMENT_GPU_CONFIGURATION,
    ENVIRONMENT_CPU_INTER_OP_CONFIGURATION,
    ENV_CPU_INTRA_OP_CONFIG,
)

if typing.TYPE_CHECKING:
    from tensorflow import config as tf_config

log = logging.getLogger(__name__)


def setup_gpu_env() -> None:
    """Set configuration for TensorFlow GPU environment based on the environment variable set."""

    gpu_memory_configuration = os.getenv(ENVIRONMENT_GPU_CONFIGURATION)

    if not gpu_memory_configuration:
        return

    # Import from tensorflow only if necessary (environment variable was set)
    from tensorflow import config as tf_config

    parsed_gpu_configuration = parse_gpu_configuration(gpu_memory_configuration)
    physical_gpus = tf_config.list_physical_devices("GPU")

    # Logic taken from https://www.tensorflow.org/guide/gpu
    if physical_gpus:
        for gpu_id, gpu_id_memory in parsed_gpu_configuration.items():
            allocating_gpu_memory(physical_gpus[gpu_id], gpu_id_memory)

    else:
        convo.shared.utils.io.raising_warning(
            f"You have an environment variable '{ENVIRONMENT_GPU_CONFIGURATION}' set but no GPUs were detected to configure."
        )


def allocating_gpu_memory(
    gpu_instance: "tf_config.PhysicalDevice", logical_memory: int
) -> None:
    """Create a new logical device for the requested amount of memory.

    Args:
        gpu_instance: PhysicalDevice instance of a GPU device.
        logical_memory: Absolute amount of memory to be allocated to the new logical device.
    """

    from tensorflow import config as tf_config

    try:
        tf_config.experimental.set_virtual_device_configuration(
            gpu_instance,
            [
                tf_config.experimental.VirtualDeviceConfiguration(
                    memory_limit=logical_memory
                )
            ],
        )

    except RuntimeError:
        # Helper explanation of where the error comes from
        raise RuntimeError(
            "Error while setting up tensorflow environment. "
            "Virtual devices must be set before GPUs have been initialized."
        )


def parse_gpu_configuration(gpu_memory_config: Text) -> Dict[int, int]:
    """Parse GPU configuration variable from a string to a dict.

    Args:
        gpu_memory_config: String containing the configuration for GPU usage.

    Returns:
        Parsed configuration as a dictionary with GPU IDs as keys and requested memory as the value.
    """

    # gpu_config is of format "gpu_id_1:gpu_id_1_memory, gpu_id_2: gpu_id_2_memory"
    # Parse it and store in a dictionary
    parsed_gpu_configuration = {}

    try:
        for instance in gpu_memory_config.split(","):
            gpu_instance_id, instance_gpu_memory = instance.split(":")
            gpu_instance_id = int(gpu_instance_id)
            instance_gpu_memory = int(instance_gpu_memory)

            parsed_gpu_configuration[gpu_instance_id] = instance_gpu_memory
    except ValueError:
        # Helper explanation of where the error comes from
        raise ValueError(
            f"Error parsing GPU configuration. Please cross-check the format of '{ENVIRONMENT_GPU_CONFIGURATION}' "
            f"at https://convo.com/docs/convo/tuning-your-model#restricting-absolute-gpu-memory-available ."
        )

    return parsed_gpu_configuration


def setup_cpu_env() -> None:
    """Set configuration for the CPU environment based on the environment variable set."""

    internal_op_parallel_thread = os.getenv(ENVIRONMENT_CPU_INTER_OP_CONFIGURATION)
    parallel_threads_intra_op = os.getenv(ENV_CPU_INTRA_OP_CONFIG)

    if not internal_op_parallel_thread and not parallel_threads_intra_op:
        return

    from tensorflow import config as tf_config

    if internal_op_parallel_thread:
        try:
            internal_op_parallel_thread = int(internal_op_parallel_thread.strip())
        except ValueError:
            raise ValueError(
                f"Error parsing the environment variable '{ENVIRONMENT_CPU_INTER_OP_CONFIGURATION}'. Please "
                f"cross-check the value."
            )

        tf_config.threading.set_inter_op_parallelism_threads(internal_op_parallel_thread)

    if parallel_threads_intra_op:
        try:
            parallel_threads_intra_op = int(parallel_threads_intra_op.strip())
        except ValueError:
            raise ValueError(
                f"Error parsing the environment variable '{ENV_CPU_INTRA_OP_CONFIG}'. Please "
                f"cross-check the value."
            )

        tf_config.threading.set_intra_op_parallelism_threads(parallel_threads_intra_op)


def setup_tf_env() -> None:
    """Setup CPU and GPU related environment settings for TensorFlow."""

    setup_cpu_env()
    setup_gpu_env()
