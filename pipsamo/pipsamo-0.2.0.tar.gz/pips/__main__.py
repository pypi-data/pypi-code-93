
# from pips import PIP, cli
from pips.pip import PIP
from pips import cli


def run():
    args = cli.parse_args()
    PIP().do(
        **args,
    )


if __name__ == '__main__':
    run()
