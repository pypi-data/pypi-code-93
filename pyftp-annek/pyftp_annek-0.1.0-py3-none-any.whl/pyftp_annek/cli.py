""" Core module with CLI """
import os
import click
import ftplib
from pprint import pprint

@click.group()
def main():
    """
    PyFTP is a cli wrapper for ftplib module in Python

    Format: pyftp command server file-to-upload username password

    Example: pyftp ascii-upload ftp.example.com file-with-path \\
            destination-filename ftpuser password
    """

@main.command()
@click.option("--helptext", is_flag=True, help="Print extra help")
def more_help(helptext):
    """ Various help options for usage information """
    result = "Use --help to view usage"
    if helptext:
        result = print_more_help()
    print(result)


@main.command('ascii-upload', short_help="Upload a file to an FTP server with storlines")
@click.argument('server-name')
@click.argument('file-with-path', type=click.Path(exists=True))
@click.argument('destination-filename')
@click.argument('ftp-username')
@click.argument('ftp-password')
def upload(server_name, file_with_path, destination_filename, ftp_username, ftp_password):
    """ Uses the ftplib module to upload a file as ascii """
    ftp = ftplib.FTP(server_name, ftp_username, ftp_password)
    put_command = 'STOR ' + destination_filename
    with open(file_with_path, 'rb') as file:
        ftp.storlines(put_command, file)
    result = ftp.dir(destination_filename)
    ftp.close()
    pprint(result)
    return result


def print_more_help():
    """ Prints help message """
    help_text = """
    This is more help TODO

    """
    return help_text


if __name__ == "__main__":
    main()

