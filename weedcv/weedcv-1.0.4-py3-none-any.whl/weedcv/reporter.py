"""
Reporter adapted from:
https://github.com/navarasu/opencv-log/blob/master/cvtest/reporter.py
"""

import os
import traceback
from pathlib import Path
from uuid import uuid4

import cv2
from cvlog import log

from weedcv.weedcv import params
from weedcv.weedcv.csv_reporter import CsvReporter


class Reporter:
    def __new__(cls):
        if not hasattr(cls, "instance") or not cls.instance:
            cls.instance = super().__new__(cls)
            cls.instance.__initialised = False
        return cls.instance

    def __init__(self):
        if not self.__initialised:
            self.__initialised = True
            report_path = Path(params.log_path) / "report"
            self.image_path = report_path / "images"
            self.reporter = CsvReporter(str(report_path / "report.csv"))

    def result(self, input_image, key_pressed, output_img):
        message = ""
        if key_pressed == ord("y"):
            result = "Pass"
        else:
            result = "Fail"
            message = self.__save_image(output_img)
        self.reporter.log_report([input_image, result.upper(), message])

    def __save_image(self, img):
        self.image_path.mkdir(parents=True, exist_ok=True)
        output_path = str(self.image_path / str(uuid4())) + ".png"
        cv2.imwrite(output_path, img)
        return output_path

    def error(self, input_image, ex):
        self.reporter.log_report([input_image, "ERROR", self.__stack_trace(ex)])

    def __stack_trace(self, ex):
        stacks = traceback.extract_tb(ex.__traceback__)[1:]
        stack_trace = ""
        for x in stacks[:10]:
            stack_trace += x.filename + ":" + str(x.lineno) + ";"
        return stack_trace


# def report(input_image_path, processing_method):
def report(input_image_path, processing_method):

    for image_path in input_image_path:
        results = processing_method(str(image_path))
        if isinstance(results, list):
            for proc_result in results:
                key_pressed = log.show_image(
                    str(image_path), "log_type", proc_result, None
                )
                Reporter().result(image_path, key_pressed, proc_result)
        else:
            key_pressed = log.show_image(str(image_path), "log_type", results, None)

            Reporter().result(image_path, key_pressed, results)
