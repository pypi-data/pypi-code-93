# -*- coding: utf-8 -*-
'''
@Time    : /
@Author  : Yanyuxiang
@Email   : yanyuxiangtoday@163.com
@FileName: /
@Software: PyCharm
'''

import cv2

def info(mp4_path):
    '''
    this func get and print video info using cv2

    :param video_path: path to video
    :return: fps, total frames, image width, image height
    '''

    cap = cv2.VideoCapture(mp4_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print('----------------------------------------------------------------------------------------------------')
    print('info fps {:.5f}, frameCnt {:^9}, width {:^5}, height {:^5}, time len {:0>2d}:{:0>2d}:{:0>2d}'.format(
        fps,
        frame_count,
        width,
        height,
        int((frame_count / fps) // 3600),
        int(((frame_count / fps) % 3600 ) // 60),
        int(((frame_count / fps) % 3600) % 60)))
    return fps, frame_count, width, height