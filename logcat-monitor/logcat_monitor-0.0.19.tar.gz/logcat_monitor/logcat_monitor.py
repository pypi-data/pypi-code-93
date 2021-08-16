#!/usr/bin/env python
# -*- coding: utf-8 -*-
# --------------------------------------------------------------
# ProjectName: Logcat Monitor
# Author: gentliu
# CreateTime: 30/7/2021 5:09 PM
# File Name: LogcatMonitor
# Description:
#   This is a tool class for use cases to find exception information in logcat in real time
# --------------------------------------------------------------

# Configure keywords to be monitored
import json
import os
import subprocess
import time
from datetime import datetime

from logcat_monitor.threadpool import ThreadPool

KEYWORDS_DICT = {"ANR in ": "Anr",
                 "FATAL EXCEPTION:": "Fatal",
                 "signal 6": "Signal6",
                 "signal 7": "Signal7",
                 "signal 11": "Signal11",
                 "CRASH: ": "Crash",
                 "Force Closed": "ForceClose"}

INTERCEPTED_MAX_ROWS = 100

LOG_FOLDER_NAME = "logcats"


class Statistics:
    def increase(self, key_dict, key):
        """
            Increase the number of error
        :param key_dict:
        :param key:
        :return:
        """
        if key in key_dict:
            attr = key_dict[key]
            count = getattr(self, attr, 0)
            target = count + 1
            setattr(self, attr, target)
            print("Count [%s] curent:%d target:%d" % (key, count, target))


class LogcatMonitor:
    # Control on and off
    _stop_logcat = True
    # logs buffer
    _logs = []
    _key_dict = KEYWORDS_DICT
    _pool = ThreadPool(1)

    def __init__(self, serial_number=None, parent_folder=None, key_dict=None, rows=INTERCEPTED_MAX_ROWS):
        if key_dict is not None:
            for key in key_dict:
                self._key_dict[key] = (key_dict[key])
        self._rows = rows
        # Create folder
        if parent_folder is None:
            self._self_folder = os.getcwd() + os.sep + LOG_FOLDER_NAME
        else:
            self._self_folder = parent_folder + os.sep + LOG_FOLDER_NAME
        if not os.path.isdir(self._self_folder):
            os.makedirs(self._self_folder)
        # Store serial number
        self._serial_number = serial_number
        # Statistics
        self._statistics = Statistics()

    def start_monitor(self):
        """
            Start logcat monitor
        :return:
        """
        self._stop_logcat = False
        print("Start monitor _logcat")
        self._pool.add_task(self._filter_keyword)

    def stop_monitor(self):
        """
            Stop logcat monitor
        :return:
        """
        if self._stop_logcat:
            print("There are no tasks in progress")
        else:
            # Save statistics
            self._save_statistics()
            print("Stopping monitor\n")
            self._stop_logcat = True
            time.sleep(5)
            self._pool.destroy()
            time.sleep(3)
            print("Pool destroy")

    def filter_file(self, file_name):
        intercept = False
        rows = 0
        keys = self._key_dict.keys()
        find_key = None
        line_count = 0
        with open(file_name, 'r', encoding='utf-8') as log_file:
            line = log_file.readline()
            while line:
                line_count = line_count + 1
                if not intercept:
                    # Read data normally
                    for key in keys:
                        if line.find(key) != -1:
                            message = "Detected：%s\n" % key
                            print(message)
                            self._logs.clear()
                            intercept = True
                            self._logs.append(line)
                            rows = 1
                            find_key = key
                else:
                    # An error has been detected.
                    # Read the subsequent qualified logs
                    if rows < self._rows:
                        # Add the current line to the logs
                        self._logs.append(line)
                        rows = rows + 1
                    else:
                        # Finished reading the required logs
                        intercept = False
                        rows = 0
                        # Increase error counter
                        self._statistics.increase(self._key_dict, find_key)
                        # Save as a file
                        self._save_file(find_key, self._logs)
                line = log_file.readline()
        # Save statistics
        self._save_statistics()

    def _filter_keyword(self):
        """
            Keep reading logcat output, find error information.
            Count the number and write relevant information to the file
        :return:
        """
        print("Start monitor _logcat")
        # Initializing local variables
        self._logcat_clear()
        intercept = False
        rows = 0
        keys = self._key_dict.keys()
        find_key = None
        # File storage location(file full path)
        print("####### STRAT LOGCAT WRITE #######")
        logcat_file_name = "%s%slogcat.txt" % (self._self_folder, os.sep)
        line_count = 0
        with open(logcat_file_name, 'w', encoding='utf-8') as log_file:
            while not self._stop_logcat:
                print("Get logcat")
                # Keep reading data
                with self._logcat() as sub:
                    for line in sub.stdout:
                        # Whether stop reading logcat
                        if self._stop_logcat:
                            # Normal termination
                            # Stop
                            print("####### STOP LOGCAT #######")
                            break
                        line_count = line_count + 1
                        # if line_count % 100 == 0:
                        #     print("####### Line:%d #######" % line_count)
                        try:
                            line_str = line.decode("utf-8")
                        except Exception as ex:
                            print(ex)
                            line_str = str(ex)
                        log_file.write(line_str)
                        if not intercept:
                            # Read data normally
                            for key in keys:
                                if line_str.find(key) != -1:
                                    message = "Detected：%s\n" % key
                                    print(message)
                                    self._logs.clear()
                                    intercept = True
                                    self._logs.append(line_str)
                                    rows = 1
                                    find_key = key
                        else:
                            # An error has been detected.
                            # Read the subsequent qualified logs
                            if rows < self._rows:
                                # Add the current line to the logs
                                self._logs.append(line_str)
                                rows = rows + 1
                            else:
                                # Finished reading the required logs
                                intercept = False
                                rows = 0
                                # Increase error counter
                                self._statistics.increase(self._key_dict, find_key)
                                # Save as a file
                                self._save_file(find_key, self._logs)
                    print("End monitor _logcat")
                    sub.kill()
                    if not self._stop_logcat:
                        # Abnormal termination
                        # wait...
                        time.sleep(2)
        print("####### END LOGCAT WRITE #######")

    def _logcat_clear(self):
        """
            Clear logcat
        :return:
        """
        if self._serial_number is not None and self._serial_number != "":
            cmd = "adb -s " + self._serial_number + " logcat -c"
        else:
            cmd = "adb logcat  -c"
        subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE)

    def _logcat(self):
        """
            _logcat continuously outputs logs
        :return:
        """
        if self._serial_number is not None and self._serial_number != "":
            cmd = "adb -s " + self._serial_number + " logcat -v time"
        else:
            cmd = "adb logcat -v time"
        sub = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE)
        return sub

    def _save_file(self, key, logs):
        """
            Save logs to file by key
        :param key:
        :param logs:
        :return:
        """
        if key is None:
            return
        # Key should in self._key_dict
        if key in self._key_dict:
            prefix = self._key_dict[key]
            # File storage location(file full path)
            file_name = "%s%s%s_%s.txt" % (self._self_folder, os.sep, prefix, datetime.now().strftime("%Y%m%d%H%M%S%f"))
            # Save to file
            # log is bytes, so mode set to wb
            with open(file_name, mode="w", encoding='utf-8') as f:
                for log in logs:
                    f.write(log)

    def _save_statistics(self):
        """
            Save the counted number of errors to the file statistics.txt
        :return:
        """
        # File storage location(file full path)
        file_name = "%s%sstatistics.txt" % (self._self_folder, os.sep)
        # Convert self._statistics to json
        json_content = json.dumps(self._statistics.__dict__, ensure_ascii=False)
        # Save to file
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(json_content)
