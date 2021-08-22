import numpy as np


def fcre_kps_min_bbox(kps, scale=1):
    '''
    创建 关键点最小外拉框
    :param kps: (ngt,num_keypoints*3)
    :param scale:
    :return:
    '''
    _kps, mask = fsplit_kps(kps)
    xys = _kps[:, :, :2]
    bbox = []
    for i, xy in enumerate(xys):
        lt = np.min(xy[mask[i]], axis=0)
        rb = np.max(xy[mask[i]], axis=0)
        bbox.append([*lt, *rb])
    bbox = np.stack(bbox, 0)
    return bbox * scale


def fverify_kps(kps, ltrb):
    '''
    校验有效性 出界的不要
    :param kps: (ngt,num_keypoints*3)
    :param ltrb: [4]
    :return:
    '''
    assert len(ltrb) == 4, 'len(ltrb)= %s' % len(ltrb)
    ngt, dim_kps = kps.shape
    # (ngt,dim_kps) ->  (ngt,num_keypoints,3)
    _kps = kps.reshape(ngt, -1, 3)
    # (ngt,num_keypoints) 超出的记录下来
    mask_x = np.logical_or(_kps[:, :, 0] < ltrb[0], _kps[:, :, 0] > ltrb[2])
    mask_y = np.logical_or(_kps[:, :, 1] < ltrb[1], _kps[:, :, 1] > ltrb[3])
    mask = np.logical_or(mask_x, mask_y)
    if mask.any():
        _kps[mask, 2] = 0
        # flog.debug('mask.sum()= %s', mask.sum())
    return _kps.reshape(ngt, -1)


def fsplit_kps(kps):
    ''' 返回 reshape后的kps 和 2二维 mask '''
    ngt, dim_kps = kps.shape
    # (ngt,dim_kps) ->  (ngt,num_keypoints,3)
    _kps = kps.reshape(ngt, -1, 3)
    # xys = _kps[:, :, :2]
    # (ngt,num_keypoints)
    mask = _kps[:, :, 2].astype(np.bool)
    return _kps, mask
