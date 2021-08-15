import click
from datetime import datetime, timezone
from getpass import getpass

from ocean import api, code, utils
from ocean.main import pass_env


@click.group(cls=utils.AliasedGroup)
def cli():
    pass


# Workloads
@cli.command()
@pass_env
def instances(ctx):
    res = api.get(ctx, "/api/instances/")
    body = utils.dict_to_namespace(res.json())

    fstring = "{:20} {:10} {:15} {:15}"

    click.echo(fstring.format("NAME", "STATUS", "TYPE", "VOLUME"))
    for pods in body.pods:
        click.echo(
            fstring.format(
                pods.name,
                pods.status,
                pods.labels.machineType.name,
                pods.volumes[0].persistentVolumeClaim.claimName,
            )
        )


@cli.command()
@click.option("-d", "--detail", help="Show selected sub tasks detail")
@click.option(
    "-A",
    "--detail-all",
    is_flag=True,
    help="Show all sub tasks detail. `--detail` option will be ignored.",
)
@pass_env
def jobs(ctx, detail, detail_all):
    detail = detail.split(",") if detail else None

    # conditions
    print_detail = detail or detail_all
    print_simple = (detail is None) and (not detail_all)
    filter_job = lambda x: print_simple or detail_all or (x in detail)

    # api call
    res = api.get(ctx, "/api/jobs/")
    body = utils.dict_to_namespace(res.json())

    fstring = "{:20} {:10} {:15} {:15} {:40} {:100}"

    click.echo(fstring.format("NAME", "STATUS", "TYPE", "VOLUME", "IMAGE", "COMMAND"))
    for jobInfo in body.jobsInfos:
        if not filter_job(jobInfo.name):
            continue

        pending, running, succeeded, failed = 0, 0, 0, 0
        details = []
        for job in jobInfo.jobs:
            status = job.jobPodInfos[0].status
            if status == "Pending":
                pending += 1
            elif status == "Running":
                running += 1
            elif status == "Succeeded":
                succeeded += 1
            elif status == "Failed":
                failed += 1

            if print_detail:
                start_time = utils.convert_time(job.startTime)
                complete_time = utils.convert_time(job.completionTime)
                delta = 0
                if status == "Running":
                    delta = (
                        datetime.now(timezone.utc).replace(microsecond=0) - start_time
                    )
                elif status == "Succeeded":
                    delta = complete_time - start_time

                start_time = utils.date_format(start_time)
                complete_time = utils.date_format(complete_time)

                details.append(
                    f"{job.name:20} {job.jobPodInfos[0].status:10} {start_time} ~ {complete_time} ({delta})"
                )

        click.echo(
            fstring.format(
                jobInfo.name,
                f"{succeeded}/{len(jobInfo.jobs)}",
                jobInfo.labels.machineType.name,
                jobInfo.volumes[0].persistentVolumeClaim.claimName,
                jobInfo.image,
                jobInfo.command,
            )
        )
        if print_detail:
            click.echo("\n".join(details))
            click.echo()


@cli.command()
@pass_env
def volumes(ctx):
    _volumes(ctx)


def _volumes(ctx, show_id=False):
    res = api.get(ctx, "/api/volumes/")
    body = utils.dict_to_namespace(res.json())

    fstring = "{:20} {:10} {:10}"
    fstring = "{id:5} " + fstring if show_id else fstring

    click.echo(fstring.format("NAME", "STATUS", "CAPACITY", id="ID"))
    for idx, vol in enumerate(body.volumes):
        click.echo(fstring.format(vol.name, vol.status, vol.capacity, id=str(idx)))

    return body.volumes


# Resources
@cli.command()
@pass_env
def images(ctx):
    _images(ctx)


def _images(ctx, show_id=False):
    res = api.get(ctx, "/api/images/")
    body = utils.dict_to_namespace(res.json())

    fstring = "{:10}"
    fstring = "{id:5} " + fstring if show_id else fstring

    click.echo(fstring.format("IMAGE", id="ID"))
    for idx, img in enumerate(body.images):
        click.echo(fstring.format(img, id=str(idx)))
    return body.images


@cli.command()
@pass_env
def quota(ctx):
    _quota(ctx)


def _quota(ctx, show_id=False):
    res = api.get(ctx, "/api/users/resources")

    body = utils.dict_to_namespace(res.json())
    fstring = "{:20} {:10} {:100}"
    fstring = "{id:5} " + fstring if show_id else fstring

    click.echo(fstring.format("NAME", "QUOTA", "SPEC", id="ID"))
    for idx, mt in enumerate(body.machineTypes):
        click.echo(
            fstring.format(
                mt.name,
                f"{mt.quotaUsedIn}/{mt.quota}",
                f"CPU {mt.cpus:2}, MEM {mt.memory:3} Gi, GPU {mt.gpus:1} x {mt.gpuType}",
                id=str(idx),
            )
        )
    return body.machineTypes


@cli.command()
@pass_env
def machine_types(ctx):
    _machine_types(ctx)


def _machine_types(ctx, show_id=False):
    res = api.get(ctx, "/api/machinetypes/")

    body = utils.dict_to_namespace(res.json())
    fstring = "{:20} {:100}"
    fstring = "{id:5} " + fstring if show_id else fstring

    click.echo(fstring.format("NAME", "SPEC", id="ID"))
    for idx, mt in enumerate(body):
        click.echo(
            fstring.format(
                mt.name,
                f"CPU {mt.cpus:4}, MEM {mt.memory:5} Gi, GPU {mt.gpus:1} x {mt.gpuType}",
                id=str(idx),
            )
        )
    return body


# CLI ENV
@cli.command()
@pass_env
def presets(ctx):
    _presets(ctx)


def _presets(ctx, show_id=False):
    fstring = "{:20} {:20} {:20} {:40}"
    fstring = "{id:5} " + fstring if show_id else fstring

    click.echo(fstring.format("NAME", "TYPE", "VOLUME", "IMAGE", id="ID"))
    for preset in utils.dict_to_namespace(ctx.get_presets()):
        default_txt = " (default)" if preset.default else ""
        click.echo(
            fstring.format(
                preset.name + default_txt,
                preset.machineType,
                preset.volume,
                preset.image,
            )
        )
