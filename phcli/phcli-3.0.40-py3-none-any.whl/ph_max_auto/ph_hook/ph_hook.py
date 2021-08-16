from phcli.ph_max_auto.ph_hook.get_spark_session import get_spark_session_func
from phcli.ph_max_auto.ph_hook.get_abs_path import get_result_path
from phcli.ph_max_auto.ph_hook.get_abs_path import get_depends_path
from phcli.ph_max_auto.ph_hook.lineage import lineage
from phcli.ph_max_auto.ph_hook.copy_asset_data import copy_asset_data
from phcli.ph_max_auto.ph_hook.ssm_options import get_args_from_ssm
from phcli.ph_max_auto.ph_hook.ssm_options import delete_args_from_ssm
from phcli.ph_logs.phLogs.ph_logs import phs3logger, LOG_DEBUG_LEVEL

logger = phs3logger("hbzhao12345", LOG_DEBUG_LEVEL)
def exec_before(*args, **kwargs):

    name = kwargs.get('name', None)
    job_id = kwargs.get('job_id', name)

    spark_func = get_spark_session_func(job_id)
    result_path_prefix = get_result_path(kwargs)
    depends_path = get_depends_path(kwargs)
    step_args = get_args_from_ssm(kwargs)
    step_args.update({
        'spark': spark_func,
        'result_path_prefix': result_path_prefix,
        'depends_path': depends_path
    })
    logger.debug(step_args)

    return step_args


def exec_after(*args, **kwargs):
    owner = kwargs.get('owner', None)
    run_id = kwargs.get('run_id', None)
    job_id = kwargs.get('job_id', None)

    delete_args_from_ssm(kwargs)
    lineage(job_id, kwargs)
    copy_asset_data(kwargs)

    return kwargs



