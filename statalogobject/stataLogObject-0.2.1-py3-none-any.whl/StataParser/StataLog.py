from stataLogObject.StataParser import StataRaw, StataTable
from stataLogObject.Configs import TableConfigs, Table

from pathlib import Path


class StataLog:
    def __init__(self, log_path):

        # Set the log path, validate it exists, and that it is .log
        self.log_path = Path(log_path)
        assert self.log_path.exists(), "Path to .log is invalid"
        assert self.log_path.suffix == ".log", "File is not a log, as it lacks a .log file extension"

        # Set the config object for known table types
        self.config = TableConfigs()

        # Create lists of table objects for each object in the self.config
        self.ols = self.create_tables(self.config.ols)
        self.ols_clu = self.create_tables(self.config.ols_clu)
        self.hdfe = self.create_tables(self.config.hdfe)

        # Panel variables
        self.fe_within = self.create_tables(self.config.fe_within)
        # TODO: Random-effects

        # Mixed
        self.mixed = self.create_tables(self.config.mixed)

        # Summary
        self.summary = self.create_tables(self.config.summary)
        self.tabulate = self.create_tables(self.config.tabulate)

    def create_tables(self, config):
        """
        For a Given configuration, isolate the raw table then format it to StataTable Generic

        :param config: The configuration Table Object for this log table that we wish to isolate
        :type config: Table
        """
        return [StataTable(table, config) for table in StataRaw(self.log_path, config.table_ext).raw_tables]

    def censure_log(self):
        """
        Logs from stata often contain a path which can be problematic if they are to sensitive locations so this
        censures them.

        :return: Nothing, override the log file
        :rtype: None
        """

        # Remove the path to log: locations
        log_raw = []
        with open(self.log_path, "r") as log_file:
            for line in log_file:
                if "log:" in line:
                    log_raw.append(f"{line.split(':')[0]}: \n")
                else:
                    log_raw.append(line)

        # Override the file
        with open(self.log_path, "w") as log_file:
            for line in log_raw:
                log_file.write(line)
