from ..ext.hist import hist_tail
import os

def run_command(n_lines: list):
    # TODO: propagate that last line in n_lines is the # of lines used
    # maybe add a check for 1 num to use default (20)
    df = hist_tail(n_lines[-1])
    exec_line = ''
    for cmd in n_lines[:-1]:
        exec_line += f"{df.iloc[cmd].Command}"
        exec_line += ' && '

    print(f"Running {exec_line[:-4]}")
    os.system(exec_line[:-4])
    # print(exec_line[:-4])