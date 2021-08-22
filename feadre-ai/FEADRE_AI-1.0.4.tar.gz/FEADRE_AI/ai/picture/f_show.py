import math
import random

import matplotlib
import numpy as np
import cv2
import torch
from PIL import Image, ImageDraw, ImageFont
from torchvision import transforms
import matplotlib.pyplot as plt

from ftools.GLOBAL_LOG import flog
from ftools.general.FColor import fcre_color_indexes, COLORS_MAP, fget_color_random, fget_color_val, COLORS_RGB, \
    fhex2rgb

'''
plt 常用颜色: 'lightgreen' 'red' 'tan'
'''

FONT4CV = cv2.FONT_HERSHEY_SIMPLEX  # 加粗
FONT4CV = cv2.FONT_HERSHEY_COMPLEX  # 细点


def _draw_grid4plt(size, grids):
    '''

    :param size:
    :param grids:
    :return:
    '''
    # colors_ = STANDARD_COLORS[random.randint(0, len(STANDARD_COLORS) - 1)]
    colors_ = 'Pink'
    w, h = size
    xys = np.array([w, h]) / grids
    off_x = np.arange(1, grids[0])
    off_y = np.arange(1, grids[1])
    xx = off_x * xys[0]
    yy = off_y * xys[1]

    for x_ in xx:
        # 画列
        plt.plot([x_, x_], [0, h], color=colors_, linewidth=1., alpha=0.3)
    for y_ in yy:
        # 画列
        plt.plot([0, w], [y_, y_], color=colors_, linewidth=1., alpha=0.3)


def _convert_uint8(img_np):
    if img_np.dtype is not np.uint8:
        img_np_uint8 = img_np.copy()
        img_np_uint8 = img_np_uint8.astype(np.uint8)
    else:
        return img_np
    return img_np_uint8


def _draw_box4plt(boxes, texts=None, font_size=10, color='red', ax=None, recover_sizewh=None, linewidth=1):
    '''

    :param boxes:
    :param texts: 与 boxes 对应的 文本 list
    :param font_size:
    :param color:
    :param ax:  ax = plt.gca()
    :return:
    '''
    if recover_sizewh is not None:
        whwh = np.tile(np.array(recover_sizewh), 2)  # 整体复制 tile
        boxes = boxes * whwh

    if texts is not None:
        try:
            font = ImageFont.truetype('simhei.ttf', font_size, encoding='utf-8')  # 参数1：字体文件路径，参数2：字体大小
        except IOError:
            font = ImageFont.load_default()
        text_w, text_h = font.getsize(str(texts[0]))
        margin = np.ceil(0.05 * text_h)

    for i, box in enumerate(boxes):
        l, t, r, b = box
        w = r - l
        h = b - t

        if ax is None:
            plt.Rectangle((l, t), w, h, color=color, fill=False, linewidth=linewidth)
        else:
            ax.add_patch(plt.Rectangle((l, t), w, h, color=color, fill=False, linewidth=linewidth))

        if texts is not None:
            if ax is None:
                plt.text(l + margin, t - text_h - margin, str(texts[i]),
                         color="r", ha='center', va='center',
                         bbox={'facecolor': 'blue', 'alpha': 0.5, 'pad': 1})
            else:
                ax.text(l + margin, t - text_h - margin, str(texts[i]),
                        color="r", ha='center', va='center',
                        bbox={'facecolor': 'blue', 'alpha': 0.5, 'pad': 1})

        x = l + w / 2
        y = t + h / 2
        plt.scatter(x, y, marker='x', color=color, s=40, label='First')


def f_show_od_ts4plt_v3(img_ts, g_ltrb=None, p_ltrb=None, is_recover_size=False,
                        p_texts=None, g_texts=None, is_normal=False, is_torgb=False,
                        grid_wh_np=None, title=None):
    '''

    :param img_ts:
    :param g_ltrb:
    :param p_ltrb:
    :param is_recover_size:
    :param p_texts:  输入 list
    :param g_texts:
    :param is_normal:
    :param is_torgb:
    :param grid_wh_np: np(7,7)
    :param title: 指定标题 不指定自动生成
    :return:
    '''
    assert isinstance(img_ts, torch.Tensor)
    # c,h,w -> h,w,c
    if is_normal:
        from ftools.ai.datas.dta_heighten.f_data_heighten4target import f_recover_normalization4ts_v2
        img_ts = img_ts.clone()
        img_ts = f_recover_normalization4ts_v2(img_ts)
    img_np = img_ts.cpu().numpy().astype(np.uint8).transpose((1, 2, 0))
    if is_torgb:
        img_np = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
    f_show_od_np4plt_v3(img_np, g_ltrb=g_ltrb, p_ltrb=p_ltrb,
                        is_recover_size=is_recover_size,
                        title=title,
                        p_texts=p_texts, g_texts=g_texts, grid_wh_np=grid_wh_np)


def f_show_od_np4plt_v3(img_np, g_ltrb=None, p_ltrb=None, other_ltrb=None, title=None,
                        is_recover_size=False, p_texts=None, g_texts=None, grid_wh_np=None,
                        ):
    img_np = _convert_uint8(img_np)
    plt.imshow(img_np)
    # plt.show()
    ax = plt.gca()

    if is_recover_size:
        recover_sizewh = img_np.shape[:2][::-1]  # npwh
    else:
        recover_sizewh = None

    if grid_wh_np is not None:
        wh = img_np.shape[:2][::-1]  # npwh
        _draw_grid4plt(wh, grid_wh_np)

    _draw_title4plt(img_np, p_ltrb, title)

    if other_ltrb is not None:
        _draw_box4plt(other_ltrb, color='tan', ax=ax, recover_sizewh=recover_sizewh)

    if g_ltrb is not None:
        _draw_box4plt(g_ltrb, texts=g_texts, color='lightgreen', ax=ax, recover_sizewh=recover_sizewh, linewidth=3)

    if p_ltrb is not None:
        _draw_box4plt(p_ltrb, texts=p_texts, color='red', ax=ax, recover_sizewh=recover_sizewh)

    plt.show()


def _draw_title4plt(img_np, p_ltrb, title):
    if title is not None:
        text = title
    else:
        if p_ltrb is not None:
            text = '%s x %s (num_pos = %s)' % (str(img_np.shape[1]), str(img_np.shape[0]), str(len(p_ltrb)))
        else:
            text = '%s x %s ' % (str(img_np.shape[1]), str(img_np.shape[0]))
    plt.title(text)


def f_show_kp_np4plt(img_np, kps, kps_seq=None, g_ltrb=None, p_ltrb=None, other_ltrb=None, title=None,
                     is_recover_size=False, p_texts=None, g_texts=None, kps_size=20,
                     ):
    indexes_color = fcre_color_indexes(len(kps[0]) // 3)

    img_np = _convert_uint8(img_np)
    plt.imshow(img_np)
    # plt.show()
    ax = plt.gca()

    if is_recover_size:
        recover_sizewh = img_np.shape[:2][::-1]  # npwh
    else:
        recover_sizewh = None

    _draw_title4plt(img_np, p_ltrb, title)
    for kp in kps:  # 这是一批
        for i, open in enumerate(kp[2::3]):
            if open != 0:
                plt.scatter(kp[::3], kp[1::3],
                            color=np.array(list(COLORS_MAP.keys()))[indexes_color],
                            s=kps_size, alpha=1.)
        if kps_seq is not None:
            for seq in kps_seq:
                _kp = kp.reshape(-1, 3)
                xyt_s = _kp[seq[0]]
                xyt_e = _kp[seq[1]]
                if xyt_s[2] != 0 and xyt_e[2] != 0:
                    plt.plot([xyt_s[0], xyt_e[0]],
                             [xyt_s[1], xyt_e[1]],
                             color=list(COLORS_MAP.keys())[indexes_color[seq[0]]],
                             linewidth=2,
                             alpha=0.8,
                             )

    if other_ltrb is not None:
        _draw_box4plt(other_ltrb, color='tan', ax=ax, recover_sizewh=recover_sizewh)

    if g_ltrb is not None:
        _draw_box4plt(g_ltrb, texts=g_texts, color='lightgreen', ax=ax, recover_sizewh=recover_sizewh, linewidth=3)

    if p_ltrb is not None:
        _draw_box4plt(p_ltrb, texts=p_texts, color='red', ax=ax, recover_sizewh=recover_sizewh)


def draw_text_chinese4cv(img_np, text, left, top, textColor=(0, 255, 0), textSize=20):
    # 图片，添加的文字，左上角坐标，字体，字体大小，颜色，字体粗细
    # img_np = cv2.putText(img_np, text_, (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
    #                      (0, 255, 0), 1)
    img_pil = Image.fromarray(cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img_pil)
    # 字体的格式
    fontStyle = ImageFont.truetype("font/simsun.ttc", textSize, encoding="utf-8")
    # 绘制文本
    draw.text((left, top), text, textColor, font=fontStyle)
    # 转换回OpenCV格式
    return cv2.cvtColor(np.asarray(img_pil), cv2.COLOR_RGB2BGR)
    # return img_np


def f_show_pic_np4plt(img_np):
    '''
    不支持float32
    :param pic:
    :return:
    '''
    img_np = _convert_uint8(img_np)
    plt.imshow(img_np)
    plt.show()


''' ********************   cv区 ******************** '''


def _draw_box4cv(img_np, boxes, texts=None,
                 color=fget_color_val(0), recover_sizewh=None, thickness=2):
    if recover_sizewh is not None:
        whwh = np.tile(np.array(recover_sizewh), 2)  # 整体复制 tile
        boxes = boxes * whwh

    if texts is not None:
        txt_size = cv2.getTextSize(texts[0], FONT4CV, fontScale=2, thickness=1)[0]

    for i, box in enumerate(boxes):
        box = list(map(int, box))
        l, t, r, b = box
        w = r - l
        h = b - t

        cv2.rectangle(img_np, (l, t), (r, b), color, thickness=thickness)
        if texts is not None:
            # mask_img = cv2.addWeighted(image, alpha, zeros_mask, beta, gamma) # 透明有点麻烦
            # cv2.rectangle(
            #     img_np,
            #     (l, t + 1),
            #     (l + txt_size[0] + 1, t + int(1.5 * txt_size[1])),
            #     (COLORS_RGB[3] * 255 * 0.7).astype(np.uint8).tolist()[1],
            #     thickness=-1,  # 负1填充
            # )
            cv2.putText(img_np, texts[i], (l, t + txt_size[1]), FONT4CV,
                        fontScale=1.3, color=fget_color_val(1), thickness=3)

        x = l + w / 2
        y = t + h / 2
        cv2.circle(img_np, (int(x), int(y)), radius=3,
                   color=color, thickness=-1,  # 负1填充
                   )


def _draw_title4cv(img_np, p_ltrb, title):
    h, w, _ = img_np.shape
    if title is not None:
        text = title
    else:
        if p_ltrb is not None:
            text = '%s x %s (num_pos = %s)' % (str(w), str(h), str(len(p_ltrb)))
        else:
            text = '%s x %s ' % (str(h), str(w))
    # 返回 ((宽,高),字号)
    text_scale = 0.4 * (float(w) / 300)
    txt_size = cv2.getTextSize(text, FONT4CV, text_scale, 1)[0]
    x = 0
    y = 0
    cv2.putText(img_np, text,
                (x, y + txt_size[1]), FONT4CV, text_scale,
                # fget_color_random(),
                fget_color_val(0),
                lineType=cv2.LINE_4,
                thickness=1, )


def f_show_pic_np4cv(img_np):
    img_np = _convert_uint8(img_np)
    cv2.imshow('Example', img_np)
    cv2.waitKey(0)


def f_show_kp_np4cv(img_np, p_kps_l, g_kps_l=None, kps_seq=None, g_ltrb=None, p_ltrb=None, title=None,
                    is_recover_size=False, p_texts=None, g_texts=None,
                    is_show=True, is_color_same=False,
                    ):
    '''

    :param img_np:
    :param g_kps_l:  (ngt,num_keypoints*3)
    :param kps_seq: [[13, 12], [12, 9], [12, 8], [9, 10], [8, 7], [10, 11], [7, 6], [12, 3], [12, 2], [2, 1], [1, 0], [3, 4],[4, 5]],
    :param g_ltrb:
    :param p_ltrb:
    :param title:
    :param is_recover_size:
    :param p_texts:
    :param g_texts:
    :param is_show:
    :return:
    '''
    img_np = f_show_od_np4cv(img_np, g_ltrb=g_ltrb, p_ltrb=p_ltrb, title=title,
                             is_recover_size=is_recover_size,
                             p_texts=p_texts, g_texts=g_texts,
                             is_show=False)

    num_invalid_points_g = 0
    if g_kps_l is not None:
        num_invalid_points_g = _draw_kps4cv(
            g_kps_l, img_np, is_color_same, is_recover_size, kps_seq, idx_color=1)

    num_invalid_points_p = 0
    if p_kps_l is not None:
        # 蓝色
        num_invalid_points_p = _draw_kps4cv(
            p_kps_l, img_np, is_color_same, is_recover_size, kps_seq, idx_color=5)

    if is_show:
        flog.debug('无效点个数 num_invalid_points_p={}, num_invalid_points_g={}'
                   .format(num_invalid_points_p, num_invalid_points_g))
        plt.imshow(img_np)
        plt.show()
    return img_np


def _draw_kps4cv(kps_l, img_np, is_color_same, is_recover_size, kps_seq, idx_color=5):
    '''

    :param kps_l:
    :param img_np:
    :param is_color_same:
    :param is_recover_size:
    :param kps_seq:
    :param idx_color:  相同颜色的 序列
    :return:
    '''
    num_keypoints = len(kps_l[0]) // 3

    if is_color_same:
        indexes_color = [idx_color] * num_keypoints
    else:
        indexes_color = fcre_color_indexes(num_keypoints)

    if is_recover_size:
        recover_sizewh = list(img_np.shape[:2][::-1])  # npwh
        recover_sizewh.append(1)  # 增加1维
        whwh = np.tile(np.array(recover_sizewh), len(indexes_color)).reshape(1, -1)  # 整体复制 tile
        kps_l = kps_l * whwh

    num_invalid_points = 0
    # kps_l = kps_l.astype(np.int)  # 只支持int 这里不能直接转  否则分数没有了
    for kp in kps_l:  # 这是一批
        if kps_seq is not None:
            for seq in kps_seq:
                _kp = kp.reshape(-1, 3)
                xyt_s = _kp[seq[0]]
                xyt_e = _kp[seq[1]]
                if xyt_s[2] != 0 and xyt_e[2] != 0:
                    cv2.line(img_np,
                             pt1=(int(xyt_s[0]), int(xyt_s[1])),
                             pt2=(int(xyt_e[0]), int(xyt_e[1])),
                             color=fget_color_val(indexes_color[seq[0]]),
                             thickness=1,
                             lineType=cv2.LINE_8,  # 速度：LINE_8>LINE_AA  美观：LINE_AA>LINE_8
                             )
                pass

        for i, xyt in enumerate(kp.reshape(-1, 3)):  # 这里是一个点
            if xyt[2] != 0:
                cv2.circle(img_np,
                           center=(int(xyt[0]), int(xyt[1])),
                           # center=tuple(xyt[:2].tolist()),  # 必须是tuple
                           radius=3,
                           thickness=-1,
                           color=fget_color_val(indexes_color[i])
                           )
            else:
                num_invalid_points += 1
    return num_invalid_points


def f_show_od_np4cv(img_np, g_ltrb=None, p_ltrb=None, title=None,
                    is_recover_size=False, p_texts=None, g_texts=None,
                    is_show=True,
                    ):
    img_np = _convert_uint8(img_np)

    if is_recover_size:
        recover_sizewh = img_np.shape[:2][::-1]  # npwh
    else:
        recover_sizewh = None

    _draw_title4cv(img_np, p_ltrb, title)

    if g_ltrb is not None:
        _draw_box4cv(img_np, g_ltrb, texts=g_texts, color=fhex2rgb(COLORS_MAP['lightgreen']),
                     recover_sizewh=recover_sizewh,
                     thickness=3)

    if p_ltrb is not None:
        _draw_box4cv(img_np, p_ltrb, texts=p_texts, color=fhex2rgb(COLORS_MAP['red']),
                     recover_sizewh=recover_sizewh,
                     thickness=3)

    if is_show:
        plt.imshow(img_np)
        plt.show()
    return img_np


''' ********************   cv区结束 ******************** '''


def keypoint_painter(images, maps, img_h, img_w, numpy_array=False,
                     phase_gt=False, center_map=None):
    images = images.clone().cpu().data.numpy().transpose([0, 2, 3, 1])
    maps = maps.clone().cpu().data.numpy()
    if center_map is not None:
        center_map = center_map.clone().cpu().data.numpy()
    imgs_tensor = []
    if phase_gt:
        for img, map, c_map in zip(images, maps, center_map):
            img = cv2.resize(img, (img_w, img_h))
            for m in map[:14]:
                h, w = np.unravel_index(m.argmax(), m.shape)
                x = int(w * img_w / m.shape[1])
                y = int(h * img_h / m.shape[0])
                img = cv2.circle(img.copy(), (x, y), radius=1, thickness=2, color=(255, 0, 0))
            h, w = np.unravel_index(c_map.argmax(), c_map.shape)
            x = int(w * img_w / c_map.shape[1])
            y = int(h * img_h / c_map.shape[0])
            img = cv2.circle(img.copy(), (x, y), radius=1, thickness=2, color=(0, 0, 255))
            if numpy_array:
                imgs_tensor.append(img.astype(np.uint8))
            else:
                imgs_tensor.append(transforms.ToTensor()(img))
    else:

        for img, map_6 in zip(images, maps):
            img = cv2.resize(img, (img_w, img_h))
            for step_map in map_6:
                img_copy = img.copy()
                for m in step_map[:14]:
                    h, w = np.unravel_index(m.argmax(), m.shape)
                    x = int(w * img_w / m.shape[1])
                    y = int(h * img_h / m.shape[0])
                    img_copy = cv2.circle(img_copy.copy(), (x, y), radius=1, thickness=2, color=(255, 0, 0))
                if numpy_array:
                    imgs_tensor.append(img_copy.astype(np.uint8))
                else:
                    imgs_tensor.append(transforms.ToTensor()(img_copy))
    return imgs_tensor


def f_show_cpm4input(img_np, kps_xy_input, heatmap_center_input):
    '''

    :param img_np:
    :param kps_xy_input: (14, 2)
    :param heatmap_center_input: (368, 368)
    :return:
    '''
    img_np = _convert_uint8(img_np)
    plt.imshow(img_np, alpha=0.7)
    for xy in kps_xy_input:
        plt.scatter(xy[0], xy[1], color='r', s=5, alpha=0.5)
    plt.imshow(heatmap_center_input, alpha=0.5)
    plt.show()


def f_show_cpm4t_all(img_np, kps_xy_input, heatmap_center_input, heatmap_t, size_wh_input):
    '''
    弄到input进行处理
    :param img_np:
    :param kps_xy_t: (14, 2)
    :param heatmap_center_input: (368, 368,1)
    :param heatmap_t: (46, 46, 14)
    :param size_wh_t: (46, 46, 15)
    :return:
    '''
    img_np = _convert_uint8(img_np)
    plt.imshow(img_np, alpha=1.0)
    for xy in kps_xy_input:
        plt.scatter(xy[0], xy[1], color='r', s=5, alpha=0.5)
    plt.imshow(heatmap_center_input, alpha=0.3)

    h, w, c = heatmap_t.shape
    img_heatmap_z = np.zeros((size_wh_input[1], size_wh_input[0], 1), dtype=np.uint8)
    for i in range(c):
        img_heatmap = heatmap_t[..., i][..., None]
        img_heatmap = cv2.resize(img_heatmap, size_wh_input)  # wh
        # img_heatmap = _convert_uint8(img_heatmap)
        img_heatmap_z = np.maximum(img_heatmap_z, img_heatmap[..., None])

    plt.imshow(img_heatmap_z, alpha=0.3)
    plt.show()


if __name__ == '__main__':
    file_img = r'D:\tb\tb\ai_code\fkeypoint\_test_pic\street.jpg'
    img_np_bgr = cv2.imread(file_img)
    boxes = np.array([
        [1, 1, 100, 100],
        [120, 120, 200, 200],
    ])
    gtexts = ['123', '445566']

    f_show_od_np4plt_v3(img_np_bgr, g_ltrb=boxes, g_texts=gtexts)
