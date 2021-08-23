import logging
import os
import datetime
import hashlib
import random

COUNTER_STREAM = "stream"

class CleanLogger:

    def __init__(
        self, 
        name, 
        streamhandler_level = logging.INFO,
        formatter = logging.Formatter('%(asctime)s -- %(levelname)8s -- %(name)s -- %(message)s', datefmt="%Y-%m-%dT%H:%M:%S%z"),
        max_history = 100,
    ):
        self._name = self.__create_clean_name(name)
        log = logging.getLogger(self._name)
        log.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(streamhandler_level)
        ch.setFormatter(formatter)

        log.addHandler(ch)

        self._log = log
        self._formatter = formatter
        self._fileloggers = {}

        self._counters = {
            COUNTER_STREAM : {}
        }

        self._history = []
        self._max_history = max_history

    def log(self):
        return self._log

    def get_name(self):
        return self._name

    def log_message(self, level, message):
        self.__count(level)
        self._history.append((
            datetime.datetime.now().isoformat(),
            level,
            self._name,
            message,
        ))
        if len(self._history) > self._max_history:
            self._history = self._history[max(0, len(self._history) - self._max_history):]
        self._log.log(level, message)

    def debug(self, msg):
        self.log_message(logging.DEBUG, msg)

    def info(self, msg):
        self.log_message(logging.INFO, msg)

    def warning(self, msg):
        self.log_message(logging.WARNING, msg)

    def error(self, msg):
        self.log_message(logging.ERROR, msg)

    def critical(self, msg):
        self.log_message(logging.CRITICAL, msg)

    def exception(self, msg):
        self.__count(logging.ERROR)
        self._log.exception(msg)

    def add_filelogger(self, filename, loglevel = logging.DEBUG, append = False):
        self.add_message_counter(filename)
        self._log.info("Registering log file '{}' ...".format(filename))
        folder = os.path.dirname(filename)
        if folder and not os.path.exists(folder):
            self._log.debug("Creating directory '{}' ...".format(folder))
            try:
                os.makedirs(folder)
            except:
                self._log.error("Cannot create folder '{fol}'. I skip adding a log file {f}.".format(fol=folder, f=filename))
                return

        fh = logging.FileHandler(filename, mode='a' if append else 'w')
        fh.setLevel(loglevel)
        fh.setFormatter(self._formatter)

        self._log.addHandler(fh)
        self._fileloggers[filename] = fh

    def remove_filelogger(self, filename):
        self._log.info("Unregistering log file '{}' ...".format(filename))
        if not filename in self._fileloggers.keys():
            self._log.info("Log file '{}' is not registered. I skip this.".format(filename))
            return

        self._log.removeHandler(self._fileloggers[filename])
        del(self._fileloggers[filename])
        self.remove_message_counter(filename)

    def get_message_count(self, countername = COUNTER_STREAM, level = logging.INFO, include_worse = True):
        if countername in self._counters.keys():
            if not include_worse:
                if level in self._counters[countername].keys():
                    return self._counters[countername][level]
            else:
                c = 0
                for count_level in range(level, logging.CRITICAL+1):
                    if count_level in self._counters[countername].keys():
                        c += self._counters[countername][count_level]
                return c
        return 0

    def add_message_counter(self, countername):
        self._counters[countername] = {}

    def remove_message_counter(self, countername):
        if countername in self._counters.keys():
            del(self._counters[countername])

    def create_foldername_for_now_short(self):
        """Gets a string representing today and the current time to the second, usable in folder names."""
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        return now

    def create_foldername_for_now_isoformat_stripped(self):
        """Gets a string representing today and the current time to the second, in ISO format, but usable in folder names."""
        now = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
        now = now.replace(":", "").replace(".", "")
        return now
        
    def get_message_history(self, max_num = 10, level_filter = None):
        filtered_history = [
            (ts, level, name, msg)
            for (ts, level, name, msg) in self._history
            if level_filter == None or level_filter == level
        ]
        return filtered_history[max(0, len(filtered_history) - max_num):]

    def __count(self, loglevel):
        for counter in self._counters.values():
            if not loglevel in counter.keys():
                counter[loglevel] = 1
                continue
            counter[loglevel] += 1

    def __create_clean_name(self, name):
        if not name:
            random_string = str(random.random())
            random_hash = hashlib.md5(random_string.encode()).hexdigest()
            return "Logger-{}".format(random_hash)
        return name