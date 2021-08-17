# -*- coding:utf-8 -*-
from __future__ import print_function
import RPi.GPIO as GPIO
import threading
import time


class Motor(object):
    def __init__(self):
        self.INT3 = 16
        self.INT4 = 20
        self.ENB = 21

    def _move_forward_(self, duration, backforward=False):
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.INT3, GPIO.OUT)
            GPIO.setup(self.INT4, GPIO.OUT)
            GPIO.setup(self.ENB, GPIO.OUT)
            pwmb = GPIO.PWM(self.ENB, 80)
            pwmb.start(50)
            if backforward:
                GPIO.output(self.INT3, GPIO.HIGH)
                GPIO.output(self.INT4, GPIO.LOW)
            else:
                GPIO.output(self.INT3, GPIO.LOW)
                GPIO.output(self.INT4, GPIO.HIGH)
            pwmb.ChangeDutyCycle(90)
            time.sleep(duration)
        finally:
            pwmb.stop()  # 停止PWM
            GPIO.cleanup()  # 清理释放GPIO资源，将GPIO复位

    def move_forward(self, duration, backforward=False, wait=True):
        if not wait:
            t1 = threading.Thread(target=self._move_forward_, args=(duration, backforward, ))
            t1.start()
        else:
            self._move_forward_(duration, backforward)


if __name__ == "__main__":
    motor = Motor()
    motor.move_forward(2, backforward=True, wait=True)
