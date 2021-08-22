import torch
import torch.nn.functional as F
import numpy as np
from torch import nn


def fquality_focal_loss(pcls, gcls, score, beta=2.0):
    '''
    支持0~1连续标签
    :param pcls: torch.Size([3, 2100, 80])
    :param gcls: torch.Size([3, 2100, 80])
    :param score: torch.Size([3, 2100])
    :param beta:
    :return: torch.Size([3, 2100, 80])
    '''
    gcls_score = gcls * score.unsqueeze(-1)
    loss_bce = F.binary_cross_entropy_with_logits(pcls, gcls_score, reduction='none')
    scale_factor = (pcls.sigmoid() - gcls_score).abs().pow(beta)
    loss = loss_bce * scale_factor
    return loss


def focalloss_fast(pcls_sigmoid, gcls, alpha=0.25, gamma=2.0):
    '''
    gcls只支持0或1标签
    '''
    eps = torch.finfo(torch.float16).eps
    pcls_sigmoid = pcls_sigmoid.clamp(min=eps, max=1 - eps)
    pt = pcls_sigmoid * gcls + (1.0 - pcls_sigmoid) * (1.0 - gcls)
    w = alpha * gcls + (1.0 - alpha) * (1.0 - gcls)
    loss = -w * torch.pow((1.0 - pt), gamma) * pt.log()
    return loss


def focalloss_center(pcls_sigmoid, gcls, alpha=2., beta=4.):
    '''
    支持0~1的连续标签 好像有损失上限
    '''
    eps = torch.finfo(torch.float16).eps
    pcls_sigmoid = pcls_sigmoid.clamp(min=eps, max=1 - eps)
    mask_pos_3d = gcls == 1
    mask_neg_3d = gcls != 1
    l_pos = -mask_pos_3d.float() * ((1.0 - pcls_sigmoid) ** alpha) * torch.log(pcls_sigmoid)
    l_neg = -mask_neg_3d.float() * ((1 - gcls) ** beta) * (pcls_sigmoid ** alpha) * torch.log(1.0 - pcls_sigmoid)
    return l_pos + l_neg


def fdistribution_focal_loss(pred, label, reduction='none'):
    '''
    通过 ce 使分布靠近GT的左右值   通过不同的权重使其回归到指定位置
    :param pred:  torch.Size([27, 8, 4])
    :param label: torch.Size([27, 4])
    :return:
        torch.Size([27, 4])

    pred:  2d:[n,8]  3d:[b,8,n]
    label: 2d:[n]    3d:[b,n] 值必须在在[0,7) 左闭右开
    # ---- 2d
    preg = torch.randint(0, 8, (3, 8)) + torch.rand((3, 8))
    print(preg)
    greg = torch.randint(0, 7, (3,)) + torch.rand(3)
    print(greg)
    loss = distribution_focal_loss(preg, greg)
    print(loss)

    # ---- 3d
    preg = torch.randint(0, 8, (3, 2, 8)) + torch.rand((3, 2, 8))
    preg = preg.permute(0, 2, 1) # (3, 2, 8) -> (3, 8, 2)
    print(preg)
    greg = torch.randint(0, 7, (3, 2)) + torch.rand(3, 2)
    print(greg)
    loss = distribution_focal_loss(preg, greg)
    print(loss)
    '''
    disl = label.long()  # 向下取整
    disr = disl + 1  # 向上取整

    # GT靠哪边哪边的权重就大
    wl = disr.float() - label  # GT距离左边的权限
    wr = label - disl.float()

    # torch.Size([3, 8400, 8])  ^^ torch.Size([3, 8400])
    loss = F.cross_entropy(pred, disl, reduction='none') * wl \
           + F.cross_entropy(pred, disr, reduction='none') * wr
    return loss  # torch.Size([24, 4])


def f_bce_loss(pconf_sigmoid, gconf, weight=1., reduction='none'):
    '''
    只支持二维
    :param pconf_sigmoid: 值必须为0~1之间 float
    :param gconf: 值为 float
    :return:
    '''
    eps = torch.finfo(torch.float16).eps
    pconf_sigmoid = pconf_sigmoid.clamp(min=eps, max=1 - eps)
    # loss = np.round(-(gconf * np.log(pconf) + (1 - gconf) * np.log(1 - pconf)), 4)
    loss = -(torch.log(pconf_sigmoid) * gconf + torch.log(1 - pconf_sigmoid) * (1 - gconf)) * weight
    return loss


class IOUloss(nn.Module):
    def __init__(self, reduction="none", loss_type="iou"):
        super(IOUloss, self).__init__()
        self.reduction = reduction
        self.loss_type = loss_type

    def forward(self, pred, target):
        assert pred.shape[0] == target.shape[0]

        pred = pred.view(-1, 4)
        target = target.view(-1, 4)
        tl = torch.max(
            (pred[:, :2] - pred[:, 2:] / 2), (target[:, :2] - target[:, 2:] / 2)
        )
        br = torch.min(
            (pred[:, :2] + pred[:, 2:] / 2), (target[:, :2] + target[:, 2:] / 2)
        )

        area_p = torch.prod(pred[:, 2:], 1)
        area_g = torch.prod(target[:, 2:], 1)

        en = (tl < br).type(tl.type()).prod(dim=1)
        area_i = torch.prod(br - tl, 1) * en
        iou = (area_i) / (area_p + area_g - area_i + 1e-16)

        if self.loss_type == "iou":
            loss = 1 - iou ** 2
        elif self.loss_type == "giou":
            c_tl = torch.min(
                (pred[:, :2] - pred[:, 2:] / 2), (target[:, :2] - target[:, 2:] / 2)
            )
            c_br = torch.max(
                (pred[:, :2] + pred[:, 2:] / 2), (target[:, :2] + target[:, 2:] / 2)
            )
            area_c = torch.prod(c_br - c_tl, 1)
            giou = iou - (area_c - area_i) / area_c.clamp(1e-16)
            loss = 1 - giou.clamp(min=-1.0, max=1.0)

        if self.reduction == "mean":
            loss = loss.mean()
        elif self.reduction == "sum":
            loss = loss.sum()

        return loss


''' -------------------------  ------------------------------ '''


# def quality_focal_loss(pred, target, beta=2.0):
#     assert len(target) == 2, """target for QFL must be a tuple of two elements,
#         including category label and quality label, respectively"""
#     # label denotes the category id, score denotes the quality score
#     label, score = target
#
#     # negatives are supervised by 0 quality score
#     pred_sigmoid = pred.sigmoid()
#     scale_factor = pred_sigmoid
#     zerolabel = scale_factor.new_zeros(pred.shape)
#     loss = F.binary_cross_entropy_with_logits(
#         pred, zerolabel, reduction='none') * scale_factor.pow(beta)
#
#     # FG cat_id: [0, num_classes -1], BG cat_id: num_classes
#     bg_class_ind = pred.size(1)
#     pos = torch.nonzero((label >= 0) & (label < bg_class_ind), as_tuple=False).squeeze(1)
#     pos_label = label[pos].long()
#     # positives are supervised by bbox quality (IoU) score
#     scale_factor = score[pos] - pred_sigmoid[pos, pos_label]
#     loss[pos, pos_label] = F.binary_cross_entropy_with_logits(
#         pred[pos, pos_label], score[pos],
#         reduction='none') * scale_factor.abs().pow(beta)
#
#     loss = loss.sum(dim=1, keepdim=False)
#     return loss
def t_fl():
    '''
    三种focalloss测试
    '''
    pcls = torch.arange(12, dtype=torch.float).reshape(1, 3, 4)
    gcls = torch.zeros_like(pcls)
    gcls[0][0][1] = 1
    gcls[0][1][2] = 1
    gcls[0][2][0] = 1
    # score = torch.rand_like(gcls)
    score = torch.ones_like(gcls)
    print(pcls.sigmoid())
    print(gcls * score)
    # loss1 = quality_focal_loss(pcls, gcls, score)
    # print(loss1)
    loss_gfl = fquality_focal_loss(pcls, gcls, score)
    print(loss_gfl)
    loss_center = focalloss_center(pcls.sigmoid(), gcls * score)
    print(loss_center)
    loss_fl = focalloss_fast(pcls.sigmoid(), gcls * score)
    print(loss_fl)


if __name__ == '__main__':
    torch.manual_seed(3)
    np.set_printoptions(suppress=True)
    torch.set_printoptions(linewidth=320, sci_mode=False, precision=5, profile='long')

    # t_fl()
    pass
