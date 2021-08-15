import click
import os
from getpass import getpass

from ocean import api, code, utils
from ocean.main import pass_env
from ocean.commands import cmd_get, cmd_logs, cmd_delete


@click.group(cls=utils.AliasedGroup)
def cli():
    pass


# Workloads
@cli.command()
@click.argument("name")
@click.option("-p", "--preset", help="run job with preset configuration")
@click.option("--purpose", default="None", help="purpose of job")
@click.option("-i", "--image", help="base docker image")
@click.option("-m", "--machine-type", help="machine-type to run this job")
@click.option("-v", "--volume", help="mounted volume")
@click.option("-r", "--repeat", default=1, help="how many repeat same job")
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    help="debug mode. follows logs and delete when finished.",
)
@click.argument("command", nargs=-1, type=click.Path())
@pass_env
def job(
    ctx, name, preset, purpose, image, machine_type, volume, repeat, debug, command
):
    # print(name, purpose, preset, image, machine_type, volume, repeat, command)

    if preset:
        presets = utils.dict_to_namespace(ctx.get_presets())
        for p in presets:
            if preset == p.name:
                image = p.image
                machine_type = p.machineType
                volume = p.volume
                break
        else:
            click.echo(
                "Invalid `preset`. Please check allowed preset here:\n\n\tocean get preset\n"
            )
            exit()
    else:
        presets = utils.dict_to_namespace(ctx.get_presets())
        for p in presets:
            if p.default:
                image = p.image
                machine_type = p.machineType
                volume = p.volume
                break

    if purpose == "" or purpose is None:
        click.echo("`purpose` cannot be blank.")
        exit(0)

    mid = api.get_id_from_machine_type(ctx, machine_type)
    if mid is None:
        click.echo(
            "Invalid `machine-type`. Please check allowed machine-type here:\n\n\tocean get quota\n"
        )
        exit()

    vid = api.get_volume_id_from_volume_name(ctx, volume)

    data = {
        code.NAME: name,
        code.PURPOSE: purpose,
        code.IMAGE: image,
        code.MACHINETYPEID: mid,
        code.VOLUMENAME: vid,
        code.REPEAT: repeat,
        code.COMMAND: " ".join(command),
    }

    res = api.post(ctx, code.API_JOB, data=data)
    click.echo(f"Job `{name}` Created.")

    if debug:
        # show logs
        cmd_logs._logs(ctx, name + "-0")

        # delete job
        cmd_delete._jobs(ctx, name)


@cli.command()
@pass_env
def presets(ctx):
    name = click.prompt("Preset Name")
    click.echo()

    machine_types = cmd_get._quota(ctx, show_id=True)
    machine_type_id = get_idx("MachineType ID", len(machine_types))
    machine_type = machine_types[machine_type_id].name
    click.echo()

    images = cmd_get._images(ctx, show_id=True)
    image_id = get_idx("Image ID", len(images))
    image = images[0]
    click.echo()

    volumes = cmd_get._volumes(ctx, show_id=True)
    volume_id = get_idx("Volume ID", len(volumes))
    volume = volumes[volume_id].name

    default = click.confirm("Set to default?")

    preset = {
        code.NAME: name,
        code.MACHINETYPE: machine_type,
        code.IMAGE: image,
        code.VOLUME: volume,
        code.DEFAULT: default,
    }

    click.echo()
    for k, v in preset.items():
        click.echo(f"{k.upper()}: {v}")
    ctx.add_presets(preset)


def get_idx(message, length):
    id = click.prompt(message, type=int)
    in_range = id in range(length)
    while not in_range:
        click.echo(f"Error: '{id}' is not a valid integer.")
        id = click.prompt(message, type=int)
        in_range = id in range(length)
    return id
