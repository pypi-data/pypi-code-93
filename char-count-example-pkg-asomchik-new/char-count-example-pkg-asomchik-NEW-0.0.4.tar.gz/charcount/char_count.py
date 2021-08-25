"""
2021-08-06 Asomchik Aleksander
FoxMindEd Python course
Task 04
Function counting number of unique characters in a string
"""
from functools import lru_cache
from collections import Counter
import argparse


# main function counting unique characters in a string
@lru_cache
def char_count(text: str) -> int:

    if not isinstance(text, str):
        raise TypeError(f"str expected, but {type(text)} got")
    char_count_dict = Counter(text)
    unique_characters = 0
    for value in char_count_dict.values():
        if value == 1:
            unique_characters += 1
    return unique_characters


def cli_for_char_count():

    # Command line initialization
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file",
        help="path to file to count unique characters")
    parser.add_argument(
        "-s",
        "--string",
        help='string to count unique characters (use "")')
    args = parser.parse_args()

    # command line arguments processing
    if args.file:
        try:
            with open(args.file, "r") as file_object:
                print(char_count(file_object.read()))
        except FileNotFoundError:
            print("File not found")
        except PermissionError:
            print("Permission error occurred")

    elif args.string:
        print(char_count(args.string))
    else:
        print("No arguments were passed")


if __name__ == "__main__":
    cli_for_char_count()
