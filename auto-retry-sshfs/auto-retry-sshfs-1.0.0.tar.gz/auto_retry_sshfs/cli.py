import argparse

from .auto_retry_sshfs import autorefreshing_sshfs_utility


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-server", required=True, help="The server to sshfs from"
    )
    parser.add_argument("--source-path", required=True, help="The path to sshfs from")
    parser.add_argument("--target-path", required=True, help="The path to sshfs to")
    parser.add_argument(
        "--sshfs-options",
        help="The options to use",
        default="reconnect,ServerAliveInterval=15,ServerAliveCountMax=3,allow_other",
    )
    args = parser.parse_args()
    autorefreshing_sshfs_utility(
        args.source_server, args.source_path, args.target_path, args.sshfs_options
    )
