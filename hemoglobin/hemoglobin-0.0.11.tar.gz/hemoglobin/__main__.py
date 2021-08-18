import argparse
from getpass import getpass
from json import dumps as json_dumps
import logging

from .hemoglobin import Hemoglobin, Config
from .grammarbot import Language as Languages


def create_args():
    """
    Creates arguments for this main function.
    Returns the created parser object.
    """
    parser = argparse.ArgumentParser(description="Check the contents of text files")

    parser.add_argument("apikey", help="Your API key for GrammarBot.", nargs="?")
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        default=False,
        dest="use_json_output",
        help="Use argument to have the results output as json.",
    )
    parser.add_argument(
        "--language",
        "-l",
        help="Language to use.",
        choices=Languages,
        type=Languages,
        default=Languages.EN_US,
    )
    parser.add_argument("--log", dest="log_level", help="Log level.", default="warning")

    parser.add_argument("path", help="Where to find these files to parse.", nargs="+")
    return parser


def render_human(hemoglobin):
    for grammarbot_file in hemoglobin.files:
        print(grammarbot_file.f.name)
        for match in grammarbot_file.matches:
            print("\tSentence: {sentence}".format(sentence=match.sentence))
            print("\t\tMessage: {message}".format(message=match.message))
            print("\t\tPossible corrections:")
            for correction in match.corrections:
                print("\t\t\t{correction}".format(correction=correction))
            print("\t\tDetail:")
            print("\t\t\tType: {type}".format(type=match.type))
            print("\t\t\tCategory: {category}".format(category=match.category))
            print("\t\t\tRule: {rule}".format(rule=match.rule))
    print(
        "Number of API calls made: {api_calls_made}".format(
            api_calls_made=hemoglobin.grammarbot.api_calls_made
        )
    )


def render_json(hemoglobin):
    print(json_dumps(hemoglobin.to_dict()))


if __name__ == "__main__":
    args = create_args().parse_args()
    logging.basicConfig(level=args.log_level.upper())
    hemoglobin = Hemoglobin.from_config(Config.from_args(args))
    if args.use_json_output:
        render_json(hemoglobin)
    else:
        render_human(hemoglobin)
