import git
import os
import click
import git
import sys
from github import Github
import subprocess


# cli_commands for the buildpan 

from c_commands import init
from c_commands import version

@click.group(help="CLI tool to manage CI- CD of projects")
def buildpan():
    pass


buildpan.add_command(init.init)
buildpan.add_command(version.version)

if __name__ == '__main__':
    buildpan()