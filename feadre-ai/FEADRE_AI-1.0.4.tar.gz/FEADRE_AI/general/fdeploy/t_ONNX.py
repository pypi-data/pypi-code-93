import random

import onnx
import onnxruntime
import torch
from torch import nn
import numpy as np
from torchvision import models


def fcre_onnx(model, data_ts, file_onnx, verbose=False,
              input_names=('input'),  # 单输入
              output_names=('output'),
              dynamic_axes=None,
              ):
    '''
    # 选择用那种ops.有三种选择：
    # 1. OperatorExportTypes.ONNX（默认），导出为标准ONNX运算符
    # 2. OperatorExportTypes.ONNX_ATEN， 导出为aten运算符
    # 3. OperatorExportTypes.ONNX_ATEN_FALLBACK， 在ONNX中注册的运算符使用ONNX,其余使用aten
    :param model:
    :param data_ts:
    :param file_onnx:
    :param verbose:
    :param input_names:
    :param output_names:
    :param dynamic_axes:
    :return:
    '''
    torch.onnx.export(model,
                      data_ts,
                      file_onnx,
                      export_params=True,  # 是否保存模型的训练好的参数
                      verbose=False,  # 是否输出debug描述
                      input_names=['input1', 'input2'],  # 定义输入结点的名字，有几个输入就定义几个
                      output_names=['output'],  # 定义输出结点的名字
                      opset_version=11,  # onnx opset的库版本
                      do_constant_folding=True,  # whether do constant-folding optimization 该优化会替换全为常数输入的分支为最终结果
                      operator_export_type=torch.onnx.OperatorExportTypes.ONNX_ATEN_FALLBACK)
    torch.onnx.export(model, data_ts, file_onnx, verbose=verbose,
                      input_names=input_names,
                      output_names=output_names,
                      dynamic_axes=dynamic_axes,
                      )


class TModel(nn.Module):

    def __init__(self):
        super().__init__()

    def forward(self, inputs):
        # export 自动 eval
        x, y = list(inputs.values())
        # (batch, 3, 320, 320)
        x1 = x + 1
        x2 = x - 1
        y = y + 1

        if self.training:
            print('训练模式')
            x1 = x2 * x1
        else:
            print('验证模式')
            x1 = x2 + x1

        # 分支判断
        if torch.onnx.is_in_onnx_export():
            print('开始onnx')

        # 切断tracing
        # if torch.onnx.isinonnxexport():
        #     # cast countmat to constant while exporting to ONNX
        #     countmat = torch.fromnumpy(
        #         countmat.cpu().detach().numpy()).to(device=img.device)

        ''' --------- 不支持 --------- '''
        # x = x[x > 0.5] # 不支持
        # x[0] = 1 # 不支持
        # x = torch.index_fill(x, -1, torch.arange(3), 1)  # 不支持
        # 不支持adaptiveAvgPool2d, Expand, ReLU6

        ''' --------- 支持 --------- '''
        # 支持float32 及 int
        # val_det = torch.tensor([1, 2], dtype=torch.float).view(1, 1, 1, 2)
        # index = torch.zeros_like(val_det, dtype=torch.long)
        # x = x.scatter(0, index, val_det)

        # x = x.max(-1)[0]
        # x = x.topk(3, dim=-1)[0]

        # return x1
        x2 = x1[:, :2, :, :] * y[0, 1]  # 支持
        return x1, x2
        # return x1, x2


if __name__ == '__main__':
    torch.set_printoptions(linewidth=320, sci_mode=False, precision=5, profile='long')
    np.set_printoptions(linewidth=320, suppress=True, precision=5, formatter={'float_kind': '{:11.5g}'.format})
    seed = 0
    # 随机种子
    np.random.seed(seed)
    random.seed(seed)
    # from yolo5 Speed-reproducibility tradeoff https://pytorch.org/docs/stable/notes/randomness.html
    torch.manual_seed(seed)

    file_onnx = 't_model.onnx'
    size_wh_input = (320, 320)

    model = TModel()
    # model = models.resnet18(pretrained=False)
    # model.eval()
    model.train()
    input_names = ['input0', 'input1']
    output_names = ['output0', 'output1']

    batch = 1
    num_end = 5
    # data_ts = torch.rand((batch, 3, *size_wh_input), dtype=torch.float)
    data_ts = torch.rand((1, 3, 230, 230), dtype=torch.float)
    # data_ts = [data_ts, torch.tensor([1, 2, 3])]
    data_dict = {input_names[0]: data_ts,
                 input_names[1]: torch.tensor([[1, 2, 3]])
                 }
    # data_np = data_ts.numpy()
    # data_np = np.random.uniform(0., 1, (1, 3, *size_wh_input), ).astype(np.float32)

    reses = model(data_dict)
    for res in reses:
        print(res.reshape(batch, -1)[:, :num_end])

    # 单输入
    # dynamic_axes = None
    dynamic_axes = {
        input_names[0]: {0: 'batch_size', 1: 'channel', 2: "height", 3: 'width'},  # 支持部份动态
        input_names[1]: {0: 'batch_size', 1: 'channel', 2: "height", 3: 'width'},  # 支持部份动态
    }

    # 多输出
    # dynamic_axes = {
    #     'input': {0: 'batch_size', 1: 'channel', 2: "height", 3: 'width'},
    #     'output0': {0: 'batch_size', 1: 'feature_maps'},
    #     'output1': {0: 'batch_size', 1: 'feature_maps'},
    #     'output2': {0: 'batch_size', 1: 'feature_maps'}
    # }

    torch.onnx.export(model, data_dict, file_onnx, verbose=False,
                      input_names=input_names,
                      output_names=output_names,
                      dynamic_axes=dynamic_axes,
                      )

    ''' --------------- 验证 ----------- '''
    # model = onnx.load(file_onnx)
    # 基本无用 Check that the IR is well formed
    # onnx.checker.check_model(model)
    # Print a human readable representation of the graph
    # print(onnx.helper.printable_graph(model.graph))

    onnx_session = onnxruntime.InferenceSession(file_onnx)
    output_name1 = onnx_session.get_outputs()[0].name
    output_name2 = onnx_session.get_outputs()[1].name
    input_name1 = onnx_session.get_inputs()[0].name
    input_name2 = onnx_session.get_inputs()[1].name

    print('开始')
    # 输出是list
    res_onnx = onnx_session.run(
        output_names=[output_name1, output_name2],
        input_feed={input_name1: data_ts.numpy(), input_name2: np.array([[1, 2, 3]], dtype=np.int64)})

    for res in res_onnx:
        print(res.reshape(batch, -1)[:, :num_end])
    print('debug')
    pass
