#!/usr/bin/env python3
import click
from . import Googler as g


@click.command()
@click.argument('query', nargs=-1)
@click.option('--private', '-p', is_flag=True, type=bool, help='Use to search privately')
def search_in_google(query, private: bool):
    if private:
        g(query).search_in_new_private_tab()
    else:
        g(query).search_in_new_tab()


if __name__ == '__main__':
    search_in_google()
