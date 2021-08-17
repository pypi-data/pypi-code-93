# -*- coding:utf-8 -*-
import time
import sys
import argparse
import kdxfsdk.config_defaults


class PCA9685:
    """
    PWM motor controler using PCA9685 boards.
    This is used for most RC Cars
    """
    def __init__(self, channel, frequency=60):
        import Adafruit_PCA9685
        # Initialise the PCA9685 using the default address (0x40).
        self.pwm = Adafruit_PCA9685.PCA9685()
        self.pwm.set_pwm_freq(frequency)
        self.channel = channel

    def set_pulse(self, pulse):
        try:
            self.pwm.set_pwm(self.channel, 0, pulse)
        except OSError as err:
            print("Unexpected issue setting PWM (check wires to motor board): {0}".format(err))


class FourFootRobot(object):
    def __init__(self):
        direction0 = PCA9685(0)
        direction1 = PCA9685(2)
        direction2 = PCA9685(4)
        direction3 = PCA9685(6)
        self.DirectionPwm = [direction0, direction1, direction2, direction3]

        foot0 = PCA9685(1)
        foot1 = PCA9685(3)
        foot2 = PCA9685(5)
        foot3 = PCA9685(7)
        self.Foot = [foot0, foot1, foot2, foot3]

    def in_line(self):
        # direction
        for i in range(4):
            self.DirectionPwm[i].set_pulse(config_defaults.DIRECTION_CONFIG[i][1])

    def stable(self):
        # direction
        for i in range(4):
            self.DirectionPwm[i].set_pulse(config_defaults.DIRECTION_CONFIG[i][2])

    def stand_up(self):
        self.in_line()
        # foot
        for i in range(4):
            self.Foot[i].set_pulse(config_defaults.FOOT_CONFIGFOOT_CONFIG[i][1])

    def set_one(self, i, pulse):
       self.Foot[i].set_pulse(pulse)

    def sit(self):
        # direction
        self.in_line()
        # foot
        for i in range(4):
            self.Foot[i].set_pulse(config_defaults.FOOT_CONFIG[i][0])

    # 1, means forward, -1 means backword
    def _right_move_begin(self, for_or_back):
        if for_or_back == 1:
            up_delta = (config_defaults.FOOT_CONFIG[1][1] + config_defaults.FOOT_CONFIG[1][2])/2
        else:
            up_delta = (config_defaults.FOOT_CONFIG[1][1] + config_defaults.FOOT_CONFIG[1][0])/2
        self.Foot[1].set_pulse(int(up_delta))
        time.sleep(config_defaults.MOVE_INTERVAL * config_defaults.MOVE_INTERVAL_RATIO)
        if for_or_back == 1:
            up_delta = (config_defaults.FOOT_CONFIG[2][1] + config_defaults.FOOT_CONFIG[2][0])/2
        else:
            up_delta = (config_defaults.FOOT_CONFIG[2][1] + config_defaults.FOOT_CONFIG[2][2])/2

        self.Foot[2].set_pulse(int(up_delta))
        time.sleep(config_defaults.MOVE_INTERVAL * config_defaults.MOVE_INTERVAL_RATIO)
        self.Foot[0].set_pulse(config_defaults.FOOT_CONFIG[0][0])
        self.Foot[3].set_pulse(config_defaults.FOOT_CONFIG[3][0])
        time.sleep(config_defaults.MOVE_INTERVAL * config_defaults.MOVE_INTERVAL_RATIO * 1.5)

    def _right_move_end(self, for_or_back):
        if for_or_back == 1:
            up_delta1 = (config_defaults.FOOT_CONFIG[1][1] + config_defaults.FOOT_CONFIG[1][0])/2
        else:
            up_delta1 = (config_defaults.FOOT_CONFIG[1][1] + config_defaults.FOOT_CONFIG[1][2])/2
        self.Foot[1].set_pulse(int(up_delta1))
        time.sleep(config_defaults.MOVE_INTERVAL * config_defaults.MOVE_INTERVAL_RATIO)
        if for_or_back == 1:
            up_delta2 = (config_defaults.FOOT_CONFIG[2][1] + config_defaults.FOOT_CONFIG[2][2])/2
        else:
            up_delta2 = (config_defaults.FOOT_CONFIG[2][1] + config_defaults.FOOT_CONFIG[2][0])/2
        self.Foot[2].set_pulse(int(up_delta2))
        time.sleep(config_defaults.MOVE_INTERVAL * config_defaults.MOVE_INTERVAL_RATIO * 1.5)

    def _left_move_begin(self, for_or_back):
        if for_or_back == 1:
            up_delta = (config_defaults.FOOT_CONFIG[0][1] + config_defaults.FOOT_CONFIG[0][2])/2
        else:
            up_delta = (config_defaults.FOOT_CONFIG[0][1] + config_defaults.FOOT_CONFIG[0][0])/2
        self.Foot[0].set_pulse(int(up_delta))
        time.sleep(config_defaults.MOVE_INTERVAL * config_defaults.MOVE_INTERVAL_RATIO)
        if for_or_back == 1:
            up_delta = (config_defaults.FOOT_CONFIG[3][1] + config_defaults.FOOT_CONFIG[3][0])/2
        else:
            up_delta = (config_defaults.FOOT_CONFIG[3][1] + config_defaults.FOOT_CONFIG[3][2])/2

        self.Foot[3].set_pulse(int(up_delta))
        self.Foot[2].set_pulse(config_defaults.FOOT_CONFIG[2][0])
        self.Foot[1].set_pulse(config_defaults.FOOT_CONFIG[1][0])
        time.sleep(config_defaults.MOVE_INTERVAL * config_defaults.MOVE_INTERVAL_RATIO * 1.5)

    def _left_move_end(self, for_or_back):
        if for_or_back == 1:
            up_delta1 = (config_defaults.FOOT_CONFIG[0][1] + config_defaults.FOOT_CONFIG[0][0])/2
        else:
            up_delta1 = (config_defaults.FOOT_CONFIG[0][1] + config_defaults.FOOT_CONFIG[0][2])/2
        self.Foot[0].set_pulse(int(up_delta1))
        time.sleep(config_defaults.MOVE_INTERVAL * config_defaults.MOVE_INTERVAL_RATIO)
        if for_or_back == 1:
            up_delta2 = (config_defaults.FOOT_CONFIG[3][1] + config_defaults.FOOT_CONFIG[3][2])/2
        else:
            up_delta2 = (config_defaults.FOOT_CONFIG[3][1] + config_defaults.FOOT_CONFIG[3][0]) / 2
        self.Foot[3].set_pulse(int(up_delta2))
        time.sleep(config_defaults.MOVE_INTERVAL * config_defaults.MOVE_INTERVAL_RATIO * 1.5)

    def tern_left(self):
        # direction
        for i in range(4):
            self.Foot[i].set_pulse(config_defaults.FOOT_CONFIG[i][0])
            self.DirectionPwm[i].set_pulse(config_defaults.DIRECTION_CONFIG[i][3])
            time.sleep(config_defaults.MOVE_INTERVAL * config_defaults.MOVE_INTERVAL_RATIO)
        self.stable()

    def forword(self):
        self._right_move_begin(1)
        time.sleep(config_defaults.MOVE_INTERVAL * config_defaults.MOVE_INTERVAL_RATIO)
        self._right_move_end(1)
        self._left_move_begin(1)
        time.sleep(config_defaults.MOVE_INTERVAL * config_defaults.MOVE_INTERVAL_RATIO)
        self._left_move_end(1)
        time.sleep(config_defaults.MOVE_INTERVAL * config_defaults.MOVE_INTERVAL_RATIO)

    def backword(self):
        self._right_move_begin(-1)
        time.sleep(config_defaults.MOVE_INTERVAL * config_defaults.MOVE_INTERVAL_RATIO)
        self._right_move_end(-1)
        self._left_move_begin(-1)
        time.sleep(config_defaults.MOVE_INTERVAL * config_defaults.MOVE_INTERVAL_RATIO)
        self._left_move_end(-1)
        time.sleep(config_defaults.MOVE_INTERVAL * config_defaults.MOVE_INTERVAL_RATIO)

    def reset_inline(self):
        self.in_line()
        self.sit()

    def reset_stable(self):
        self.stable()
        self.stand_up()



def parse_args(args):
    parser = argparse.ArgumentParser(prog='calibrate', usage='%(prog)s [options]')
    parser.add_argument('--channel', help='The channel youd like to calibrate [0-15]')
    parsed_args = parser.parse_args(args)
    return parsed_args


def calibrate():
    args = sys.argv[1:]
    args = parse_args(args)
    channel = int(args.channel)
    c = PCA9685(channel)
    while True:
        try:
            val = input("""Enter a PWM setting to test.py ('q' for quit) (0-1500): """)
            if val == 'q' or val == 'Q':
                break
            pmw = int(val)
            c.set_pulse(pmw)
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt received, exit.")
            break
        except Exception as ex:
            print("Oops, {}".format(ex))


if __name__ != '__main__':
    calibrate()

if __name__ == '__main__':
    foot_robot = FourFootRobot()
    foot_robot.sit()
    time.sleep(2)
    foot_robot.stand_up()
    for i in range(10):
        foot_robot.forword()
        time.sleep(0.1)
    foot_robot.sit()
