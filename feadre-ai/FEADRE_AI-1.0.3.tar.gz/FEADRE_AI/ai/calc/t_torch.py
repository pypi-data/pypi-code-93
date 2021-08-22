import torch
import numpy as np


def t_scatter(src):
    # det = torch.randn((1, 4), dtype=torch.float)
    # print(det.shape)
    # index = torch.tensor([[0, 2]])
    # res = src.scatter(1, index, det)
    # print(res)

    src = torch.zeros((1, 2, 6), dtype=torch.float)
    det = torch.tensor([[[2, 4, 6, 8]]], dtype=torch.float)
    print(det.shape)
    # index = torch.tensor([[[1, 0, 1, 0], ]])  # 1表示维度索引,位置表示赋值对应
    index = torch.zeros((1, 1, 6))
    index = torch.index_fill(index, -1, torch.arange(6), 1)

    # index = torch.tensor([[[1, 0, 1, 0], ]])
    res = src.scatter(1, index[..., :2].long(), det)
    # res = src.scatter(1, index, det)
    print(res)
    return res


def t_index_fill():
    batch = 2
    data_ts = torch.rand((batch, 3, 320, 320), dtype=torch.float)
    # res = torch.index_fill(data_ts, -1, torch.arange(2), 1)  # 最后一维,前两个
    res = torch.index_fill(data_ts, -1,
                           torch.tensor([[0, 1]]),
                           1)  # 最后一维,前两个
    print(res)


def t_slice():
    s = slice(1, 4, 2)  # 切片对象
    # print(s)

    a = torch.arange(16).view(4, 4)
    # print(fslice(a.shape[0], 2))
    print(a)

    print(a[::2, ::2])  # 间隙一维切片
    i1 = torch.arange(0, a.shape[0], 2)
    i2 = torch.arange(0, a.size(1), 2)
    # fslice1 = fslice(start=0, stop=a.shape[0], step=2)
    print(a[i1, :][:, i2])  # 间隙一维切片

    x = torch.rand(1, 1, 9, 9)
    # print(s)
    patch_top_left = x[..., ::2, ::2]
    patch_top_right = x[..., ::2, 1::2]
    patch_bot_left = x[..., 1::2, ::2]
    patch_bot_right = x[..., 1::2, 1::2]
    print(patch_top_left, patch_top_right, patch_bot_left, patch_bot_right)

    j02_2 = torch.arange(0, x.shape[2], 2)
    j12_2 = torch.arange(1, x.shape[2], 2)
    j02_3 = torch.arange(0, x.shape[3], 2)
    j12_3 = torch.arange(1, x.shape[3], 2)
    patch_top_left = x[..., j02_2, :][..., j02_3]
    patch_top_right = x[..., j02_2, :][..., j12_3]
    patch_bot_left = x[..., j12_2, :][..., j02_3]
    patch_bot_right = x[..., j12_2, :][..., j12_3]
    print(patch_top_left, patch_top_right, patch_bot_left, patch_bot_right)


if __name__ == '__main__':
    # src = torch.zeros((2, 6), dtype=torch.float)
    # res = t_scatter(src)

    # index = torch.tensor([0, 1, 0, 0])
    # print(torch.index_select(res, 1, index))

    # t_index_fill()

    # 查找 val 在数值中的索引
    # ind_max_src = np.unravel_index(ind_max, A.shape)

    pass
