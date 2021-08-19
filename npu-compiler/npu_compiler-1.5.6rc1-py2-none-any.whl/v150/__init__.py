#coding: utf-8
import os

import tensorflow as tf
from tensorflow.python.framework import graph_util
from tensorflow.python.framework import ops

from npu_compiler.v150.config import Config
from npu_compiler.v150.compiler import run

from . import __file__

def compile_model(config_file):
    Config.parse_config(config_file, {"QUIET":True})
    Config.parse_para()
    Config.check_config()
    run()

def update_npu_model(sess, output_nodes, pb_path, config_path):
    constant_graph = graph_util.convert_variables_to_constants(sess, sess.graph_def, output_nodes)
    with tf.gfile.FastGFile(pb_path, mode='wb') as f:
        f.write(constant_graph.SerializeToString())
    compile_model(config_path)

def npu_inference(placeholders, tf_outputs, infer_batch=False, name=None):
    lib_path = os.path.join(os.path.dirname(__file__), "C/gxnpuop.so")
    gxnpuop = tf.load_op_library(lib_path)
    return gxnpuop.npu_inference(placeholders, tf_outputs, infer_batch, name)

@ops.RegisterGradient("NPUInference")
def _NPUInferenceGrad(op, *grads): # grads为npu的输出，支持不定输出
    placeholder_grads = [None] * op.get_attr("inputs_num") # 第1个输入为tf的输入，不做传递
    tf_grads = list(*grads) # 第2个输入为tf的输出，grad直接传递
    return placeholder_grads + tf_grads

