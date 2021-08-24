import os
import json
import time


class LogBase:
    """
    Log base class. LogWriter and LogReader inherit from this class.
    """

    def __init__(self, folder: str = "./", filename: str = "log.json"):
        self.path = folder + filename

    def assert_file_exists(self):
        """
        Throw error if the logfile does not exist.
        :return: None
        """
        if not os.path.exists(self.path):
            raise Exception(f"The file {self.path} does not exist.")

    def create_file(self):
        """
        Create the logfile if it does not exist yet.
        :return: None
        """
        if not os.path.exists(self.path):
            open(self.path, "w")

    def reset(self):
        """
        Clear contents of logfile.
        :return: None
        """
        self.assert_file_exists()
        open(self.path, "w+").close()

    def remove(self):
        """
        Remove the logfile.
        :return: None
        """
        self.assert_file_exists()
        os.remove(self.path)


class LogWriter(LogBase):
    """
    LogWriter for writing contents to the logfiles.
    """

    def __init__(self, folder: str = "./", filename: str = "log.json", threshold: int = 16):
        LogBase.__init__(self, folder, filename)
        self.log_buffer = []  # buffer of all logs before being written to file
        self.threshold = threshold  # threshold before writing to file
        # create the log file if not yet exists
        self.create_file()

    @staticmethod
    def with_datetime(folder: str = "./", threshold: int = 16):
        """
        Create logfile with filename the datetime.
        :param folder: the folder name
        :param threshold: the threshold of the buffer
        :return: LogWriter
        """
        return LogWriter(folder, f"{str(int(time.time()))}.json", threshold)

    def log(self, data):
        """
        Log a single data entity to the logfile.
        :param data: any kind of data you want to store (in json format)
        :return: None
        """
        self.log_buffer.append(data)
        if len(self.log_buffer) >= self.threshold:
            # write all data to file and flush buffer
            self.flush()

    def flush(self):
        """
        If needed, flush the buffer and make sure everything is written to the logfile.
        :return: None
        """
        if len(self.log_buffer) == 0:
            return

        # get length of file
        with open(self.path, "a+") as file:
            file.seek(0, os.SEEK_END)
            length = file.tell()

        # remove last \n] from json file
        with open(self.path, "r+") as file:

            while length > 0 and file.read(1) != "]":
                length -= 1
                file.seek(length, os.SEEK_SET)

            # also remove newline for prettiness
            if length > 0:
                length -= 1

            if length > 0:
                file.seek(length, os.SEEK_SET)
                file.truncate()

        with open(self.path, "a+") as file:
            if length == 0:
                # start json file
                file.write("[\n")
            if length > 0:
                # set ',' for previously added entry
                file.write(",\n")
            # write new entries
            file.write(",\n".join([json.dumps(el) for el in self.log_buffer]))
            # always close file to have correct json syntax
            file.write("\n]\n")

        self.log_buffer = []


class LogReader(LogBase):
    """
    LogReader for reading contents from the logfiles.
    """

    def __init__(self, folder: str = "./", filename: str = "log.json"):
        LogBase.__init__(self, folder, filename)
        self.assert_file_exists()

    def retrieve(self):
        """
        Retrieve all the content of the logfile.
        :return: list of all rows in logfile
        """
        self.assert_file_exists()
        with open(self.path, "r+") as file:
            file.seek(0, os.SEEK_END)
            pos = file.tell()

            if pos <= 0:
                return []

            # return to start to read file
            file.seek(0)
            return json.load(file)
