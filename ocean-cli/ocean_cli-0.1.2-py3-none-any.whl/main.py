import argparse
import click
from pathlib import Path
import os
import yaml
import sentry_sdk

from ocean import code


sentry_sdk.init(
    "https://a6b6c48c3f444b9f99ca70b543c09a46@o922093.ingest.sentry.io/5881410",
    traces_sample_rate=1.0,
)


CONTEXT_SETTINGS = dict(auto_envvar_prefix="COMPLEX")


class Environment:
    def __init__(self, load=True):
        self.verbose = False
        self.config_path = Path.home() / ".ocean" / "config.yaml"
        self.config = {}

        if load:
            self.load_config()

    def load_config(self):
        if not self.config_path.exists():
            click.echo(
                f"Config file '{self.config_path}' is not exist.\nPlease run \n\n\tocean init\n"
            )
            exit()

        with open(self.config_path, "r") as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

    def save_config(self):
        with open(self.config_path, "w") as f:
            yaml.dump(self.config, f)

    def update_config(self, key, value):
        self.config.update({key: value})
        self.save_config()

    def get_auth_token(self):
        return self.config.get(code.AUTH_TOKEN)

    def get_url(self):
        return self.config.get(code.OCEAN_URL)

    def get_token(self):
        return self.config.get(code.TOKEN)

    def get_username(self):
        self.config.get(code.USERNAME)

    def get_uuid(self):
        return self.config.get(code.UUID)

    # preset
    def get_presets(self):
        return self.config[code.PRESETS]

    def add_presets(self, preset):
        if preset[code.DEFAULT]:
            for p in self.config[code.PRESETS]:
                p[code.DEFAULT] = False
        self.config[code.PRESETS].append(preset)
        self.save_config()

    def delete_presets(self, key):
        for idx, pre in enumerate(self.config[code.PRESETS]):
            if pre["name"] == key:
                del self.config[code.PRESETS][idx]
                self.save_config()
                break
        else:
            click.echo(f"Preset `{key}` not found.")
            exit()

    def log(self, msg, *args):
        """Logs a message to stderr."""
        if args:
            msg %= args
        click.echo(msg, file=sys.stderr)

    def vlog(self, msg, *args):
        """Logs a message to stderr only if verbose is enabled."""
        if self.verbose:
            self.log(msg, *args)


pass_env = click.make_pass_decorator(Environment, ensure=True)
cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "commands"))


class ComplexCLI(click.MultiCommand):
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith(".py") and filename.startswith("cmd_"):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            mod = __import__(f"ocean.commands.cmd_{name}", None, None, ["cli"])
        except ImportError as e:
            print(e)
            return
        return mod.cli


@click.command(cls=ComplexCLI, context_settings=CONTEXT_SETTINGS)
def cli():
    pass


if __name__ == "__main__":
    cli()
