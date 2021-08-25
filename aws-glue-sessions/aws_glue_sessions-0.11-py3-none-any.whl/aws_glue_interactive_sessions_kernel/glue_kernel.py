import os
import pathlib

import click


@click.group()
def cli():
    pass

@click.command()
def install():
    path = str(pathlib.Path(__file__).parent.absolute())
    os.system("echo 'Installing Glue kernels...'")
    os.system("chmod +x " + path + "/install.sh")
    os.system("sh " + path + "/install.sh")
    os.system("echo 'Glue kernels installed.'")

if __name__ == '__main__':
    install()
