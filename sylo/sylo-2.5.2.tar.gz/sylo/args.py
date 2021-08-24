import argparse


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Sort Your Life Out! Python Pomodoro Timer"
    )
    parser.add_argument("-w", "--work_time", help="Set the work time length", type=int)
    parser.add_argument("-r", "--rest_time", help="Set the rest time length", type=int)
    parser.add_argument(
        "-a",
        "--audio_file",
        help="""Set the full path to an audio \
        file you want to be played on completion of a timer""",
        type=str,
    )
    parser.add_argument(
        "-l",
        "--log",
        help="Set the log level",
        type=str,
        choices=[
            "DEBUG",
            "INFO",
        ],
    )
    parser.add_argument("-s", "--speed_mode", dest="speed_mode", action="store_true")
    parser.add_argument(
        "-t",
        "--theme",
        help="Set the color scheme",
        type=str,
        choices=[
            "blue",
            "red",
            "green",
            "lblue",
            "lred",
            "lgreen",
            "magenta",
            "yellow",
            "white",
            "black",
            "rainbow",
        ],
    )
    parser.set_defaults(speed_mode=False)
    return parser.parse_args()
