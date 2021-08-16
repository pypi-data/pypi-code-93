import argparse
import subprocess
import sys

HELP_MSG = '''
ifa <command> [<args>]

The most commonly used commands are:
    run [seq] [config_file_path]                run IFA service in foreground
'''

class IfaEntrance(object):

    def __init__(self):
        parser = argparse.ArgumentParser(description='IFA Command Tool', usage=HELP_MSG)
        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print(f'Unrecognized command {args.command}\n')
            parser.print_help()
            exit(1)

        # ------ parser start ------
        self.main_parser = argparse.ArgumentParser(description='gun run')
        self.main_parser.add_argument('-s', '--msg_seq', help='Message sequence from which to start monitoring')
        self.main_parser.add_argument('-c', '--cfg', help='config file path')
        # ------ parser end ------

        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def run(self):
        from .ifa_runner import IfaRunner
        from .util.config import Configurator

        seq = None
        if len(sys.argv) > 1:
            args = self.main_parser.parse_args(sys.argv[2:])
            print(f'seq: {args.msg_seq}, cfg: {args.cfg}')

            if args.msg_seq:
                seq = int(args.msg_seq)

            if args.cfg:
                Configurator(args.cfg)

        runner = IfaRunner(seq)
        runner.run()
    
    # TODO: Implement start method, to run IFA service in background
    def start(self):
        raise Exception('"start" method not implemented, please use "run" instead.')

if __name__ == "__main__":
    entrance = IfaEntrance()
