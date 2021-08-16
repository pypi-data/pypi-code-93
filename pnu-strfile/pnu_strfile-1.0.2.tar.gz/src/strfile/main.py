#!/usr/bin/env python
""" strfile, unstr - create a random access file for storing strings
License: 3-clause BSD (see https://opensource.org/licenses/BSD-3-Clause)
Author: Hubert Tournier
"""

import getopt
import logging
import os
import random
import re
import struct
import sys

# Version string used by the what(1) and ident(1) commands:
ID = "@(#) $Id: strfile, unstr - create a random access file for storing strings v1.0.2 (August 16, 2021) by Hubert Tournier $"

# Default parameters. Can be overcome by command line options
parameters = {
    "Unstr": False,
    "Has comments": False,
    "Delimiting char": "%",
    "Ignore case": False,
    "Alphabetical order": False,
    "Randomize access": False,
    "Run silently": False,
    "Is rotated": False,
    "Command flavour": "",
}

# strfile constants:
STR_VERSION = 1
STR_RANDOM = 0x1
STR_ORDERED = 0x2
STR_ROTATED = 0x4
STR_COMMENTS = 0x8


################################################################################
def display_strfile_usage():
    """Displays usage"""
    print("strfile [-Ciorsx] [-c char] source_file [output_file]", file=sys.stderr)


################################################################################
def display_unstr_usage():
    """Displays usage"""
    print("usage: unstr datafile", file=sys.stderr)


################################################################################
def display_help():
    """Displays usage and help"""
    if parameters["Unstr"]:
        print("usage: unstr [--debug] [--help|-?] [--version]", file=sys.stderr)
        print("       [--] datafile", file=sys.stderr)
        print("  ---------  --------------------------------------------------", file=sys.stderr)
    else:
        print("usage: strfile [--debug] [--help|-?] [--version]", file=sys.stderr)
        print("       [-Ciorsx] [-c char] [--] source_file [output_file]", file=sys.stderr)
        print("  ---------  --------------------------------------------------", file=sys.stderr)
        print("  -C         Flag the file as containing comments", file=sys.stderr)
        print("  -c char    Change the delimiting character from % to char", file=sys.stderr)
        print("  -i         Ignore case when ordering the strings", file=sys.stderr)
        print("  -o         Order the strings in alphabetical order", file=sys.stderr)
        print("  -r         Randomize access to the strings", file=sys.stderr)
        print("  -s         Run silently", file=sys.stderr)
        print("  -x         Alphabetic characters are rotated 13 positions", file=sys.stderr)
    print("  --debug    Enable debug mode", file=sys.stderr)
    print("  --help|-?  Print usage and this help message and exit", file=sys.stderr)
    print("  --version  Print version and exit", file=sys.stderr)
    print("  --         Options processing terminator", file=sys.stderr)
    print(file=sys.stderr)


################################################################################
def process_environment_variables():
    """Process environment variables"""
    # pylint: disable=C0103
    global parameters
    # pylint: enable=C0103

    if "STRFILE_DEBUG" in os.environ.keys() \
    or "UNSTR_DEBUG" in os.environ.keys():
        logging.disable(logging.NOTSET)

    if "FLAVOUR" in os.environ.keys():
        parameters["Command flavour"] = os.environ["FLAVOUR"].lower()
    if "STRFILE_FLAVOUR" in os.environ.keys():
        parameters["Command flavour"] = os.environ["STRFILE_FLAVOUR"].lower()
    if "UNSTR_FLAVOUR" in os.environ.keys():
        parameters["Command flavour"] = os.environ["STRFILE_FLAVOUR"].lower()

    logging.debug("process_environment_variables(): parameters:")
    logging.debug(parameters)


################################################################################
def process_command_line():
    """Process command line options"""
    # pylint: disable=C0103
    global parameters
    # pylint: enable=C0103

    # option letters followed by : expect an argument
    # same for option strings followed by =
    character_options = "Cc:iorsx?"
    string_options = [
        "debug",
        "help",
        "version",
    ]

    try:
        options, remaining_arguments = getopt.getopt(
            sys.argv[1:], character_options, string_options
        )
    except getopt.GetoptError as error:
        logging.critical("Syntax error: %s", error)
        display_help()
        sys.exit(1)

    for option, argument in options:

        if option == "--debug":
            logging.disable(logging.NOTSET)

        elif option in ("--help", "-?"):
            display_help()
            sys.exit(0)

        elif option == "--version":
            print(ID.replace("@(" + "#)" + " $" + "Id" + ": ", "").replace(" $", ""))
            sys.exit(0)

        elif option == "-C":
            parameters["Has comments"] = True

        elif option == "-c":
            if len(argument) > 1:
                logging.critical("Option -c argument must be a single character")
                sys.exit(1)
            else:
                parameters["Delimiting char"] = argument

        elif option == "-i":
            parameters["Ignore case"] = True

        elif option == "-o":
            parameters["Alphabetical order"] = True
            parameters["Randomize access"] = False

        elif option == "-r":
            if not parameters["Alphabetical order"]:
                parameters["Randomize access"] = True

        elif option == "-s":
            parameters["Run silently"] = True

        elif option == "-x":
            parameters["Is rotated"] = True

    logging.debug("process_command_line(): parameters:")
    logging.debug(parameters)
    logging.debug("process_command_line(): remaining_arguments:")
    logging.debug(remaining_arguments)

    return remaining_arguments


################################################################################
def strfile(source_file, output_file):
    """strfile command behaviour"""
    number_of_strings = 0
    offsets = [ 0 ]
    lines = [ ]
    longest_length = 0
    shortest_length = sys.maxsize
    last_offset = 0
    current_offset = 0
    current_line = ""
    current_length = 0

    file_content = None
    with open(source_file, "r") as file:
        file_content = file.readlines()

    for line in file_content:
        line_length = len(line)
        current_offset += line_length
        if line == parameters["Delimiting char"] + os.linesep:
            number_of_strings += 1

            if current_length > longest_length:
                longest_length = current_length
            if current_length < shortest_length:
                shortest_length = current_length

            offsets.append(current_offset)
            current_line = re.sub(r"^[^A-Za-z]+", "", current_line)
            lines.append([current_line, last_offset])

            last_offset = current_offset
            current_length = 0
            current_line = ""
        else:
            current_length += line_length
            if parameters["Ignore case"]:
                current_line += line.lower()
            else:
                current_line += line

    # like in the original command, -o has precedence over -r if both are used:
    if parameters["Alphabetical order"]:
        lines = sorted(lines, key=lambda lines:lines[0])
    elif parameters["Randomize access"]:
        random.shuffle(lines)

    try:
        with open(output_file, "wb") as file:
            # header / version number as unsigned 32bits int:
            file.write(struct.pack("!I", STR_VERSION))

            # header / number of strings in the file as unsigned 32bits int:
            file.write(struct.pack("!I", number_of_strings))

            # header / length of longest string as unsigned 32bits int:
            file.write(struct.pack("!I", longest_length))

            # header / length of shortest string as unsigned 32bits int:
            file.write(struct.pack("!I", shortest_length))

            # header / flags as unsigned 32bits int:
            flags = 0
            if parameters["Randomize access"]:
                flags += STR_RANDOM
            if parameters["Alphabetical order"]:
                flags += STR_ORDERED
            if parameters["Is rotated"]:
                flags += STR_ROTATED
            if parameters["Has comments"]:
                flags += STR_COMMENTS
            file.write(struct.pack("!I", flags))

            # header / delimiting character as char with 3 padding bytes:
            file.write(struct.pack("!c", parameters["Delimiting char"].encode('ASCII')))
            file.write(struct.pack("!x"))
            file.write(struct.pack("!x"))
            file.write(struct.pack("!x"))

            # body / table of file offsets as unsigned 64bits int:
            for line in lines:
                file.write(struct.pack("!Q", line[1]))
            file.write(struct.pack("!Q", offsets[-1]))
    except PermissionError:
        print(output_file + ": Permission denied", file=sys.stderr)
        sys.exit(1)

    if not parameters["Run silently"]:
        print('"{}.dat" created'.format(source_file))
        if number_of_strings == 1:
            print("There was 1 string")
        else:
            print("There were {} strings".format(number_of_strings))
        plural = "s"
        if longest_length == 1:
            plural = ""
        print("Longest string: {} byte{}".format(longest_length, plural))
        plural = "s"
        if shortest_length == 1:
            plural = ""
        print("Shortest string: {} byte{}".format(shortest_length, plural))
        logging.debug("Offsets:")
        logging.debug(offsets)
        logging.debug("%d lines:", len(lines))
        logging.debug(lines)


################################################################################
def read_strfile_header(datafile):
    """Returns a dictionnary with the strfile's header contents"""

    if not os.path.isfile(datafile + ".dat"):
        return None

    version = ""
    number_of_strings = 0
    longest_length = 0
    shortest_length = 0
    flags = 0
    flag_random = 0
    flag_ordered = 0
    flag_rotated = 0
    flag_comments = 0
    delimiting_character = "%"

    with open(datafile + ".dat", "rb") as file:
        # header / version number as unsigned 32bits int:
        version = struct.unpack("!I", file.read(4))[0]

        # header / number of strings in the file as unsigned 32bits int:
        number_of_strings = struct.unpack("!I", file.read(4))[0]

        # header / length of longest string as unsigned 32bits int:
        longest_length = struct.unpack("!I", file.read(4))[0]

        # header / length of shortest string as unsigned 32bits int:
        shortest_length = struct.unpack("!I", file.read(4))[0]

        # header / flags as unsigned 32bits int:
        flags = struct.unpack("!I", file.read(4))[0]
        flag_random = flags & STR_RANDOM == STR_RANDOM
        flag_ordered = flags & STR_ORDERED == STR_ORDERED
        flag_rotated = flags & STR_ROTATED == STR_ROTATED
        flag_comments = flags & STR_COMMENTS == STR_COMMENTS

        # header / delimiting character as char with 3 padding bytes:
        delimiting_character = struct.unpack("!c", file.read(1))[0]
        delimiting_character = delimiting_character.decode("utf-8", "replace")
        #file.read(3)

    logging.debug("datafile=%s", datafile + ".dat")
    logging.debug("version=%d", version)
    logging.debug("number_of_strings=%d", number_of_strings)
    logging.debug("longest_length=%d", longest_length)
    logging.debug("shortest_length=%d", shortest_length)
    logging.debug("flags=%d", flags)
    logging.debug("flag_random=%r", flag_random)
    logging.debug("flag_ordered=%r", flag_ordered)
    logging.debug("flag_rotated=%r", flag_rotated)
    logging.debug("flag_comments=%r", flag_comments)
    logging.debug("delimiting_character=%s", delimiting_character)

    return {
        "version": version,
        "number of strings": number_of_strings,
        "longest length": longest_length,
        "shortest length": shortest_length,
        "random flag": flag_random,
        "ordered flag": flag_ordered,
        "rotated flag": flag_rotated,
        "comments flag": flag_comments,
        "delimiting char": delimiting_character,
        }


################################################################################
def read_strfile_body(datafile, number_of_strings):
    """Returns a dictionnary with the strfile's body contents"""

    if not os.path.isfile(datafile + ".dat"):
        return None

    offsets = []

    with open(datafile + ".dat", "rb") as file:
        file.seek(4 * 6)

        # body / table of file offsets as unsigned 64bits int:
        for _ in range(number_of_strings + 1):
            offsets.append(struct.unpack("!Q", file.read(8))[0])

    logging.debug("datafile=%s", datafile + ".dat")
    logging.debug("offsets:")
    logging.debug(offsets)

    return offsets


################################################################################
def get_file_linesep(file):
    """Return the line separator used in a file"""
    try:
        while true:
            character = file.read(1)
            character = character.decode("utf-8", "replace")

            if character == '\r':
                return "\r\n"

            if character == '\n':
                return "\n"
    except:
        return "\n"


################################################################################
def read_fortune(datafile, offset, delimiting_character):
    """Returns the fortune at datafile/offset"""

    if not os.path.isfile(datafile):
        return None

    with open(datafile, "rb") as file:
        # We can't rely on the local os.linesep because the data file may have been generated
        # on a platform where its value is different
        file_linesep = get_file_linesep(file)

        file.seek(offset)

        line = ""
        in_end_of_line = False
        new_line = True
        in_delimiting_character = False
        end_of_string = False

        while not end_of_string:
            character = file.read(1)
            character = character.decode("utf-8", "replace")

            if not character:
                end_of_string = True

            if in_end_of_line:
                in_end_of_line = False
                if character == file_linesep[1]:
                    new_line = True
                    if in_delimiting_character:
                        in_delimiting_character = False
                        end_of_string = True
                    else:
                        line += file_linesep
                    continue
                in_delimiting_character = False
                line += file_linesep[0] + character

            if character == file_linesep[0]:
                if len(file_linesep) == 1:
                    new_line = True
                    if in_delimiting_character:
                        in_delimiting_character = False
                        end_of_string = True
                    else:
                        line += character
                else:
                    in_end_of_line = True

            elif character == delimiting_character:
                if new_line:
                    in_delimiting_character = True
                    new_line = False
                elif in_delimiting_character:
                    # in comment
                    in_delimiting_character = False
                    line += character + character
                else:
                    line += character

            else:
                line += character
                new_line = False

        return line


################################################################################
def unstr(datafile):
    """unstr command behaviour"""
    header = read_strfile_header(datafile)
    offsets = read_strfile_body(datafile, header["number of strings"])

    if not header["random flag"] and not header["ordered flag"]:
        print("unstr: nothing to do -- table in file order", file=sys.stderr)
        sys.exit(1)

    for i in range(header["number of strings"]):
        fortune = read_fortune(datafile, offsets[i], header["delimiting char"])
        print(fortune + header["delimiting char"])


################################################################################
def main():
    """The program's main entry point"""
    program_name = os.path.basename(sys.argv[0])
    if program_name != "strfile":
        parameters["Unstr"] = True

    console_log_format = program_name + ": %(levelname)s: %(message)s"
    logging.basicConfig(format=console_log_format, level=logging.DEBUG)
    logging.disable(logging.INFO)

    process_environment_variables()
    arguments = process_command_line()

    # unstr behaviour:
    if parameters["Unstr"]:
        if len(arguments) != 1:
            display_unstr_usage()
            sys.exit(1)

        if not os.path.isfile(arguments[0]):
            print("unstr: " + arguments[0] + ": No such file or directory", file=sys.stderr)
            sys.exit(1)
        if not os.path.isfile(arguments[0] + ".dat"):
            print("unstr: " + arguments[0] + ".dat: No such file or directory", file=sys.stderr)
            sys.exit(1)

        unstr(arguments[0])

    # strfile behaviour:
    else:
        if len(arguments) == 0:
            print("No input file name")
            display_strfile_usage()
            sys.exit(1)

        if os.path.isfile(arguments[0]):
            output_file = ""
            if len(arguments) == 2:
                output_file = arguments[1]
            else:
                output_file = arguments[0] + ".dat"
            strfile(arguments[0], output_file)
        else:
            print(arguments[0] + ": No such file or directory", file=sys.stderr)
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
