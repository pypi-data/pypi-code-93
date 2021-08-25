try:
    from gpiozero import Button
    from gpiozero import LED, PWMLED
    import time

    import sys, os, inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0, parentdir)

    from define import *

#    fan=LED(FAN_PWM_PIN, active_high=False, initial_value=True)
    fan=PWMLED(FAN_PWM_PIN, active_high=False, initial_value=0, frequency = 100)

    def fanTurnOn(on):
        global fan
        if on:
            fan.value=0.5
        else:
            fan.value=0
    if __name__ == "__main__":
        fanTurnOn(True)
        time.sleep(5)
        fanTurnOn(False)
        time.sleep(5)
        fanTurnOn(True)
        time.sleep(5)
        fanTurnOn(False)
except Exception as e:
    print(e)
    pass
    
    
