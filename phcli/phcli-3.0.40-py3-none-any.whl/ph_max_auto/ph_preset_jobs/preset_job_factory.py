from phcli.ph_errs.ph_err import exception_not_found_preset_job


def preset_factory(context, **kwargs):
    if 'preset.write_asset' == kwargs['job_name']:
        from phcli.ph_max_auto.ph_preset_jobs.write_asset import copy_job
        copy_job(context, **kwargs)
    else:
        raise exception_not_found_preset_job
