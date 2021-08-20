import tensorrt as trt
# import pycuda.driver as cuda
# import pycuda.autoinit

def uff_convert(uff_model,
                trt_path,
                uff_inputs=dict(),
                uff_outputs=list(),
                uff_format="NHWC",
                max_batch_size=1,
                fp16=0,
                int8=0,
                calibrator=None,
                verbose=0,
                network_ext_fn=None):
    """
    uff -> trt, support fp32, fp16, int8.
    :param uff_model: uff buffer already live in memory, or path of model
    :param trt_path: for save engine
    :param uff_inputs: dict, not batch, eg. uff_inputs = {"input_0' : [120, 120, 3]}
    :param uff_outputs: list of str, eg. uff_outputs = ["sigmoid_0", "output_0"]
    :param uff_format: NHWC, NCHW, NC
    :param max_batch_size: fixed batch not dynamic batch
    :param fp16: turn on fp16
    :param int8: turn on int8
    :param calibrator: int8 calibrator
    :param verbose: whether to print tensorrt log of processing.
    :param network_ext_fn: extend network by tensorrt api
    """

    # get tensorrt version
    trt_version = trt.__version__
    # cuda_version = cuda.get_version()
    print("tensorrt version:", trt_version)
    # print("cuda version:", cuda_version)

    # instantiate Logger
    severity = trt.Logger.VERBOSE if verbose else trt.Logger.WARNING
    TRT_LOGGER = trt.Logger(severity)

    # builder properties
    builder = trt.Builder(TRT_LOGGER)
    builder.max_workspace_size = 1 << 30  # 1GB
    builder.max_batch_size = max_batch_size

    if fp16:
        if builder.platform_has_fast_fp16:
            builder.fp16_mode = True
        else:
            raise RuntimeError("不支持fp16")

    if int8:
        if builder.platform_has_fast_int8:
            builder.int8_mode = True
            builder.int8_calibrator = calibrator
        else:
            raise RuntimeError("不支持int8")

    # create network
    network = builder.create_network()

    parser = trt.UffParser()
    uff_order = {"NHWC": trt.UffInputOrder.NHWC,
                 "NCHW": trt.UffInputOrder.NCHW,
                 "NC": trt.UffInputOrder.NC}

    for name, shape in uff_inputs.items():
        parser.register_input(name, shape, order=uff_order[uff_format])
    for name in uff_outputs:
        parser.register_output(name)

    if isinstance(uff_model, str):
        success = parser.parse(uff_model, network)
    else:
        success = parser.parse_buffer(uff_model, network)
    if not success: raise RuntimeError("模型解析失败")

    if network_ext_fn:
        network_ext_fn(network)

    # for i in range(network.num_layers):
    #     layer = network.get_layer(i)
    #     print(layer.name, '-- ', layer.get_output(0).shape)

    # print('display network output ', '#' * 50)
    # for i in range(network.num_outputs):
    #     ret = network.get_output(i)
    #     print(ret.name, '---', ret.shape)

    print('Building, this may take a while...')

    engine = builder.build_cuda_engine(network)
    with open(trt_path, "wb") as f:
        f.write(engine.serialize())
        print('Saved engin in {}'.format(trt_path))

    print("engine.max_batch_size={}".format(engine.max_batch_size))
    for i in range(engine.num_bindings):
        binding_type = "input_node:" if engine.binding_is_input(i) else "output_node:"
        binding_name = engine.get_binding_name(i)
        binding_shape = engine.get_binding_shape(i)
        print(binding_type, binding_name, binding_shape)
