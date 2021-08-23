# -*- coding: utf-8 -*-
'''
@Time    : /
@Author  : Yanyuxiang
@Email   : yanyuxiangtoday@163.com
@FileName: /
@Software: PyCharm
'''

def rm_elem(input_list,
            elem=None):
    '''
    remove elem from input_list if elem in input_list,
    if not elem, will remove '.DS_Store'.

    :param input_list: list to remove elem
    :param elem:       elem ot remove in list
    :return:           None
    '''
    if elem:
        input_list.remove(elem) if elem in input_list else None
    else:
        input_list.remove('.DS_Store') if '.DS_Store' in input_list else None
    return
