#############################################################################
##                               Splive                                    ##
#############################################################################
# Command line tool to append several csv files together into one large file.
# Mainly used to concat several daily logfiles into one for better 
# visualization

import os
import sys
import argparse
import glob


#############################################################################
##                           Global constants                              ##
#############################################################################
#CLIENT_ID = ""  # The ID of this app for authorization


#############################################################################
##                           Global variables                              ##
#############################################################################
auto_accept_mode    = False
input_path          = ""
output_path         = ""
output_file         = ""

#############################################################################
##                               Helpers                                   ##
#############################################################################

def argset():
    """
    Sets command line arguments
    """
    global input_path
    global output_path
    global output_file
    global auto_accept_mode

    parser = argparse.ArgumentParser(description=
                     "Easily splice several CSV files together")

    # Input path
    parser.add_argument('input_path', nargs='?', 
        default=os.getcwd(), 
        help="""
            Path to input CSVs. Will use current directory if ommited
            """)

    # Output path
    parser.add_argument('output_file', nargs='?', 
        default=os.getcwd()+"/Spliced.csv", 
        help="""
            Path and filename of output CSV. Will use 
            <CurrentDirectory>/Spliced.csv as default
            """)

    # Parse args
    args = parser.parse_args()
    input_path  = args.input_path
    output_file = args.output_file
    output_path = os.path.dirname(output_file)

    # Output recognized args
    print("Using input path:")
    print(input_path)
    print("Using output path:")
    print(output_path)
    print("Using output file:")
    print(output_file)
    print("---")

    # Argument sanity checks
    if not os.path.isdir(input_path):
        print("The input path specified does not exist, exiting")
        sys.exit(os.EX_USAGE)
    if not os.path.isdir(output_path):
        print("The output path specified does not exist, exiting")
        sys.exit(os.EX_USAGE)
    if not ".csv" in output_file:
        print("Please specify a file path for output_file instead of a directory")
        print("Hint: my/output/path/spliced.csv, not my/output/path")
        sys.exit(os.EX_USAGE)


def read_file_list(input_path):
    """
    Read in files from input_path 
    """
    file_path_list = glob.glob(input_path + "/*.csv")

    return(file_path_list)


def splice_files(file_path_list, output_file):
    """
    Splices together all found csv files from input_path to output_path
    """
    # Create new spliced file, containing header
    with open(output_file, "w") as outfile:
        with open(file_path_list[0], "r") as infile:
            # Get only first line from input file
            line = infile.readline()

            # if line is empty
            if not line:
                sys.exit(1)

            outfile.write(line)

    # Append all lines of all found files individually to just created file
    with open(output_file, "a") as outfile:
        for file in file_path_list:

            if file != output_file:

                with open(file, "r") as infile:
                    count = 0
                    while True:
                        # Get individual lines from opened input file
                        line = infile.readline()

                        # If line is empty, end of file is reached, go to next file
                        if not line:
                            break
                        
                        if count > 0:
                            outfile.write(line)

                        count += 1

        print("All files spliced")
        print("---")


#############################################################################
##                               main()                                    ##
#############################################################################
def main():
    print("--------------------")
    print("--Starting  Splive--")
    print("--------------------")

    # Set command line arguments
    argset()

    # Read in file list
    file_path_list = read_file_list(input_path)

    # Sort files automatically for now, later allow interactive sorting
    file_path_list.sort()

    # Check if files were found
    if not file_path_list:
        print("No valid files found at input_path")
        sys.exit(os.EX_USAGE)

    # Output file list
    print("Found the following files: ")
    for file in file_path_list:
        print(file)
    print("---")

    # Create spliced file
    splice_files(file_path_list, output_file)


#############################################################################
##                         main() idiom                                    ##
#############################################################################
if __name__ == "__main__":
    main()