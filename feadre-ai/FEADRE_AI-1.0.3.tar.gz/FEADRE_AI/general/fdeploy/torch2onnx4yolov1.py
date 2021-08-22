import onnxruntime
import torch
from torchvision import models

from ftools.ai.fmodels.f_layer_get import ModelOut4Resnet18
from yolov1.net.net_yolov1 import YOLOv1_NetOD


def ffun_onnx(pretrained_dict_y):
    dd = {}
    for k, v in pretrained_dict_y.items():
        dd[k.replace('net.', '')] = v
    return dd


if __name__ == '__main__':
    import os

    from ftools.ai.CONFIG_BASE import FCFG_BASE
    from ftools.ai.fits.fweight import load_weight

    cfg = FCFG_BASE()
    cfg.device = torch.device('cpu')
    cfg.SIZE_WH_INPUT_TRAIN  = (320, 320)

    cfg.NUM_CLASSES = 3
    cfg.STRIDE = 32

    backbone = models.resnet18(pretrained=True)
    backbone = ModelOut4Resnet18(backbone)
    model = YOLOv1_NetOD(backbone, cfg)

    _file_read_weight = None  # 无yolo1文件
    # path_root_weight = r'M:\AI\weights\feadre\zz'
    # _file_read_weight = os.path.join(path_root_weight, 'nanodet_shuffle2_type3_38_12.03_p75.7_r63.4' + '.pth')

    start_epoch = load_weight(file_weight=_file_read_weight, model=model,
                              optimizer=None, lr_scheduler=None,
                              device=cfg.device, ffun=ffun_onnx)

    batch = 1
    num_end = 10
    data_ts = torch.rand((batch, 3, *cfg.SIZE_WH_INPUT_TRAIN ), dtype=torch.float)
    reses = model(data_ts)

    for res in reses:
        print(res.reshape(batch, -1)[:, :num_end])

    # 验证
    file_onnx = 'yolov1.onnx'
    input_names = ['input']
    output_names = ['out_cls', 'out_conf_box']

    torch.onnx.export(model, data_ts, file_onnx, verbose=False,
                      input_names=input_names,
                      output_names=output_names,
                      dynamic_axes=None,
                      opset_version=11,
                      )

    onnx_session = onnxruntime.InferenceSession(file_onnx)
    res_onnx = onnx_session.run(
        output_names=output_names,
        input_feed={input_names[0]: data_ts.numpy()})

    for res in res_onnx:
        print(res.reshape(batch, -1)[:, :num_end])
    print('debug')
