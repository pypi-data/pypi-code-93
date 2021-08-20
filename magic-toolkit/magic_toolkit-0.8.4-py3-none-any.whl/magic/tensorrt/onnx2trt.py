import tensorrt as trt

def onnx_convert(onnx_path,
                 trt_path,
                 max_batch_size=0,
                 fp16=0,
                 int8=0,
                 calibrator=None,
                 verbose=0):
    """
    onnx -> trt
    support fp32, fp16, int8
    :param onnx_path: onnx model path
    :param trt_path: for save engine
    :param max_batch_size: fixed batch not dynamic batch
    :param fp16: turn on fp16
    :param int8: turn on int8
    :param calibrator: int8 calibrator
    :param verbose: whether to print tensorrt log of processing.
    """

    # get tensorrt version
    trt_version = trt.__version__
    print("tensorrt version:", trt_version)

    # instantiate Logger
    severity = trt.Logger.VERBOSE if verbose else trt.Logger.WARNING
    TRT_LOGGER = trt.Logger(severity)

    EXPLICIT_BATCH = 1 << (int)(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
    with trt.Builder(TRT_LOGGER) as builder, \
            builder.create_network(EXPLICIT_BATCH) as network, \
            trt.OnnxParser(network, TRT_LOGGER) as parser:

        with open(onnx_path, 'rb') as model:
            if not parser.parse(model.read()):
                for error in range(parser.num_errors):
                    print(parser.get_error(error))

        # configurate builder
        builder.max_workspace_size = 2 << 30  # 2G
        if max_batch_size < 1:
            max_batch_size = network.get_input(0).shape[0]
        builder.max_batch_size = max_batch_size

        if fp16:
            if builder.platform_has_fast_fp16:
                builder.fp16_mode = True
            else:
                print("不支持fp16")

        if int8:
            if builder.platform_has_fast_int8:
                builder.int8_mode = True
                builder.int8_calibrator = calibrator
            else:
                print("不支持int8")

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
