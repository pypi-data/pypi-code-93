#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from laipvt.sysutil.args import Args


def main():
    args = Args().parse_args()
    from laipvt.cli.deploy import deploy_main
    deploy_main(args)
