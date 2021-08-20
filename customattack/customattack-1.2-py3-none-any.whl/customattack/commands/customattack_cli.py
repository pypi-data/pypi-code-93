import argparse
from customattack.commands.attack_command import AttackCommand

def main():
    parser = argparse.ArgumentParser(
        "custom CLI",
        usage="[python -m] custom <commands> [<args>]",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(help="custom commands helpers")
    AttackCommand.register_subcommand(subparsers)

    # Let's go
    args = parser.parse_args()
    print("**parser args**", args)
    if not hasattr(args, "func"):
        parser.print_help()
        exit(1)
    # Run
    func = args.func
    del args.func
    func.run(args)


if __name__ == "__main__":
    main()