from spell.api.models import (
    ContainerResourceRequirements,
    PodAutoscaleConfig,
    ResourceRequirement,
    BatchingConfig
)


def create_pod_autoscale_config(
    min_pods,
    max_pods,
    target_cpu_utilization,
    target_requests_per_second,
    default_min_pods=None,
    default_max_pods=None,
    default_target_cpu_utilization=None,
    default_target_requests_per_second=None
):
    # All parameters may be None. If None, use the default value.
    pod_autoscale_config = PodAutoscaleConfig(
        min_pods=min_pods if min_pods else default_min_pods,
        max_pods=max_pods if max_pods else default_max_pods
    )

    if target_cpu_utilization is not None:
        pod_autoscale_config.target_cpu_utilization = int(target_cpu_utilization * 100)
    else:
        pod_autoscale_config.target_cpu_utilization = default_target_cpu_utilization

    if target_requests_per_second is not None:
        pod_autoscale_config.target_avg_requests_per_sec_millicores = int(
            target_requests_per_second * 1000
        )
    else:
        pod_autoscale_config.target_avg_requests_per_sec_millicores =\
            default_target_requests_per_second

    return pod_autoscale_config


def create_resource_requirements(
    ram_request,
    cpu_request,
    ram_limit,
    cpu_limit,
    gpu_limit,
    ram_request_default_value=None,
    cpu_request_default_value=None,
    ram_limit_default_value=None,
    cpu_limit_default_value=None,
    gpu_limit_default_value=None
):
    # All parameters may be None. If so, use the default value.
    resource_request = ResourceRequirement(
        memory_mebibytes=ram_request or ram_request_default_value
    )
    if cpu_request is not None:
        resource_request.cpu_millicores = int(cpu_request * 1000)
    else:
        resource_request.cpu_millicores = cpu_request_default_value

    resource_limit = ResourceRequirement(
        memory_mebibytes=ram_limit or ram_limit_default_value,
        gpu=gpu_limit or gpu_limit_default_value
    )
    if cpu_limit is not None:
        resource_limit.cpu_millicores = int(cpu_limit * 1000)
    else:
        resource_limit.cpu_millicores = cpu_limit_default_value

    return ContainerResourceRequirements(
        resource_request=resource_request,
        resource_limit=resource_limit,
    )


def create_batching_config(
    enable_batching,
    max_batch_size,
    request_timeout,
    enable_batching_default_value=False,
    max_batch_size_default_value=BatchingConfig.DEFAULT_MAX_BATCH_SIZE,
    request_timeout_default_value=BatchingConfig.DEFAULT_REQUEST_TIMEOUT
):
    # All parameters may be None. If None, use the default value.
    if (
        (enable_batching is True)
        or (enable_batching is None and enable_batching_default_value is True)
    ):
        return BatchingConfig(
            is_enabled=True,
            max_batch_size=max_batch_size or max_batch_size_default_value,
            request_timeout_ms=request_timeout or request_timeout_default_value,
        )
    else:
        return BatchingConfig(is_enabled=False)
