import torch

from ftools.GLOBAL_LOG import flog
from ftools.ai.fits.olf.floss import f_bce_loss
from ftools.ai.object_detection.boxes.f_boxes import bbox_iou_v3, ltrb2xywh, xywh2ltrb
from ftools.ai.calc.f_calc_adv import f_cre_grid_cells

from ftools.ai.picture.f_show import f_show_od_ts4plt_v3
import numpy as np
import torch.nn.functional as F


@torch.no_grad()
def match4yolox(gltrb_b, glabels_b, num_classes,
                pcls_b, p_xywh_input_b, p_ltrb_input_b, pconf_b,
                strides_match_input,
                img_ts=None, is_visual=False, center_radius=2.5):
    '''
    这里的计算只用于找GT simOTA
    :return:
    '''
    ngt = len(glabels_b)
    dim = len(strides_match_input)

    p_xywh_input_3d = p_xywh_input_b.unsqueeze(0).repeat(ngt, 1, 1)  # torch.Size([12, 8400, 4])
    # torch.Size([12, 8400])
    radius_ts_input_3d = (strides_match_input * center_radius).unsqueeze(0).repeat(ngt, 1)

    # glabels_b.unsqueeze(1).repeat(1, dim, 1)
    gltrb_i_b_3d = gltrb_b.unsqueeze(1).repeat(1, dim, 1)
    l = gltrb_i_b_3d[..., 0]
    t = gltrb_i_b_3d[..., 1]
    r = gltrb_i_b_3d[..., 2]
    b = gltrb_i_b_3d[..., 3]

    # --- 是否框内条件 --- torch.Size([12, 8400])
    mask_col_lr = torch.logical_and(p_xywh_input_3d[..., 0] >= l, p_xywh_input_3d[..., 0] <= r)
    mask_row_tb = torch.logical_and(p_xywh_input_3d[..., 1] >= t, p_xywh_input_3d[..., 1] <= b)
    mask_in_gtboxes_1d = torch.logical_and(mask_col_lr, mask_row_tb).any(0)
    # flog.debug('mask_in_gtboxes %s', mask_in_gtboxes.sum())
    # mask_2d = mask_in_gtboxes

    # (nn) --- 中心格子半径条件 ---
    gxywh_b_3d = ltrb2xywh(gltrb_i_b_3d)
    mask_radius_1d = torch.logical_and(
        torch.abs(p_xywh_input_3d[..., 0] - gxywh_b_3d[..., 0]) < radius_ts_input_3d,
        torch.abs(p_xywh_input_3d[..., 1] - gxywh_b_3d[..., 1]) < radius_ts_input_3d).any(0)

    # flog.debug('mask_radius %s', mask_radius.sum())

    # 1d
    mask_in_radius_or = torch.logical_or(mask_in_gtboxes_1d, mask_radius_1d)  # 或对小目标进行匹配
    # num_pos_ = mask_in_radius_or.sum()
    # 满足的几乎必选
    mask_in_radius_and = torch.logical_and(mask_in_gtboxes_1d, mask_radius_1d)

    # 所有的GT 与 侯选人 进行IOU
    iou = bbox_iou_v3(gltrb_b, p_ltrb_input_b, mode='iou', is_aligned=False)
    c_iou = -torch.log(iou + 1e-8)

    # 正例 cls 进行bce
    gcls4cost = F.one_hot(glabels_b.to(torch.int64) - 1, num_classes).float() \
        .unsqueeze(1).repeat(1, dim, 1)

    _pcls_conf_sigmoid = pcls_b.sigmoid() * pconf_b.sigmoid().unsqueeze(-1)
    pcls_conf_sigmoid_ngt = _pcls_conf_sigmoid.unsqueeze(0).repeat(ngt, 1, 1)
    # 这个有 sum
    c_cls = f_bce_loss(pcls_conf_sigmoid_ngt.sqrt_(),
                       gcls4cost, reduction='none').sum(-1)
    del pcls_conf_sigmoid_ngt
    del _pcls_conf_sigmoid

    # 使mask_in_radius的损失尽最小 优先选择框内和半径内的正例 (ngt,n侯造人)
    cost = c_cls + 3.0 * c_iou \
           + 100000.0 * torch.logical_not(mask_in_radius_and).unsqueeze(0).repeat(ngt, 1) \
           + 100000.0 * torch.logical_not(mask_in_radius_or).unsqueeze(0).repeat(ngt, 1)

    iou_top_val, _ = torch.topk(iou, 10, dim=-1)
    # ngt选取正例的个数 [ngt] 向下取整
    dynamic_ks = torch.clamp(iou_top_val.sum(1).int(), min=1)

    mask_pos_b = torch.zeros_like(mask_in_radius_and, dtype=torch.bool)
    gcls_b_res = torch.zeros_like(pcls_b,dtype=torch.float)
    gltrb_b_res = torch.zeros_like(p_ltrb_input_b)
    # 还是有可能重复(一个框属于多个GT) 是否解决重复问题
    for i in range(ngt):
        # largest 最小的 [nks个]
        _, index = torch.topk(cost[i], dynamic_ks[i], dim=-1, largest=False)
        mask_pos_b[index] = True
        gcls_b_res[index, glabels_b[i] - 1] = 1. * iou[i, index]
        gltrb_b_res[index] = gltrb_b[i]

    del c_cls, c_iou, cost, iou,

    if is_visual:
        flog.debug('dynamic_ks %s', dynamic_ks.sum())
        flog.debug('num_pos %s\n', mask_pos_b.sum())
        p_ltrb_input_pos = p_ltrb_input_b[mask_pos_b]
        f_show_od_ts4plt_v3(img_ts, g_ltrb=gltrb_b.cpu(),
                            g_texts=glabels_b.cpu().tolist(),
                            p_ltrb=p_ltrb_input_pos.cpu(),
                            is_normal=True,
                            )
    return mask_pos_b, gcls_b_res, gltrb_b_res


def decode_yolox(pt_xywh_b, grids_t):
    '''
    解码出来是特图
    :param pt_xywh_b:  必须 c 是最后一维
    :return: 输出原图归一化
    '''
    # 单一格子偏移 + 特图格子偏移
    p_xy_t = pt_xywh_b[..., :2] + grids_t
    p_wh_t = pt_xywh_b[..., 2:].exp()
    p_xywh_t = torch.cat([p_xy_t, p_wh_t], -1)
    return p_xywh_t


def match4atss(gltrb_i_b, anc_ltrb_i, nums_dim_t_list, num_atss_topk=9, glabels_b=None,
               img_ts=None, is_visual=False):
    '''
    这里默认都是 input 尺寸 且是batch
    核心作用:
        1. 使正例框数量都保持一致 保障小目标也能匹配到多个anc
        2. 用最大一个iou的均值和标准差,计算阀值,用IOU阀值初选正样本
        3. 确保anc中心点在gt框中

    :param gltrb_i_b:
    :param anc_ltrb_i:
    :param anc_ltrb_i:
    :param nums_dim_t_list:
        [1600, 400, 100] 这个是每个特图对应的维度数 用于索引 如果只有一层可以优化掉
    :param num_atss_topk: # 这个 topk = 初选个数 要 * 该层的anc数
    :param glabels_b: 暂时没用 可视化
    :param img_ts: 可视化
    :param is_visual:  可视化
    :return:
        mask_pos : [2100] 正例mask
        anc_max_iou: [2100] anc 对应的最大IOU值
        g_pos_index: [2100] anc 对应GT的索引
    '''

    def _force_set(device, ious_ag, mask_pos4all, mask_pos4distances, num_atss_topk):
        # 强制以IOU匹配 num_atss_topk 个   [2100, ngt] -> [2100] -> [nnn] ^^ -> tuple([n_nogt])
        indexes = torch.where(mask_pos4all.sum(0) == 0)[0]
        _mask = torch.zeros_like(ious_ag, dtype=torch.bool, device=device)

        for ii in indexes:
            # [2100, ngt] -> [2100,1] -> [2100]
            _mask_dis = mask_pos4distances[:, ii].squeeze(-1)
            # [2100,ngt] -> [nnnn]
            _iou_s = ious_ag[_mask_dis, ii]
            max_index = _iou_s.topk(num_atss_topk)[1]
            _m = torch.zeros_like(_iou_s, dtype=torch.bool)
            _m[max_index] = True
            _mask[_mask_dis, ii] = _m

        return _mask

    device = gltrb_i_b.DEVICE

    # 计算 iou
    anc_xywh_i = ltrb2xywh(anc_ltrb_i)
    # num_anc = anc_xywh_i.shape[0]
    # (anc 个,boxes 个) torch.Size([3, 10647])
    ious_ag = bbox_iou_v3(anc_ltrb_i, gltrb_i_b)
    num_gt = gltrb_i_b.shape[0]  # 正样本个数

    # 全部ANC的距离
    gxywh_i_b = ltrb2xywh(gltrb_i_b)
    # 中间点绝对距离 多维广播 (anc 个,boxes 个)  torch.Size([32526, 7])
    distances = (anc_xywh_i[:, None, :2] - gxywh_i_b[None, :, :2]).pow(2).sum(-1).sqrt()

    # 每层 anc 数是一致的
    # num_atss_topk = 9  # 这个 topk = 初选个数 要 * 该层的anc数

    idxs_candidate = []  # 这个用来保存最一层所匹配的最小距离anc的索引  每层9个
    index_start = 0  # 这是每层的anc偏移值
    for i, num_dim_feature in enumerate(nums_dim_t_list):  # [24336, 6084, 1521, 441, 144]
        '''每一层的每一个GT选 topk * anc数'''
        index_end = index_start + num_dim_feature
        # 取出某层的所有anc距离  中间点绝对距离 (anc 个,boxes 个)  torch.Size([32526, 7]) -> [nn, 7]
        distances_per_level = distances[index_start:index_end, :]
        # 确认该层的TOPK 不能超过该层总 anc 数 这里是一个数
        topk = min(num_atss_topk, num_dim_feature)
        # 选 topk个最小的 每个gt对应对的anc的index torch.Size([24336, box_n])---(anc,gt) -> torch.Size([topk, 1])
        _, topk_idxs_per_level = distances_per_level.topk(topk, dim=0, largest=False)  # 只能在某一维top
        idxs_candidate.append(topk_idxs_per_level + index_start)
        index_start = index_end

    # 用于计算iou均值和方差 候选人，候补者；应试者 torch.Size([405, 1])
    idxs_candidate = torch.cat(idxs_candidate, dim=0)
    '''--- 选出每层每个anc对应的距离中心最近topk iou值 ---'''
    # ***************这个是ids选择 这个是多维筛选 ious---[anc,ngt]    [405, ngt] [0,1...ngt]-> [405,ngt]
    ious_candidate = ious_ag[idxs_candidate, torch.arange(num_gt)]  # 这里是index 蒙板取数的方法
    mask_pos4distances = torch.zeros_like(distances, device=device, dtype=torch.bool)
    # [2000,ngt]
    mask_pos4distances[idxs_candidate, torch.arange(idxs_candidate.shape[1])] = True

    '''--- 用最大一个iou的均值和标准差,计算阀值 ---'''
    # 统计每一个 GT的均值 std [ntopk,ngt] -> [ngt] 个
    _iou_mean_per_gt = ious_candidate.mean(dim=0)  # 除维
    _iou_std_per_gt = ious_candidate.std(dim=0)
    _iou_thresh_per_gt = _iou_mean_per_gt + _iou_std_per_gt
    '''--- 用IOU阀值初选正样本 ---'''
    # torch.Size([32526, 1]) ^^ ([ngt] -> [1,ngt]) -> [32526,ngt]
    mask_pos4iou = ious_ag >= _iou_thresh_per_gt.unsqueeze(0)  # 核心是这个选

    '''--- 中心点需落在GT中间 需要选出 anc的中心点-gt的lt为正, gr的rb-anc的中心点为正  ---'''
    # torch.Size([32526, 1, 2])
    dlt = anc_xywh_i[:, None, :2] - gltrb_i_b[None, :, :2]
    drb = gltrb_i_b[None, :, 2:] - anc_xywh_i[:, None, :2]
    # [32526, 1, 2] -> [32526, 1, 4] -> [32526, 1]
    mask_pos4in_gt = torch.all(torch.cat([dlt, drb], dim=-1) > 0.01, dim=-1)
    mask_pos4all = torch.logical_and(torch.logical_and(mask_pos4distances, mask_pos4iou), mask_pos4in_gt)

    '''--- 生成最终正例mask [32526, ngt] -> [32526] ---'''
    # 多个GT可能对应 不同的index 需要合并
    msak_pos_1d = mask_pos4all.any(1)

    '''--- 确定anc匹配 一个锚框被多个真实框所选择，则其归于iou较高的真实框  ---'''
    # (anc 个,boxes 个) torch.Size([3, 10647])
    anc_max_iou, g_index = ious_ag.max(dim=1)  # 存的是 bboxs的index

    ''' 这里是强制代码 '''
    if msak_pos_1d.sum() == 0 or (mask_pos4iou.sum(0) == 0).any() or (mask_pos4all.sum(0) == 0).any():
        '''
        msak_pos_1d 该图所有GT都没有匹配GT,概率较低
        mask_pos4iou 该图存在的通过IOU高斯值 没有匹配到的GT
        mask_pos4all 最终IOU+框内条件 存在有没有匹配到的GT
        '''
        # mask_pos4all mask_pos4iou mask_pos4distances
        # flog.debug('有问题 mask_pos4iou= %s, mask_pos4iou= %s, mask_pos4all= %s '
        #            % (mask_pos4distances.sum(0), mask_pos4iou.sum(0), mask_pos4all.sum(0)))
        # 强制修正 1阶段 选5个IOU最大的 再进行框内逻辑
        _mask = _force_set(device, ious_ag, mask_pos4all, mask_pos4distances, 5)
        # 更新 两个mask
        mask_pos4all[_mask] = True
        mask_pos4all = torch.logical_and(mask_pos4all, mask_pos4in_gt)  # 优先框内
        # 1阶段未修复的 2阶段直接取两个IOU最大的匹配
        if (mask_pos4all.sum(0) == 0).any():
            # 二次修正 单修就很难再进来
            # flog.error('二次修正,强制选一个 mask_pos4all= %s' % (mask_pos4all.sum(0)))
            _mask = _force_set(device, ious_ag, mask_pos4all, mask_pos4distances, 2)
            mask_pos4all[_mask] = True
        msak_pos_1d = mask_pos4all.any(1)
        # 修正强制IOU 对应关系  解决iou小 最终被强制修订  这里不能再用 anc_max_iou值
        ious_ag[mask_pos4all] = 999
        anc_max_iou, g_index = ious_ag.max(dim=1)  # 存的是 bboxs的index
        # flog.debug('修正后匹配的GT mask_pos4all= %s ' % (mask_pos4all.sum(0)))
        # is_visual = True

    if is_visual or msak_pos_1d.sum() == 0 or (mask_pos4all.sum(0) == 0).any():
        # 修正后还不行的进来 这里
        flog.error('双重修正后不可能没有 mask_pos4iou= %s, mask_pos4all= %s ' % (mask_pos4iou.sum(0), mask_pos4all.sum(0)))
        from ftools.ai.picture import f_show_od_ts4plt_v3
        # ***********  debug 可视  每层选9个匹配27(3*9)个正例可视化  *****************
        # 多个gt 对应一个anc 进行转换显示
        dim, ngt = mask_pos4distances.shape
        # [2100,4] -> [ngt,2100,4]
        anc_ltrb_i_pos = anc_ltrb_i.view(1, dim, 4).repeat(ngt, 1, 1)[mask_pos4distances.t()]
        f_show_od_ts4plt_v3(img_ts, g_ltrb=gltrb_i_b.cpu(),
                            # p_ltrb=anc_ltrb_i[mask_pos_distances],
                            p_ltrb=anc_ltrb_i_pos.cpu(),
                            is_normal=True,
                            )

        # ***********  可视化IOU  *****************
        # mask_pos 已经进行max iou 筛选对应的GT
        anc_ltrb_i_pos = anc_ltrb_i.view(1, dim, 4).repeat(ngt, 1, 1)[mask_pos4iou.t()]
        f_show_od_ts4plt_v3(img_ts, g_ltrb=gltrb_i_b.cpu(),
                            p_ltrb=anc_ltrb_i_pos.cpu(),
                            is_normal=True,
                            )

        # ***********  可视化  多重过滤(IOU正态阀值,框内,已对应最大GT)后个正例可视化  *****************
        # mask_pos 已经进行max iou 筛选对应的GT
        f_show_od_ts4plt_v3(img_ts, g_ltrb=gltrb_i_b.cpu(),
                            p_ltrb=anc_ltrb_i[msak_pos_1d].cpu(),
                            is_normal=True,
                            )

    return msak_pos_1d, anc_max_iou, g_index


def decode4nanodet(anc_xy_t, p_tltrb_t, max_size_hw=None):
    '''
    p -> g
    :param anc_xy_t: torch.Size([2100, 2])
    :param p_tltrb_t: torch.Size([3, 2100, 4])
    :param max_size_hw: 预测时使用 这个在归一化后使用 clamp是一样的
    :return:
    '''
    assert anc_xy_t.shape[-1] == 2, 'anc_xy_t 输入应为xy shape = %s' % anc_xy_t.shape
    # torch.Size([3, 2100])
    x1 = anc_xy_t[..., 0] - p_tltrb_t[..., 0]
    y1 = anc_xy_t[..., 1] - p_tltrb_t[..., 1]
    x2 = anc_xy_t[..., 0] + p_tltrb_t[..., 2]
    y2 = anc_xy_t[..., 1] + p_tltrb_t[..., 3]
    if max_size_hw is not None:
        x1 = x1.clamp(min=0, max=max_size_hw[1])
        y1 = y1.clamp(min=0, max=max_size_hw[0])
        x2 = x2.clamp(min=0, max=max_size_hw[1])
        y2 = y2.clamp(min=0, max=max_size_hw[0])
    # torch.Size([3, 2100]) x4 torch.Size([3, 2100,4])
    return torch.stack([x1, y1, x2, y2], -1)


def encode4nanodet(anc_xy_t, g_ltrb_t, max_val, eps=0.1, is_debug=False):
    '''
    编码针对特图
    :param anc_xy_t:  torch.Size([2100, 2])
    :param g_ltrb_t:  torch.Size([3, 2100, 4])
    :param max_val: 限制匹配的正例 最大距离 在0~7 之内
    :param is_debug:  用于查看 GT 与 匹配的点 的ltrb距离是否会超过7
    :param eps:
    :return:
    '''
    left = anc_xy_t[:, 0] - g_ltrb_t[..., 0]
    top = anc_xy_t[:, 1] - g_ltrb_t[..., 1]
    right = g_ltrb_t[..., 2] - anc_xy_t[:, 0]
    bottom = g_ltrb_t[..., 3] - anc_xy_t[:, 1]
    g_tltrb_t = torch.stack([left, top, right, bottom], -1)
    if is_debug:
        # flog.debug('注意是正例 最大值应该在7以内 min=%f  max=%f' % (g_tltrb_t.min(), g_tltrb_t.max()))
        pass
    if max_val is not None:
        g_tltrb_t = g_tltrb_t.clamp(min=0, max=max_val - eps)
    return g_tltrb_t


def match_yolo1_od(g_ltrb_input_b, g_labels_b, size_wh_t_ts, device, cfg, img_ts_input):
    '''
    匹配 gyolo 如果需要计算IOU 需在这里生成
    :param g_ltrb_input_b: ltrb
    :return:
    '''
    num_gt = g_ltrb_input_b.shape[0]
    g_txywh_t, weights, indexs_colrow_t = encode_yolo1_od(g_ltrb_input_b, size_wh_t_ts, cfg)

    g_cls_b_ = torch.zeros((size_wh_t_ts[1], size_wh_t_ts[0], cfg.NUM_CLASSES), device=device)
    g_weight_b_ = torch.zeros((size_wh_t_ts[1], size_wh_t_ts[0], 1), device=device)
    g_txywh_t_b_ = torch.zeros((size_wh_t_ts[1], size_wh_t_ts[0], 4), device=device)

    labels_index = (g_labels_b - 1).long()
    indexs_colrow_t = indexs_colrow_t.long()  # index需要long类型

    for i in range(num_gt):
        g_cls_b_[indexs_colrow_t[i, 1], indexs_colrow_t[i, 0], labels_index[i]] = 1  # 构建 onehot
        g_weight_b_[indexs_colrow_t[i, 1], indexs_colrow_t[i, 0]] = weights[i]
        g_txywh_t_b_[indexs_colrow_t[i, 1], indexs_colrow_t[i, 0]] = g_txywh_t[i]

    g_cls_b_ = g_cls_b_.reshape(-1, cfg.NUM_CLASSES)
    g_weight_b_ = g_weight_b_.reshape(-1, 1)
    g_txywh_t_b_ = g_txywh_t_b_.reshape(-1, 4)

    '''可视化验证'''
    if cfg.IS_VISUAL:
        mask_pos_1d = (g_weight_b_ > 0).any(-1)  # [169]

        # [2] -> [1,2] -> [ngt,2]
        sizes_wh_t_ts = size_wh_t_ts.unsqueeze(0).repeat(num_gt, 1)

        flog.debug('size_wh_t_ts = %s', size_wh_t_ts)
        flog.debug('g_txywh_t = %s', g_txywh_t)
        flog.debug('indexs_colrow_t = %s', indexs_colrow_t)
        flog.debug('对应index = %s', indexs_colrow_t[0, 1] * size_wh_t_ts[0] + indexs_colrow_t[0, 0])
        flog.debug('对应index = %s', torch.where(g_weight_b_ > 0))

        flog.debug('g_ltrb_input_b = %s', g_ltrb_input_b)

        grid_wh = [size_wh_t_ts[0].item(), size_wh_t_ts[1].item()]
        # 预测时需要sigmoid  这里的 g_txywh_t_b_ 已 sigmoid
        p_ltrb_t = decode_yolo1_od(p_txywh_t_sigmoidxy=g_txywh_t_b_, grid_xy=grid_wh)
        p_ltrb_t_pos = p_ltrb_t[mask_pos_1d]

        # 特图 -> input
        # img_wh_ts_x2 = torch.tensor(img_np.shape[:2][::-1], device=device).repeat(2)
        p_ltrb_input_pos = p_ltrb_t_pos * cfg.STRIDE

        flog.debug('p_ltrb_input_pos = %s', p_ltrb_input_pos)
        flog.debug(' ----------------------------------------- ')
        f_show_od_ts4plt_v3(img_ts=img_ts_input,
                            g_ltrb=g_ltrb_input_b.cpu(),
                            p_ltrb=p_ltrb_input_pos.cpu(),
                            is_recover_size=False,
                            is_normal=True,  # 图形归一化恢复
                            grid_wh_np=size_wh_t_ts.cpu().numpy()
                            )

    return g_cls_b_, g_weight_b_, g_txywh_t_b_


def encode_yolo1_od(g_ltrb_input_b, size_wh_t_ts, cfg):
    # ltrb -> xywh 原图归一化   编码xy与yolo2一样的
    g_xywh_input = ltrb2xywh(g_ltrb_input_b)
    g_xywh_t = g_xywh_input / cfg.STRIDE
    cxys_t = g_xywh_t[:, :2]
    whs_t = g_xywh_t[:, 2:]
    whs_one = whs_t / size_wh_t_ts

    # 转换到特图的格子中
    indexs_colrow_t = cxys_t.floor()
    g_txy_t = cxys_t - indexs_colrow_t
    g_twh_t = whs_t.log()
    g_txywh_t = torch.cat([g_txy_t, g_twh_t], dim=-1)

    # 值在 1~2 之间 放大小的
    weights = 2.0 - torch.prod(whs_one, dim=-1)

    return g_txywh_t, weights, indexs_colrow_t


def decode_yolo1_od(p_txywh_t_sigmoidxy, grid_wh):
    '''
    解码出来是特图
    :param p_txywh_t_sigmoidxy:  必须 c 是最后一维
    :return: 输出原图归一化
    '''
    device = p_txywh_t_sigmoidxy.DEVICE
    # 单一格子偏移 + 特图格子偏移
    p_xy_t = p_txywh_t_sigmoidxy[..., :2] \
             + f_cre_grid_cells((grid_wh[1], grid_wh[0]), is_swap=True, num_repeat=1).to(device)
    p_wh_t = p_txywh_t_sigmoidxy[..., 2:].exp()
    p_xywh_t = torch.cat([p_xy_t, p_wh_t], -1)
    p_ltrb_t = xywh2ltrb(p_xywh_t)
    return p_ltrb_t


def match_fcos4od(g_ltrb_input_b, g_labels_b, dim_total, cfg, img_ts=None, ):
    '''
    只计算半径正例  添加 g_ltrbs在最后
    center_ness == 1?
    '''
    device = g_ltrb_input_b.DEVICE
    g_xywh_input = ltrb2xywh(g_ltrb_input_b)

    # gt:  cls centerness offltrb radius iou area keypoints*2 kpmask +ltrb
    _area_b_ = torch.empty(dim_total, device=device)  # 这个用于记录当前图片 多个框的面积
    _area_b_[:] = 999999999999.  # 面积赋个极大值 float最大值   sys.maxsize int最大值
    g_cls_b_ = torch.zeros((dim_total, cfg.NUM_CLASSES), device=device)  # 全为背景置1
    g_centerness_b_ = torch.zeros((dim_total, 1), device=device)
    g_tltrb_input_b_ = torch.zeros((dim_total, 4), device=device)
    positive_radius_b_ = torch.zeros((dim_total, 1), device=device)  # 半径正例
    g_ltrb_input_b_ = torch.zeros((dim_total, 4), device=device)  # 4

    # degbug 调试异常匹配
    # if cfg.tcfg_temp2 in [39, 57, 206, 226, 239]:
    #     f_show_od_ts4plt_v3(img_ts, gboxes_ltrb=g_ltrb_input_b, is_normal=True)
    #     长宽比过大 导致阀值过大 匹配不了大特图, 小特图又没有点
    # print('123')
    # pass

    # 遍历每一个标签, 的每一层的格子  找出格子是否在预测框中, 并记录差异
    for i in range(len(g_labels_b)):
        l = g_ltrb_input_b[i, 0]
        t = g_ltrb_input_b[i, 1]
        r = g_ltrb_input_b[i, 2]
        b = g_ltrb_input_b[i, 3]
        area_gt_input = torch.prod(g_xywh_input[i][2:])  # 连乘

        index_colrow_input = []
        scale_thresholds = []
        radius = []

        # 特图 -> input图 这个可以复用
        for j, s in enumerate(cfg.STRIDES):
            # 每层网格对应特图的 网格点
            _grids = f_mershgrid(fix=cfg.t_grids_hw[j][0], col=cfg.t_grids_hw[j][1], is_no_swap=False).to(device)
            _grids = _grids * s + s // 2
            # dim, _ = _grids.shape
            index_colrow_input.append(_grids)

            _scale = torch.empty_like(_grids, device=device)
            _scale[:, 0] = cfg.SCALE_THRESHOLDS[j]
            _scale[:, 1] = cfg.SCALE_THRESHOLDS[j + 1]
            scale_thresholds.append(_scale)

            # [nn]
            _radius = torch.empty_like(_grids[:, 0], device=device)
            _radius[:] = cfg.MATCH_RADIUS * s  # 半径阀值
            radius.append(_radius)

        # _start_indexes = []
        # _s = 0
        # for _i in range(5):
        #     _s += len(index_colrow_input[_i])
        #     _start_indexes.append(_s)

        # (nn,2)
        index_colrow_input = torch.cat(index_colrow_input, 0)
        scale_thresholds = torch.cat(scale_thresholds, 0)
        radius = torch.cat(radius, 0)  # [nn] # 这个根据 cfg.MATCH_RADIUS 算出来的 每层固定值

        # (nn) # --- 是否框内条件 ---
        mask_col_lr = torch.logical_and(index_colrow_input[:, 0] >= l, index_colrow_input[:, 0] <= r)
        mask_row_tb = torch.logical_and(index_colrow_input[:, 1] >= t, index_colrow_input[:, 1] <= b)
        mask_in_gtboxes = torch.logical_and(mask_col_lr, mask_row_tb)

        # (nn) --- 中心格子半径条件 ---
        # 网格点在右 到中心的距离
        off_rtxy_input = index_colrow_input - g_xywh_input[i, :2].unsqueeze(0)
        # 网格点在左 到中心的距离
        off_ltxy_input = g_xywh_input[i, :2].unsqueeze(0) - index_colrow_input
        off_lrtxy_input = torch.cat([off_rtxy_input, off_ltxy_input], -1)
        off_lrtxy_input_max, _ = torch.max(off_lrtxy_input, -1)
        mask_radius = off_lrtxy_input_max < radius

        # 是等价的
        # mask_radius = torch.logical_and(torch.abs(index_colrow_input[:, 0] - g_xywh_input[i, 0]) < radius,
        #                                 torch.abs(index_colrow_input[:, 1] - g_xywh_input[i, 1]) < radius)

        ''' (nn,2) 这是匹配的结果 每层对应特图网格到 input ltrb的距离  lt框内全为正  rb框内全为正  '''
        # torch.Size([3614, 2])  ^^(1,2) =
        off_lt_input = index_colrow_input - g_ltrb_input_b[i, :2].unsqueeze(0)  # 恢复权重为-1
        off_rb_input = g_ltrb_input_b[i, 2:].unsqueeze(0) - index_colrow_input  # 恢复权重为1
        # 后续通过IOU计算LOSS 这里不进行匹配 用于计算最大边,确定匹配到哪一层 和centerness
        off_ltrb_input = torch.cat([off_lt_input, off_rb_input], -1)  # (nn,4)
        off_ltrb_input_max, _ = torch.max(off_ltrb_input, -1)  # (nn,4) -> (nn)
        # 这个也是框内正例
        # off_ltrb_input_min, _ = torch.min(off_ltrb_input, -1)  # (nn,4) -> (nn)
        # mask_in_gtboxes1 = off_ltrb_input_min > 0
        # [340, 2] ->

        # (nn)  # --- 层阀值条件 ---
        mask_in_ceng = torch.logical_and(off_ltrb_input_max > scale_thresholds[:, 0],
                                         off_ltrb_input_max <= scale_thresholds[:, 1])

        # --- 面积条件 小于的选中 ---
        mask_area = _area_b_ > area_gt_input

        # 框内正例
        mask_kuang = torch.logical_and(torch.logical_and(mask_in_gtboxes, mask_in_ceng), mask_area)
        # 半径正例
        mask = torch.logical_and(mask_kuang, mask_radius)

        # (nn) -> (nn,1)
        lr_min = torch.min(off_ltrb_input[:, ::2], -1)[0]
        lr_max = torch.max(off_ltrb_input[:, ::2], -1)[0]
        tb_min = torch.min(off_ltrb_input[:, 1::2], -1)[0]
        tb_max = torch.max(off_ltrb_input[:, 1::2], -1)[0]
        # center_ness = torch.sqrt(lr_min / lr_max * tb_min / tb_max)
        # sqrt不能为0 这里可以不用 clamp
        center_ness = torch.sqrt((lr_min * tb_min) / (lr_max * tb_max))
        # center_ness[center_ness.isinf()] = 1.
        center_ness[center_ness.isnan()] = 0.
        center_ness.unsqueeze_(-1)

        g_cls_b_[mask, g_labels_b[i].long() - 1] = 1.  # 这个需要保留以前的值 本次只复写需要的
        g_centerness_b_[mask_kuang] = center_ness[mask_kuang]  # 这个大于0 与 positive_radius_b_ 等价
        positive_radius_b_[mask] = 1
        _area_b_[mask] = area_gt_input  # 面积更新
        g_tltrb_input_b_[mask] = off_ltrb_input[mask]
        g_ltrb_input_b_[mask] = g_ltrb_input_b[i]

    # (g_centerness_b_ > 0.).sum().cpu().item()==(g_cls_b_ == 1).sum().cpu().item()

    # debug
    # if (g_centerness_b_ > 0.).sum().cpu().item() == 0:
    #     print(cfg.tcfg_temp2)
    #     cfg.IS_VISUAL = True
    # cfg.tcfg_temp2 += 1

    if cfg.IS_VISUAL:
        cfg.IS_VISUAL = False
        ''' 可视化匹配最大的ANC '''
        import matplotlib.pyplot as plt
        from f_tools.pic.enhance.f_data_pretreatment4np import f_recover_normalization4ts

        _img_ts = img_ts.clone()
        _img_ts = f_recover_normalization4ts(_img_ts)
        img_np = _img_ts.cpu().numpy().astype(np.uint8).transpose((1, 2, 0))
        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        # f_show_od_np4plt_v2(img_np, gboxes_ltrb=g_ltrb_input_b)
        # plt.imshow(img_np)
        # plt.show()
        # 生成随机颜色
        # COLOR_RANDOM_CV = f_random_color4cv(cfg.NUM_CLASSES)

        print('框内 %s  半径 %s' % ((g_centerness_b_ > 0.).sum().cpu().item(), (g_cls_b_ == 1).sum().cpu().item()))
        start_index = 0
        num_gt = 0

        for j in range(len(cfg.STRIDES)):
            # 遍历每层的 row col
            for row in range(cfg.t_grids_hw[j][0]):
                for col in range(cfg.t_grids_hw[j][1]):
                    # 网络在原图的坐标
                    x = col * cfg.STRIDES[j] + cfg.STRIDES[j] // 2
                    y = row * cfg.STRIDES[j] + cfg.STRIDES[j] // 2
                    # start_index+(row* w +col)
                    index = (row * cfg.t_grids_hw[j][1] + col) + start_index

                    # if g_centerness_b_[index] > 0.:  # 这个是框内
                    if (g_cls_b_[index] == 1).any():  # 这个半径正例

                        # 正例
                        off_l, off_t, off_r, off_b = g_tltrb_input_b_[index]
                        # 网络位置 求GT的位置
                        xmin = int(x - off_l)
                        ymin = int(y - off_t)
                        xmax = int(x + off_r)
                        ymax = int(y + off_b)

                        gcls = np.argmax(g_cls_b_[index, :].cpu(), axis=-1)
                        mess = '%s' % (int(gcls))

                        # 这个是网格点 这个是用CV 画 np cv画参考
                        cv2.circle(img_np, (int(x), int(y)), 5, COLOR_CV['green'], -1)
                        cv2.rectangle(img_np, (xmin, ymin), (xmax, ymax), (0, 0, 255), 2)
                        cv2.rectangle(img_np, (int(xmin), int(abs(ymin) - 15)),
                                      (int(xmin + (xmax - xmin) * 0.55), int(ymin)), (255, 0, 0), -1)
                        cv2.putText(img_np, mess, (int(xmin), int(ymin)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                        num_gt += 1
            start_index += (cfg.t_grids_hw[j][0] * cfg.t_grids_hw[j][1])

        cv2.putText(img_np, 'num_gt=' + str(num_gt), (0, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.5, color=(0, 255, 0), thickness=2)
        f_show_od_np4plt_v2(img_np)  # 这个显示  bgr 有色差
        # cv2.imshow('image', img_np)
        # cv2.waitKey(0)

    return g_cls_b_, g_centerness_b_, g_tltrb_input_b_, positive_radius_b_, g_ltrb_input_b_


def decode_fcos4box(cfg, p_tltrb_input, toone_wh_ts_input, is_to_one=False):
    '''
    size_toone_wh_ts : torch.Size([batch, 2])
    '''
    device = p_tltrb_input.DEVICE
    weight = torch.tensor([-1, -1, 1, 1], device=device).view(1, 1, -1)

    index_colrow = []  # 这个是表示对应特图上的点, 感受野中心点
    # start_index = 0
    for j, s in enumerate(cfg.STRIDES):
        # 这里将特图网格转换到input网格
        _grids = f_mershgrid(fix=cfg.t_grids_hw[j][0], col=cfg.t_grids_hw[j][1], is_no_swap=False).to(device)
        _grids = _grids * s + s // 2  # 每层对应的特图感受野块
        index_colrow.append(_grids)
        # start_index += (grid_wh[1] * grid_wh[0])

    index_colrow = torch.cat(index_colrow, 0)
    index_colrow_x2 = index_colrow.repeat(1, 2).unsqueeze(0)
    index_colrow_x5 = index_colrow.repeat(1, cfg.NUM_KEYPOINTS).unsqueeze(0)
    p_ltrb_input = p_tltrb_input * weight + index_colrow_x2  # 得到真实 ltrb

    if is_to_one:  # 是否特图尺寸  默认否为运行进行 归一化
        p_ltrb_one = p_ltrb_input / toone_wh_ts_input.repeat(1, 2).unsqueeze(1)  # 归一化尺寸
        return p_ltrb_one
    return p_ltrb_input
