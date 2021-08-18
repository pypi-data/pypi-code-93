import argparse
import os
from typing import Text

from convo.shared.utils.cli import printing_error
import convo.shared.nlu.training_data.loading
from convo.nlu.utils import write_to_file


def training_data_conversion(
    data_file: Text, out_file: Text, output_format: Text, language: Text
):
    if not os.path.exists(data_file):
        printing_error(
            "Data file '{}' does not exist. Provide a valid NLU data file using "
            "the '--data' argument.".format(data_file)
        )
        return

    if output_format == "json":
        train = convo.shared.nlu.training_data.loading.load_data_set(data_file, language)
        out_val = train.nlu_json(indent=2)
    elif output_format == "md":
        train = convo.shared.nlu.training_data.loading.load_data_set(data_file, language)
        out_val = train.nlu_markdown()
    else:
        printing_error(
            "Did not recognize output format. Supported output formats: 'json' and "
            "'md'. Specify the desired output format with '--format'."
        )
        return

    write_to_file(out_file, out_val)


def prime(args: argparse.Namespace):
    training_data_conversion(args.data, args.out, args.format, args.language)
