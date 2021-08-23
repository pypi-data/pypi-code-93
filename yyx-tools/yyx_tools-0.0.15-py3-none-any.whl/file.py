# -*- coding: utf-8 -*-
'''
@Time    : /
@Author  : Yanyuxiang
@Email   : yanyuxiangtoday@163.com
@FileName: /
@Software: PyCharm
'''

import os
import numpy as np

def save(dump_path,
         content,
         keep_ori):
    '''
    save str/np.array to txt or csv

    :param dump_path: path to save file
    :param content:   content to save, it could be str or np.array2d
    :param keep_ori:  if True, it will add content at the tail of thr file, else will delte ori file
    :return:          None
    '''

    keep_ori = (keep_ori == 'True') if isinstance(keep_ori, str) else keep_ori

    os.system(f'rm {dump_path}') if not keep_ori and os.path.exists(dump_path) else None

    if dump_path[-4:] != '.txt' and dump_path[-4:] != '.csv':
        raise Exception('wrong type to save')

    if isinstance(content, str):
        with open(dump_path, 'a') as dump_file:
            dump_file.write(content)
    elif isinstance(content, type(np.array(0.0))):
            np.savetxt(dump_path, content, fmt='%.5f', delimiter=',')
    else:
        raise Exception('wrong content type')

    return

