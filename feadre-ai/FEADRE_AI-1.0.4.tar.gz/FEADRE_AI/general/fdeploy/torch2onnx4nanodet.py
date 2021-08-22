import onnxruntime
import torch


def ffun_onnx(pretrained_dict_y):
    dd = {}
    for k, v in pretrained_dict_y.items():
        dd[k.replace('net.', '')] = v
    return dd


if __name__ == '__main__':
    import os

    from ftools.ai.CONFIG_BASE import FCFG_BASE
    from ftools.ai.fits.fweight import load_weight
    from nanodet.net.net_nanodet import NetNanodet
    from nanodet.net.shufflenetv2 import ShuffleNetV2

    cfg = FCFG_BASE()
    cfg.NUM_CLASSES = 3
    cfg.anc_scale = 5  # 这个是anc大小,关系到regmax的设置, 这个值越大匹配的anc与真实的GT的距离(最大和最小值)越大  octave_base_scale
    cfg.reg_max = 7  # 特图差距最大值7 分成8份
    cfg.device = torch.device('cpu')
    cfg.SIZE_WH_INPUT_TRAIN  = (320, 320)

    backbone = ShuffleNetV2(model_size='1.0x', )
    backbone.dims_out = (116, 232, 464)
    model = NetNanodet(backbone, num_class=3, reg_max=7)

    path_root_weight = r'M:\AI\weights\feadre\zz'
    _file_read_weight = os.path.join(path_root_weight, 'nanodet_type3_44_11.89_p75.6_r62.7' + '.pth')

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
    output_names = ['pcls', 'pt_ltrb']

    torch.onnx.export(model, data_ts, file_onnx, verbose=True,
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
