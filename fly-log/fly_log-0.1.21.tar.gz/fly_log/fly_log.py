import sys
import os
import time


old_print = print


def debug_print(*p):
    current_frame = sys._getframe(1)
    code_info = " %s(%s:%s)" % (current_frame.f_code.co_name, os.path.basename(current_frame.f_code.co_filename), current_frame.f_lineno)
    old_print(time.strftime("%Y-%m-%d %H:%M:%S") + code_info, *p)



