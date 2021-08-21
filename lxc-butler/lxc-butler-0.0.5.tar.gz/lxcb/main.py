#! /usr/bin/env python3

import os
import sys
import site
import argparse


# add the directory which contains the lxcb module to the path. this will only
# ever execute when running the main.py script directly since the python
# package will use an entrypoint
if __name__ == '__main__':
    mod = os.path.dirname(os.path.realpath(__file__))
    site.addsitedir(os.path.dirname(mod))


from lxcb import info, create, mount


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subcommand', required=True)

    # create subparser
    parser_create = subparsers.add_parser('create')
    parser_create.add_argument('name')
    parser_create.add_argument('--distro', default=info.distro)
    parser_create.add_argument('--release', default=info.release)
    parser_create.add_argument('--arch', default=info.arch)
    parser_create.add_argument('--ssh-config',
                               default=f'{info.home}/.ssh/config.d/lxc')

    # mount subparser
    parser_mount = subparsers.add_parser('mount')
    parser_mount.add_argument('name')
    parser_mount.add_argument('host_path')
    parser_mount.add_argument('dest_path')

    args = parser.parse_args()

    if args.subcommand == 'create':
        return create.create(args.name, args.distro, args.release, args.arch,
                             args.ssh_config)
    elif args.subcommand == 'mount':
        return mount.add_mount(args.name, args.host_path, args.dest_path)


if __name__ == '__main__':
    sys.exit(1 if not main() else 0)
