import os
import sys

EXT_NAME_IMG = ['.jpg', '.jpeg', '.webp', '.bmp', '.png']
EXT_VIDEO_IMG = ['mp4', 'mov', 'avi', 'mkv']




def get_path_root():
    '''os.path.dirname(os.path.abspath(__file__))'''
    debug_vars = dict((a, b) for a, b in os.environ.items() if a.find('IPYTHONENABLE') >= 0)
    # 根据不同场景获取根目录
    if len(debug_vars) > 0:
        """当前为debug运行时"""
        path_root = sys.path[2]
    elif getattr(sys, 'frozen', False):
        """当前为exe运行时"""
        path_root = os.getcwd()
    else:
        """正常执行"""
        path_root = sys.path[1]
    path_root = path_root.replace("\\", "/")  # 替换斜杠
    return path_root


def get_img_file(path):
    files_pic = []
    for maindir, subdir, file_name_list in os.walk(path):
        for filename in file_name_list:
            apath = os.path.join(maindir, filename)
            ext = os.path.splitext(apath)[1]
            if ext in EXT_NAME_IMG:
                files_pic.append(apath)
    return files_pic


def fshow_time(fun, arg_list=None, num_time=1):
    '''

    :param fun:
    :param arg_list:  net, input  arg 需在外面打包为list
    :return:
    '''
    import time
    from ftools.GLOBAL_LOG import flog
    assert num_time >= 1
    ret = None
    start = time.time()
    flog.debug('show_time---开始---%s-------' % (fun.__name__))
    for i in range(num_time):
        if arg_list is None:
            ret = fun()
        else:
            ret = fun(*arg_list)
    flog.debug('show_time---完成---%s---%s\n' % (fun.__name__, time.time() - start))
    return ret
