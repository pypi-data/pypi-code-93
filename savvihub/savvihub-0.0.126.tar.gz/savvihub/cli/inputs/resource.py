from typing import Optional

import inquirer

from savvihub.cli.exceptions import ExitException
from savvihub.cli.typer import Context
from savvihub.cli.utils import inquire_list


def resource_name_callback(ctx: Context, resource_name: str) -> Optional[str]:
    assert ctx.params['organization_name'] and ctx.store['cluster']

    if ctx.store['cluster'].is_savvihub_managed:
        resources = ctx.authenticated_client.kernel_resource_list(ctx.params['organization_name']).results
        if resource_name:
            for resource in resources:
                if resource.name == resource_name.strip():
                    ctx.store['processor_type'] = resource.processor_type
                    ctx.store['resource_spec_id'] = resource.id
                    return resource.name
            else:
                raise ExitException(f'Resource not found: {resource_name.strip()}')
        else:
            selected_resource = inquire_list(
                "Please choose a resource",
                [(f'{x.name} ({x.description})', x) for x in resources],
            )
            ctx.store['processor_type'] = selected_resource.processor_type
            ctx.store['resource_spec_id'] = selected_resource.id
            return selected_resource.name

    elif resource_name:
        raise ExitException('--resource option can be set only with a savvihub-managed cluster')

    return None


def processor_type_callback(ctx: Context, processor_type: str) -> str:
    assert ctx.store['cluster']

    if ctx.store['cluster'].is_savvihub_managed:
        return ctx.store['processor_type']

    processor_type = processor_type.upper() if processor_type else None
    if processor_type not in ['CPU', 'GPU']:
        processor_type = inquire_list(
            "Please choose a processor type",
            ['CPU', 'GPU'],
        )
    return processor_type


def cpu_limit_callback(ctx: Context, cpu_limit: float) -> Optional[float]:
    assert ctx.store['cluster']
    if ctx.store['cluster'].is_savvihub_managed:
        return 0

    if cpu_limit <= 0:
        cpu_limit = float(inquirer.prompt([inquirer.Text(
            'question',
            message="CPU limit (the number of vCPUs)",
            default=1.0,
        )], raise_keyboard_interrupt=True).get('question'))
        if cpu_limit <= 0:
            raise ExitException('Must be greater than 0')

    return cpu_limit


def memory_limit_callback(ctx: Context, memory_limit: str) -> Optional[str]:
    assert ctx.store['cluster']
    if ctx.store['cluster'].is_savvihub_managed:
        return None
    if memory_limit:
        return memory_limit

    memory_limit = float(inquirer.prompt([inquirer.Text(
        'question',
        message="Memory limit in GiB",
        default='4.0',
    )], raise_keyboard_interrupt=True).get('question'))
    if memory_limit <= 0:
        raise ExitException('Must be greater than 0')

    return str(memory_limit) + 'Gi'


def gpu_type_callback(ctx: Context, gpu_type: str) -> str:
    assert ctx.store['cluster'] and ctx.params['processor_type']
    if ctx.store['cluster'].is_savvihub_managed or ctx.params['processor_type'] != 'GPU':
        return 'Empty'

    if gpu_type:
        return gpu_type

    nodes = ctx.authenticated_client.cluster_node_list(
        ctx.params['organization_name'], ctx.store['cluster'].name).nodes
    ctx.store['nodes'] = nodes
    gpu_type = inquire_list(
        "Please choose the GPU type",
        [(f'{x.gpu_product_name}: ({x.gpu_allocatable - x.gpu_limits}/{x.gpu_allocatable})', x) for x in nodes],
    ).gpu_product_name
    return gpu_type


def gpu_limit_callback(ctx: Context, gpu_limit: int) -> int:
    assert ctx.store['cluster'] and ctx.params['gpu_type']
    if ctx.store['cluster'].is_savvihub_managed or ctx.params['gpu_type'] == 'Empty':
        return 0

    if gpu_limit <= 0:
        gpu_limit = int(inquirer.prompt([inquirer.Text(
            'question',
            message="GPU limit (the number of GPUs)",
            default=1,
        )], raise_keyboard_interrupt=True).get('question'))
        if gpu_limit <= 0:
            raise ExitException('Must be greater than 0')
    return gpu_limit
