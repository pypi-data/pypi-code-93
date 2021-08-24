# from .fly_log import debug_print
from fly_log import debug_print

print = debug_print

def dev_run1():
    print("dev_run1")
    print("dev_run1")


if __name__ == '__main__':
    dev_run1()
