import logging
from datetime import datetime
from dotenv import load_dotenv
import os
import glob


class Logger:
    def __init__(self):
        # Load envs
        load_dotenv()

        # Create missing directories
        if not os.path.exists("logs"):
            os.makedirs("logs")

        FORMAT = "%(asctime)-10s | %(levelname)s | %(message)s"

        log_file = "./logs/" + (datetime.today()).strftime("%Y-%m-%d") + ".log"
        logging.basicConfig(filename=log_file, format=FORMAT, level=logging.INFO)

    def get_logs(last_log: bool, output: bool) -> None:
        if last_log:
            list_of_files = glob.glob("./logs/*.log")
            list_of_files_not_empty = list(
                filter(lambda x: os.path.getsize(x) > 0, list_of_files)
            )  # Remove all empty files

            if list_of_files_not_empty == []:
                print("No logs yet")
                return None

            latest_file = max(
                list_of_files_not_empty, key=os.path.getctime
            )  # List the last log by creation date

            if output:
                with open(latest_file, "r") as file:
                    print(file.read())  # Output to stdout
            else:
                os.system(f"open {latest_file}")  # Open directory
        else:
            os.system("open logs")
