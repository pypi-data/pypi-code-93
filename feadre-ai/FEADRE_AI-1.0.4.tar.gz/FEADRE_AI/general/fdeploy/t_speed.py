import os
import random

import onnxruntime
import torch
from torchvision import models
import numpy as np

from ftools.ai.fits.fweight import load_weight
from ftools.f_general import fshow_time

torch.set_printoptions(linewidth=320, sci_mode=False, precision=5, profile='long')
np.set_printoptions(linewidth=320, suppress=True, precision=5, formatter={'float_kind': '{:11.5g}'.format})
seed = 0
np.random.seed(seed)
random.seed(seed)
torch.manual_seed(seed)


def show_reses(reses):
    for res in reses:
        print(res.reshape(batch, -1)[:, :num_end], '\n')
    print(str('-------------------------------------------------------------' + '\n'))


def f_script(trace_script, input_t):
    reses = trace_script(input_t)
    show_reses(reses)


def f_y(model, input_t):
    reses = model(input_t)
    show_reses(reses)


def f_onnx(onnx_session, input_dict, output_names_list):
    reses = onnx_session.run(
        output_names=output_names_list,
        input_feed=input_dict)
    show_reses(reses)


class CFG:
    pass


if __name__ == '__main__':
    batch = 5
    num_end = 5
    num_time = 1
    path_save_root = '../../../_temp/file'

    cfg = CFG()
    cfg.IS_TEST = True
    cfg.IS_VAL = False
    cfg.NUM_CLASSES = 80  # ***
    cfg.device = torch.device('cpu')
    cfg.save_weight_name = ''
    cfg.PRED_CONF_THR = 0.35  # 这些参数无数只用于创建
    cfg.PRED_NMS_THR = 0.6  # 这些参数无数只用于创建
    path_host = 'M:'
    cfg.PATH_SAVE_WEIGHT = os.path.join(path_host, r'/AI/weights/feadre')

    ''' --------------------- yolo1 ----------------------
        能够正常转换  
        script 报错 return self._forward_impl(x) '''
    # from yolov1.net.fcre_model import finit_model  # 这个成功
    # file_onnx = 'yolo1.onnx'
    # output_names = ['output0', 'output1', 'output2']

    ''' --------------------- nanodet ----------------------
        全不行 
    '''
    # from nanodet.net.fcre_model import finit_model

    # file_onnx = 'nanodet.onnx'
    # output_names = ['output0', 'output1']

    ''' --------------------- yolox ----------------------
        trace_trace可以转换  
        script: 报错 x = self.stems[k](x)
        onnx: RuntimeError: step!=1 is currently not supported  不支持二维切片
    '''
    from yolox.net.fcre_model import finit_model

    file_onnx = 'yolox.onnx'
    file_script = 'yolox.pt'
    _file_read_weight = os.path.join(cfg.PATH_SAVE_WEIGHT, 'zz/yolox_coco_nano' + '.pth')
    output_names = ['output0', 'output1', 'output2']

    ''' -------------------------------------------------------------- '''
    input_t = torch.rand((batch, 3, 320, 320))
    input_cre_model = torch.rand((1, 3, 320, 320))

    model_z = finit_model(cfg)
    load_weight(file_weight=_file_read_weight, model=model_z,
                optimizer=None, lr_scheduler=None,
                device=cfg.device, ffun=None)
    model_z.eval()
    model = model_z.net

    fshow_time(f_y, arg_list=[model, input_t], num_time=num_time)

    ''' ------------ script ------------ '''
    file_script = os.path.join(path_save_root, file_script)

    # trace_script = torch.jit.script(model, input_trace)
    trace_trace = torch.jit.trace(model, input_cre_model)

    trace_trace.save(file_script)
    trace_trace = torch.jit.load(file_script)
    fshow_time(f_script, arg_list=[trace_trace, input_t], num_time=num_time)

    ''' ------------ onnx ------------ '''
    input_names = ['input0', ]

    dynamic_axes = {
        input_names[0]: {0: 'batch_size', 1: 'channel', 2: "height", 3: 'width'},  # 支持部份动态
    }

    file_onnx = os.path.join(path_save_root, file_onnx)
    torch.onnx.export(model, input_cre_model,
                      f=file_onnx,
                      verbose=False,
                      input_names=input_names,
                      output_names=output_names,
                      dynamic_axes=dynamic_axes,
                      opset_version=11,
                      )
    onnx_session = onnxruntime.InferenceSession(file_onnx)
    output_name1 = onnx_session.get_outputs()[0].name
    input_name1 = onnx_session.get_inputs()[0].name

    # res_onnx = onnx_session.run(
    #     output_names=[output_name1],
    #     input_feed={input_name1: input_t.numpy()})
    # print(res_onnx)

    arg_list = [onnx_session, {input_name1: input_t.numpy()}, output_names]
    fshow_time(f_onnx, arg_list=arg_list, num_time=num_time)
