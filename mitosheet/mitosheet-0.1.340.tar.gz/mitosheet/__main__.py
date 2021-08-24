"""
The main entry point for the mitosheet package, this command
line interface allows you to set some toggles in the user.json
"""
from mitosheet.user.db import set_user_field
import sys
from mitosheet.user import initialize_user
from mitosheet.user.schemas import UJ_MITOSHEET_TELEMETRY, UJ_USER_EMAIL

def main():
    """
    Currently, the main usage of this function is:
    python -m mitosheet turnofflogging
    python -m mitosheet turnonlogging

    We also have 
    python -m mitosheet clearemail
    """
    # Make sure the user is initalized first, but do not identify
    # then, in case they are turning off logging
    initialize_user(identify=False)

    # Then, if we are being told to turn off logging, turn off logging
    if len(sys.argv) > 1:
        if sys.argv[-1] == 'turnofflogging':
            print("Turning off all logging")
            set_user_field(UJ_MITOSHEET_TELEMETRY, False)
            print("Logging turned off!")
        if sys.argv[-1] == 'turnonlogging':
            print("Turning on all logging")
            set_user_field(UJ_MITOSHEET_TELEMETRY, True)
            print("Logging turned on!")
        if sys.argv[-1] == 'clearemail':
            print("Clearing email")
            set_user_field(UJ_USER_EMAIL, '')
            print("Email cleared")


if __name__ == '__main__':
    main()