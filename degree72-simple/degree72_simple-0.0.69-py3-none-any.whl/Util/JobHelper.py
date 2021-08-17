import os


def debug():
    return not (os.getenv('PRODUCTION') == 'TRUE')


def get_stack_frame(stack, frame_trace_num=0):  # the order of frame you want to trace
    frames = []
    switch = True
    temp = ''
    for each in stack:
        path = each[1]
        folder = os.path.basename(os.path.dirname(path)) # folder name of **.py
        if folder in ['Core', 'Util']:
            continue
        elif switch:
            temp = folder
            switch = False
        if temp == folder:
            frames.append(each)

    return frames[frame_trace_num]


def get_data_folder(stack, project_name='.'):
    if debug():
        stack_folder = os.path.dirname(get_stack_frame(stack)[1])
        if os.path.basename(stack_folder) == 'operators':  # airflow
            folder_path = os.path.join(os.path.expanduser('~'), 'Data', *project_name.split('.'))
        else:
            folder_path = os.path.join(stack_folder, 'Data')
    else:
        folder_path = os.path.join(os.path.expanduser('~'), 'Data', *project_name.split('.'))

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    return folder_path

