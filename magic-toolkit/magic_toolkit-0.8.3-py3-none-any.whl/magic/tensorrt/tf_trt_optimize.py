import tensorflow as tf
from tensorflow.python.compiler.tensorrt import trt_convert as trt
    
def tftrt_optimize(protobuf,
                   max_batch_size,
                   nodes_blacklist,
                   fp16=0,
                   minimum_segment_size=3):
    """
    tf-trt for acceleration
    :param protobuf: path of pb.
    :param max_batch_size: max size for the input batch.
    :param nodes_blacklist:  list of node names to prevent the converter from touching.
    :param precision_mode: one of TrtPrecisionMode.supported_precision_modes().
    :param minimum_segment_size: the minimum number of nodes required for a subgraph
     to be replaced by TRTEngineOp.
    :return:
    """

    with tf.Session() as sess:
        # First deserialize your frozen graph:
        with tf.gfile.GFile(protobuf, 'rb') as f:
            frozen_graph = tf.GraphDef()
            frozen_graph.ParseFromString(f.read())
        # Now you can create a TensorRT inference graph from your frozen graph:

        precision_mode = trt.TrtPrecisionMode.FP32
        if fp16:
            precision_mode = trt.TrtPrecisionMode.FP16
        # if int8:
        #     precision_mode = trt.TrtPrecisionMode.INT8

        converter = trt.TrtGraphConverter(
            input_graph_def=frozen_graph,
            nodes_blacklist=nodes_blacklist,
            max_batch_size=max_batch_size,
            precision_mode=precision_mode,
            minimum_segment_size=minimum_segment_size)
        trt_graph = converter.convert()

        # Import the TensorRT graph into a new graph(sess.graph) and run:

        tf.import_graph_def(graph_def=trt_graph, name="")

        tf.io.write_graph(trt_graph, "./", "trt_" + protobuf, as_text=False)
